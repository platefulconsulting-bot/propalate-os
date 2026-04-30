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
  puppeteer: {
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    protocolTimeout: 300000, // 5 min — guards against slow inject on session restore
  },
});

let ready = false;

client.on('qr', qr => {
  console.log('\nScan this QR with the outreach phone — Settings → Linked Devices → Link a Device:\n');
  qrcode.generate(qr, { small: true });
});
client.on('authenticated', () => log('Authenticated. Session cached for next run.'));
client.on('ready', () => { ready = true; log('WhatsApp client ready. Polling every', POLL_SEC, 'seconds. Listening for inbound replies.'); pollLoop(); });
client.on('disconnected', r => { console.error('Disconnected:', r); process.exit(1); });
client.on('auth_failure', m => { console.error('Auth failure:', m); process.exit(1); });

// ── Recent-send dedup so worker-originated messages don't get double-logged
//    when the message_create event fires for them.
const recentlySent = new Set();
function recentKey(chatId, body) { return chatId + '|' + String(body || '').slice(0, 200); }
function markRecentSend(chatId, body) {
  const key = recentKey(chatId, body);
  recentlySent.add(key);
  setTimeout(() => recentlySent.delete(key), 30000);
}

// ── Two listeners with complementary coverage:
//    'message' fires reliably for INBOUND only — primary path for replies.
//    'message_create' fires for OUTBOUND from any linked device (phone, WA Web)
//      — used to capture manual sends. Worker's own sends are excluded via recentlySent.
//    A processedIds set protects against the rare case where both events fire for
//    the same physical message.
const processedIds = new Set();
function alreadyProcessed(msg) {
  const id = (msg.id && (msg.id._serialized || msg.id.id)) || (msg.from + '|' + msg.timestamp + '|' + (msg.body || '').slice(0, 50));
  if (processedIds.has(id)) return true;
  processedIds.add(id);
  setTimeout(() => processedIds.delete(id), 60000);
  return false;
}

// Resolve a chatId to an E.164 phone. Handles @c.us (direct) and @lid (newer
// privacy-preserving format) by digging into contact.id._serialized which still
// carries the underlying phone-based @c.us identity. contact.number is unreliable
// for @lid contacts (it returns the LID digit string, not the actual phone).
async function resolvePhone(msg, chatId) {
  if (chatId && chatId.endsWith('@c.us')) return '+' + chatId.replace('@c.us', '');
  try {
    const contact = await msg.getContact();
    const sid = (contact && contact.id && contact.id._serialized) || '';
    if (sid.endsWith('@c.us')) return '+' + sid.replace('@c.us', '');
    if (contact && contact.id && contact.id.user && /^\d{10,15}$/.test(contact.id.user)) {
      return '+' + contact.id.user;
    }
    if (contact && contact.number && /^\d{10,15}$/.test(String(contact.number))) {
      return '+' + contact.number;
    }
  } catch (e) { console.warn('getContact failed:', e.message); }
  return null;
}

client.on('message', async msg => {
  try {
    if (msg.fromMe) return;
    // Skip group / status / broadcast (chatId @g.us / status@broadcast).
    if (!msg.from || msg.from.endsWith('@g.us') || msg.from.includes('status@broadcast')) return;
    if (alreadyProcessed(msg)) return;
    await handleInbound(msg);
  } catch (e) {
    console.error('inbound (message) handler error:', e.message);
  }
});

client.on('message_create', async msg => {
  try {
    if (!msg.fromMe) return; // inbound goes through 'message'
    if (!msg.to || msg.to.endsWith('@g.us') || msg.to.includes('status@broadcast')) return;
    if (recentlySent.has(recentKey(msg.to, msg.body))) return;
    if (alreadyProcessed(msg)) return;
    await handleOutboundManual(msg);
  } catch (e) {
    console.error('outbound (message_create) handler error:', e.message);
  }
});

