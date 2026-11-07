// Shared deck frame: theme, layouts, helpers. Consulting-style, 13.33 x 7.5 in.
const pptxgen = require('pptxgenjs');

const THEME = {
  name: 'Public ITS Case',
  headFontFace: 'Calibri',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '1B2A41',   // ink navy (text, headers)
    lt1: 'FFFFFF',
    dk2: '4F6D7A',   // steel (secondary text)
    lt2: 'EEF2F5',   // panel tint
    accent1: '1B2A41', // navy
    accent2: 'D9822B', // signal amber (highlight)
    accent3: '4F6D7A', // steel
    accent4: '9DB4C0', // light steel
    accent5: 'C7D3DA', // pale
    accent6: '7A8B99', // mid grey
    hlink: '1B2A41', folHlink: '4F6D7A',
  },
};
const HEX = THEME.colors;

function newDeck() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'Matthew Kang';
  pres.title = 'Public ITS Market: Roadway (Bus) and Railway';
  const C = pres.SchemeColor;

  // Content layout: action title + tracker + footer with source and page number
  pres.defineSlideMaster({
    title: 'CONTENT',
    background: { color: 'FFFFFF' },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.45, y: 0.32, w: 11.6, h: 0.95, fontSize: 20, bold: true, color: C.text1, valign: 'top', align: 'left', margin: 0, isTextBox: true }, text: '' } },
      { placeholder: { options: { name: 'tracker', type: 'body', x: 11.1, y: 0.18, w: 1.8, h: 0.3, fontSize: 9, color: C.text2, align: 'right', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'source', type: 'body', x: 0.45, y: 6.9, w: 12.45, h: 0.3, fontSize: 8.5, color: C.text2, valign: 'top', margin: 0 }, text: '' } },
      { text: { text: 'Public ITS market case', options: { x: 0.45, y: 7.22, w: 4, h: 0.2, fontSize: 8, color: C.text2, margin: 0, isTextBox: true } } },
    ],
    slideNumber: { x: 12.5, y: 7.18, w: 0.4, h: 0.25, fontSize: 8, color: HEX.dk2, align: 'right' },
  });

  // Cover layout: dark
  pres.defineSlideMaster({
    title: 'COVER',
    background: { color: HEX.dk1 },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: 0.8, y: 2.3, w: 11.5, h: 1.6, fontSize: 36, bold: true, color: C.background1, valign: 'bottom', align: 'left', margin: 0 }, text: '' } },
      { placeholder: { options: { name: 'body', type: 'body', x: 0.8, y: 4.05, w: 11.5, h: 1.4, fontSize: 16, color: 'C7D3DA', valign: 'top', margin: 0 }, text: '' } },
    ],
  });

  return { pres, C };
}

// ---- helpers ------------------------------------------------------------
const bodyText = (slide, text, o) => slide.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 11, color: HEX.dk1, valign: 'top' }, o));

function panelHeader(slide, text, x, y, w, opts = {}) {
  // subtle tinted header bar for a panel (not an accent stripe: it is the header cell itself)
  slide.addShape('rect', { x, y, w, h: 0.3, fill: { color: opts.fill || HEX.dk1 }, line: { color: opts.fill || HEX.dk1 } });
  slide.addText(text, { x: x + 0.08, y, w: w - 0.16, h: 0.3, fontSize: 10.5, bold: true, color: 'FFFFFF', valign: 'middle', margin: 0, isTextBox: true });
}

function stat(slide, big, label, x, y, w, opts = {}) {
  slide.addText(big, { x, y, w, h: 0.55, fontSize: opts.size || 26, bold: true, color: opts.color || HEX.accent2, margin: 0, isTextBox: true, align: opts.align || 'left' });
  slide.addText(label, { x, y: y + 0.55, w, h: 0.5, fontSize: 9.5, color: HEX.dk2, margin: 0, isTextBox: true, valign: 'top', align: opts.align || 'left' });
}

const tableStyle = {
  fontFace: 'Calibri', fontSize: 9, color: HEX.dk1, border: { type: 'solid', pt: 0.5, color: 'C7D3DA' }, margin: 0.04,
};
function headerRow(cells) {
  return cells.map(t => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: HEX.dk1 }, fontSize: 9, valign: 'middle' } }));
}

const chartBase = {
  chartColors: [HEX.dk1, HEX.accent3, HEX.accent2, HEX.accent4, HEX.accent6, HEX.accent5],
  catAxisLabelColor: HEX.dk2, valAxisLabelColor: HEX.dk2, catAxisLabelFontSize: 9, valAxisLabelFontSize: 9,
  catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt', legendFontFace: '+mn-lt',
  valGridLine: { color: 'E3E8EC', size: 0.5 }, catGridLine: { style: 'none' },
  legendFontSize: 9, legendColor: HEX.dk2, dataLabelColor: HEX.dk1, dataLabelFontSize: 8.5,
  catAxisLineShow: false, valAxisLineShow: false, plotArea: { fill: { color: 'FFFFFF' } }, chartArea: { fill: { color: 'FFFFFF' } },
};

module.exports = { THEME, HEX, newDeck, bodyText, panelHeader, stat, tableStyle, headerRow, chartBase };
