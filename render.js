const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file:///home/user/propalate-os/drama_consolidation.html');
  await page.waitForTimeout(1200); // let fonts load
  const el = await page.$('.canvas');
  await el.screenshot({ path: '/home/user/propalate-os/drama_consolidation.png' });
  await browser.close();
  console.log('done');
})();
