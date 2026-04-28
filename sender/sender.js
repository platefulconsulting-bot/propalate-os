// PFC WhatsApp sender — polls Supabase for due leads and sends via whatsapp-web.js.
// Run: `npm install && node sender.js`. First run prints a QR — scan with the
// outreach phone (Settings → Linked Devices → Link a Device) and stay logged in.

require('dotenv').config();

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const SB_URL = required('SB_URL');
const SB_KEY = required('SB_KEY');
const POLL_SEC = num('POLL_SEC', 60);
const RATE_LIMIT_MS = Math.max(num('RATE_LIMIT_MS', 120000), 60000); // default 2 min, hard floor 1 min
const DAILY_CAP = num('DAILY_CAP', 200);
const DRY_RUN = process.env.DRY_RUN === '1';

function required(k) { const v = process.env[k]; if (!v) { console.error(`Missing env ${k}`); process.exit(1); } return v; }
function num(k, d) { const v = Number(process.env[k]); return Number.isFinite(v) && v > 0 ? v : d; }
function ts() { return new Date().toLocaleTimeString('en-IN'); }
const log = (...a) => console.log(`[${ts()}]`, ...a);

// ── Daily-cap tracking, persisted across restarts ──────────────────
const CAP_FILE = path.join(__dirname, '.daily-count.json');
function readCap() {
  try {
    const j = JSON.parse(fs.readFileSync(CAP_FILE, 'utf8'));
    if (j.date === todayKey()) return j.count;
  } catch (e) {}
  return 0;
}
function writeCap(count) {
  fs.writeFileSync(CAP_FILE, JSON.stringify({ date: todayKey(), count }));
}
function todayKey() { return new Date().toISOString().slice(0, 10); }
let dailyCount = readCap();

