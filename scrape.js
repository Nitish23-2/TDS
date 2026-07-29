const { chromium } = require('playwright');

(async () => {
  const seeds = ['88', '89', '90', '91', '92', '93', '94', '95', '96', '97'];
  let grandTotal = 0;

  const browser = await chromium.launch();
  const page = await browser.newPage();

  for (const seed of seeds) {
    const url = `https://sanand0.github.io/tdsdata/js_table/?seed=${seed}`;
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForSelector('table td');
    const cellTexts = await page.$$eval('table td', cells =>
      cells.map(c => parseInt(c.textContent.trim(), 10) || 0)
    );
    const seedSum = cellTexts.reduce((acc, val) => acc + val, 0);
    console.log(`Seed ${seed} sum: ${seedSum}`);
    grandTotal += seedSum;
  }

  await browser.close();
  console.log(`TOTAL SUM: ${grandTotal}`);
})();