async function handleOutboundManual(msg) {
  const phone = await resolvePhone(msg, msg.to);
  if (!phone) { log(`📤 manual outbound: could not resolve recipient phone (chatId=${msg.to})`); return; }
  const body = msg.body || '';
  const ts = msg.timestamp ? new Date(msg.timestamp * 1000).toISOString() : new Date().toISOString();

  const found = await sb(`leads?phone=eq.${encodeURIComponent(phone)}&limit=1`);
  if (!found?.length) {
    log(`📤 manual outbound to unknown ${phone}: "${body.slice(0, 60)}"`);
    return;
  }
  const lead = found[0];

  sb('send_log', {
    method: 'POST',
    body: JSON.stringify({
      lead_id: lead.id,
      channel: 'whatsapp',
      status: 'sent',
      message_body: body,
      sent_at: ts,
    })
  }).catch(e => console.warn('manual outbound send_log insert failed:', e.message));

  const updates = {
    total_msgs_sent: (lead.total_msgs_sent || 0) + 1,
    last_msg_sent_at: ts,
    paused: true,
    next_send_at: null,
  };
  if (['new', 'queued'].includes(lead.stage)) updates.stage = 'contacted';

  await sb(`leads?id=eq.${lead.id}`, { method: 'PATCH', body: JSON.stringify(updates) })
    .catch(e => console.warn('manual outbound lead patch failed:', e.message));

  log(`📤 ${lead.name} (${phone}) — manual: "${body.slice(0, 80)}"`);
}

async function handleInbound(msg) {
  // DEBUG: dump every identifier we can find so we can pick the right one for @lid contacts.
  try {
    const c = await msg.getContact().catch(() => null);
    const chat = await msg.getChat().catch(() => null);
    log('🐛 inbound deep-debug:', JSON.stringify({
      msg_from: msg.from, msg_to: msg.to, msg_author: msg.author,
      msg_id: msg.id && (msg.id._serialized || msg.id.id),
      contact_number: c && c.number,
      contact_id: c && c.id && (c.id._serialized || c.id.user || c.id),
      contact_pushname: c && c.pushname,
      contact_name: c && c.name,
      contact_isUser: c && c.isUser,
      chat_id: chat && chat.id && (chat.id._serialized || chat.id.user),
      chat_name: chat && chat.name,
    }));
  } catch (e) { log('🐛 inbound deep-debug failed:', e.message); }

  const phone = await resolvePhone(msg, msg.from);
  if (!phone) { log(`📥 inbound: could not resolve sender phone (chatId=${msg.from})`); return; }
  const body = msg.body || '';
  const ts = msg.timestamp ? new Date(msg.timestamp * 1000).toISOString() : new Date().toISOString();

  const found = await sb(`leads?phone=eq.${encodeURIComponent(phone)}&limit=1`);
  if (!found?.length) {
    log(`📥 inbound from unknown ${phone}: "${body.slice(0, 60)}"`);
    return;
  }
  const lead = found[0];

  const cls = classify(body);
  const updates = {
    total_replies: (lead.total_replies || 0) + 1,
    last_reply_at: ts,
    paused: true,
    next_send_at: null,
  };
  if (cls.dnc && lead.stage !== 'client') {
    updates.stage = 'dnc';
  } else if (['new', 'queued', 'contacted'].includes(lead.stage)) {
    updates.stage = 'replied';
  }
  if (!lead.temperature && cls.temperature) {
    updates.temperature = cls.temperature;
  }

  await sb(`leads?id=eq.${lead.id}`, { method: 'PATCH', body: JSON.stringify(updates) });

  // Best-effort inbound log entry. Tolerated to fail if status='received' is not allowed.
  sb('send_log', {
    method: 'POST',
    body: JSON.stringify({
      lead_id: lead.id,
      channel: 'whatsapp',
      status: 'received',
      message_body: body,
      sent_at: ts,
    })
  }).catch(e => console.warn('inbound send_log insert failed:', e.message));

  log(`📥 ${lead.name} (${phone}) → ${cls.label.toUpperCase()}: "${body.slice(0, 80)}"`);
}

