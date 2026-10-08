import pw from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pw;

const DIR = '/home/user/HelpMeDraft---projet-fil-rouge/docs/dossier';
const SRC = `file://${DIR}/dossier-projet.html`;
const OUT = process.argv[2] || '/home/user/HelpMeDraft---projet-fil-rouge/docs/Dossier-projet-HelpMeDraft.pdf';

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await browser.newPage();
await page.goto(SRC, { waitUntil: 'networkidle' });
await page.emulateMedia({ media: 'print' });

const footer = `
<div style="width:100%;font-family:Inter,Arial,sans-serif;font-size:7.3pt;color:#8795a1;
            padding:0 19mm;display:flex;justify-content:space-between;align-items:center;">
  <span>Dossier de projet — HelpMeDraft · Ophélie Bellissens</span>
  <span class="pageNumber"></span>
</div>`;

const common = {
  format: 'A4',
  printBackground: true,
  margin: { top: '20mm', bottom: '16mm', left: '0mm', right: '0mm' },
};

await page.pdf({ ...common, path: `${DIR}/.body.pdf`, displayHeaderFooter: true,
                 headerTemplate: '<div></div>', footerTemplate: footer });
await page.pdf({ ...common, path: `${DIR}/.cover.pdf`, pageRanges: '1' });
await browser.close();
console.log('ok', OUT);