// ── Supabase REST helper ───────────────────────────────────────────
async function sb(p, opts = {}) {
  const r = await fetch(`${SB_URL}/rest/v1/${p}`, {
    ...opts,
    headers: {
      'apikey': SB_KEY,
      'Authorization': `Bearer ${SB_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': opts.method === 'POST' ? 'return=representation' : (opts.method === 'PATCH' ? 'return=minimal' : ''),
      ...(opts.headers || {})
    }
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  const t = await r.text();
  return t ? JSON.parse(t) : null;
}

// ── Template renderer: replaces {{var}} with lead fields. ──────────
function render(tpl, lead) {
  const fallback = { name: 'there', restaurant_name: 'your restaurant', city: 'your city', swiggy_rating: 'your rating', zomato_rating: 'your rating' };
  return String(tpl || '').replace(/\{\{\s*(\w+)\s*\}\}/g, (_, k) => {
    const v = lead[k];
    if (v == null || v === '' || v === 'null') return fallback[k] || '';
    return String(v);
  });
}

// ── WhatsApp client ────────────────────────────────────────────────
const client = new Client({
  authStrategy: new LocalAuth({ dataPath: path.join(__dirname, 'wa-session') }),
  puppeteer: { args: ['--no-sandbox', '--disable-setuid-sandbox'] },
});

let ready = false;

client.on('qr', qr => {
  console.log('\nScan this QR with the outreach phone — Settings → Linked Devices → Link a Device:\n');
  qrcode.generate(qr, { small: true });
});
client.on('authenticated', () => log('Authenticated. Session cached for next run.'));
client.on('ready', () => { ready = true; log('WhatsApp client ready. Polling every', POLL_SEC, 'seconds.'); pollLoop(); });
client.on('disconnected', r => { console.error('Disconnected:', r); process.exit(1); });
client.on('auth_failure', m => { console.error('Auth failure:', m); process.exit(1); });

// ── Send one lead ──────────────────────────────────────────────────
async function sendOne(lead, step) {
  const digits = String(lead.phone || '').replace(/[^\d]/g, '');
  if (!digits) return { status: 'failed', error: 'No phone' };
  const chatId = digits + '@c.us';
  const body = render(step.template, lead);

  if (DRY_RUN) {
    log(`[DRY-RUN] ${lead.name} (${lead.phone}) → ${body.slice(0, 80)}…`);
    return { status: 'sent', body };
  }

  let isReg;
  try { isReg = await client.isRegisteredUser(chatId); }
  catch (e) { return { status: 'failed', error: 'isRegistered check failed: ' + e.message, body }; }
  if (!isReg) return { status: 'failed', error: 'Number not on WhatsApp', body };

  await client.sendMessage(chatId, body);
  return { status: 'sent', body };
}

// ── Process a single lead end-to-end ───────────────────────────────
async function processLead(lead, sequencesById) {
  const seq = sequencesById[lead.sequence_id];
  if (!seq) { log('skip — no sequence found for', lead.id); return; }

  const stepNum = (lead.sequence_step || 0) + 1;
  if (stepNum > seq.total_steps) {
    await sb(`leads?id=eq.${lead.id}`, { method: 'PATCH', body: JSON.stringify({ next_send_at: null }) });
    return;
  }

  const steps = await sb(`sequence_steps?sequence_id=eq.${lead.sequence_id}&step_number=eq.${stepNum}&limit=1`);
  const step = steps?.[0];
  if (!step) { log('skip — no step', stepNum, 'in seq', lead.sequence_id); return; }

  let result;
  try { result = await sendOne(lead, step); }
  catch (e) { result = { status: 'failed', error: e.message, body: render(step.template, lead) }; }

  // Always log — sent or failed.
  await sb('send_log', {
    method: 'POST',
    body: JSON.stringify({
      lead_id: lead.id,
      sequence_id: lead.sequence_id,
      step_number: stepNum,
      channel: 'whatsapp',
      status: result.status,
      message_body: result.body,
      error_msg: result.error || null,
      sent_at: new Date().toISOString(),
    })
  }).catch(e => console.error('send_log insert failed:', e.message));

  if (result.status !== 'sent') {
    log(`✗ ${lead.name}: ${result.error}`);
    return;
  }

  // Compute next_send_at from the next step's delay_hours.
  let nextSendAt = null;
  if (stepNum < seq.total_steps) {
    const nextSteps = await sb(`sequence_steps?sequence_id=eq.${lead.sequence_id}&step_number=eq.${stepNum + 1}&limit=1`);
    const delayH = nextSteps?.[0]?.delay_hours ?? 24;
    nextSendAt = new Date(Date.now() + delayH * 3600 * 1000).toISOString();
  }

  const updates = {
    sequence_step: stepNum,
    total_msgs_sent: (lead.total_msgs_sent || 0) + 1,
    last_msg_sent_at: new Date().toISOString(),
    next_send_at: nextSendAt,
    stage: lead.stage === 'queued' ? 'contacted' : lead.stage,
  };
  try {
    await sb(`leads?id=eq.${lead.id}`, { method: 'PATCH', body: JSON.stringify(updates) });
  } catch (e) {
    console.error(`✗ FAILED TO ADVANCE lead ${lead.id} (${lead.name}) — pausing it to prevent re-send. Error:`, e.message);
    try { await sb(`leads?id=eq.${lead.id}`, { method: 'PATCH', body: JSON.stringify({ paused: true }) }); } catch (_) {}
    return;
  }

  dailyCount += 1;
  writeCap(dailyCount);

  log(`✓ ${lead.name} step ${stepNum}/${seq.total_steps} (${dailyCount}/${DAILY_CAP} today)`);
}

// ── Poll loop ──────────────────────────────────────────────────────
async function pollLoop() {
  // Reset daily cap if date rolled over.
  if (readCap() === 0 && dailyCount > 0) dailyCount = 0;

  try {
    if (dailyCount >= DAILY_CAP) {
      log(`daily cap reached (${dailyCount}/${DAILY_CAP}) — sleeping`);
    } else {
      const sequences = await sb('sequences?select=*');
      const sequencesById = Object.fromEntries((sequences || []).map(s => [s.id, s]));

      const url = `leads?sequence_id=not.is.null&paused=eq.false&next_send_at=lte.${encodeURIComponent(new Date().toISOString())}&stage=in.(new,queued,contacted)&order=next_send_at.asc&limit=50`;
      const due = await sb(url);

      const room = DAILY_CAP - dailyCount;
      const batch = (due || []).slice(0, room);

      if (!batch.length) log('no leads due');
      else log(`processing ${batch.length} due lead(s)`);

      for (const lead of batch) {
        if (!ready) break;
        if (dailyCount >= DAILY_CAP) { log('daily cap reached mid-batch'); break; }
        await processLead(lead, sequencesById);
        await sleep(RATE_LIMIT_MS);
      }
    }
  } catch (e) {
    console.error('Poll error:', e.message);
  }
  setTimeout(pollLoop, POLL_SEC * 1000);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Graceful shutdown ──────────────────────────────────────────────
process.on('SIGINT', async () => { log('Shutting down…'); try { await client.destroy(); } catch (e) {} process.exit(0); });

console.log('PFC WhatsApp sender starting…');
console.log(DRY_RUN ? '⚠ DRY-RUN mode — no messages will actually be sent.' : '');
client.initialize();