// ── Reply classifier ──────────────────────────────────────────────
// Returns { label, temperature?, dnc? }. Order matters: DNC > cold > hot > warm.
function classify(text) {
  const t = String(text || '').toLowerCase().trim();
  if (!t) return { label: 'empty', temperature: 'warm' };

  // DNC: abuse, strong rejection, legal, asking to stop. Triggers stage=dnc.
  const dnc = [
    /\b(fuck|bsdk|bc\b|mc\b|chutiya|gandu|bhosdike|behenchod|madarchod|maderchod)\b/,
    /\b(stop\s+messag|block\s+me|don'?t\s+(message|contact|call|text)\s+me)\b/,
    /\b(harassment|complaint|legal\s+action|police|fir)\b/,
    /\b(mat\s+bhej(o|na)?|mat\s+karo|message\s+mat)\b/,
    /\b(unsubscribe|opt\s*out|remove\s+me)\b/,
  ];
  if (dnc.some(re => re.test(t))) return { label: 'dnc', dnc: true };

  // Cold: clear "not interested", busy-with-no-reschedule, dismissive.
  const cold = [
    /\b(not\s+interested|nahi\s+chahiye|nahin\s+chahiye|interested\s+nahi)\b/,
    /\b(no\s+thanks?|nope|nahi|nahin)\s*$/i,
    /^\s*(no|nahi|nahin)\s*[.!]?\s*$/,
    /\b(busy\s+hu|abhi\s+free\s+nahi|baad\s+m?ein\s+dekhenge|kabhi\s+nahi)\b/,
    /\b(bye|leave\s+me|chod\s+do)\b/,
  ];
  if (cold.some(re => re.test(t))) return { label: 'cold', temperature: 'cold' };

  // Hot: clear interest, asking price, asking for call/demo, "let's do".
  const hot = [
    /\b(interested\s+(hu|hoon|hai)?|m?ein\s+interested)\b/,
    /\b(call\s+(karo|kar\s+lo|me|kara|do)|kab\s+call|call\s+timing|callback)\b/,
    /\b(price|kitne\s+ka|kitna\s+lagega|kitne\s+rupay|cost|charges?|fee|fees)\b/,
    /\b(demo|meet(ing)?|details?\s+bhej(o|en)?|info\s+bhej)\b/,
    /\blet'?s\s+(do|talk|meet|connect)\b/,
    /\b(send\s+me|share\s+(details|info|brochure))\b/,
    /\b(haan|haa|han|haanji|sure|okay|ok\s+(karo|kar\s+do|hai)|theek\s+hai|chalo)\s*[!.]?\s*$/i,
    /^\s*(yes|haan|haa|sure|ok|okay)\s*[!.]?\s*$/i,
  ];
  if (hot.some(re => re.test(t))) return { label: 'hot', temperature: 'hot' };

  // Default: warm — they engaged, intent unclear. Human should review.
  return { label: 'warm', temperature: 'warm' };
}

// ── Send one lead ──────────────────────────────────────────────────
async function sendOne(lead, step) {
  const digits = String(lead.phone || '').replace(/[^\d]/g, '');
  if (!digits) return { status: 'failed', error: 'No phone' };
  const chatId = digits + '@c.us';
  // Per-lead override beats sequence step template.
  const tpl = (lead.custom_template && String(lead.custom_template).trim())
    ? lead.custom_template
    : step.template;
  const body = render(tpl, lead);

  if (DRY_RUN) {
    log(`[DRY-RUN] ${lead.name} (${lead.phone}) → ${body.slice(0, 80)}…`);
    return { status: 'sent', body };
  }

  let isReg;
  try { isReg = await client.isRegisteredUser(chatId); }
  catch (e) { return { status: 'failed', error: 'isRegistered check failed: ' + e.message, body }; }
  if (!isReg) return { status: 'failed', error: 'Number not on WhatsApp', body };

  // Mark this exact send so the message_create listener skips it (we log it ourselves below).
  markRecentSend(chatId, body);
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
