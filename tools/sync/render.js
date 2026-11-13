// Captures slide images + home screens from tools/sync/.render (served by serve.py on :8765)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const REPO = path.resolve(__dirname, '..', '..'); const IMG = path.join(REPO, 'docs', 'img');
const slides = fs.readFileSync(path.join(__dirname, 'slides.txt'), 'utf8').trim().split('\n').map(l => l.split('\t')[0]);
(async () => {
  const b = await chromium.launch(); const errs = [];
  let p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); p.on('pageerror', e => errs.push(e.message));
  for (const [i, f] of slides.entries()) {
    await p.goto('http://localhost:8765/E_' + f + '.dc.html'); await p.waitForTimeout(f === 'BrandLogo' ? 6500 : 2600);
    await p.screenshot({ path: path.join(IMG, `slide-${String(i + 1).padStart(2, '0')}.jpg`), type: 'jpeg', quality: 86 });
  }
  p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  for (const f of ['Main', 'Alert', 'Voice', 'Done']) { await p.goto('http://localhost:8765/' + f + '.dc.html'); await p.waitForTimeout(2200); await p.screenshot({ path: path.join(IMG, `screen-${f}.png`) }); }
  console.log('slides:', slides.length, 'errors:', errs.length ? errs.slice(0, 5).join(' | ') : 'none'); await b.close();
})();
