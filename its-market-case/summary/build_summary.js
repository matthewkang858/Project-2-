const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType, LevelFormat, BorderStyle, PageBreak } = require('docx');
const C = JSON.parse(fs.readFileSync('content.json', 'utf8'));
const FONT = 'Arial';
const NAVY = '1B2A41', STEEL = '4F6D7A', TINT = 'EEF2F5';
const p = (text, o = {}) => new Paragraph(Object.assign({ children: [new TextRun({ text, font: FONT, size: o.size || 20, color: o.color || '000000', bold: o.bold, italics: o.italics })], spacing: { after: o.after !== undefined ? o.after : 120, before: o.before || 0 }, alignment: o.align }, o.para || {}));
const bullet = (text) => new Paragraph({ children: [new TextRun({ text, font: FONT, size: 20 })], numbering: { reference: 'bul', level: 0 }, spacing: { after: 80 } });
const h1 = (text) => new Paragraph({ text, heading: HeadingLevel.HEADING_1 });
const h2 = (text) => new Paragraph({ text, heading: HeadingLevel.HEADING_2 });
const border = { style: BorderStyle.SINGLE, size: 4, color: 'C7D3DA' };
function table(t) {
  const total = t.widths.reduce((a, b) => a + b, 0);
  const mk = (txt, w, hdr) => new TableCell({ width: { size: w, type: WidthType.DXA }, shading: hdr ? { type: ShadingType.CLEAR, fill: NAVY, color: 'auto' } : undefined, margins: { top: 60, bottom: 60, left: 80, right: 80 }, borders: { top: border, bottom: border, left: border, right: border }, children: [new Paragraph({ children: [new TextRun({ text: txt, font: FONT, size: 18, bold: !!hdr, color: hdr ? 'FFFFFF' : '000000' })], spacing: { after: 0 } })] });
  const rows = [new TableRow({ tableHeader: true, children: t.headers.map((h, i) => mk(h, t.widths[i], true)) })];
  t.rows.forEach((r, ri) => rows.push(new TableRow({ children: r.map((c, i) => { const cell = mk(c, t.widths[i], false); if (ri % 2 === 1) cell.root[1] && 0; return cell; }) })));
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: t.widths, rows });
}
const children = [];
children.push(new Paragraph({ text: C.title, heading: HeadingLevel.TITLE }));
children.push(p(C.subtitle, { size: 22, color: STEEL, after: 160 }));
children.push(p(C.meta, { size: 18, color: STEEL, italics: true, after: 240 }));
C.sections.forEach(sec => {
  children.push(h1(sec.h1));
  (sec.intro || []).forEach(t => children.push(p(t)));
  sec.subs.forEach(sub => {
    children.push(h2(sub.h2));
    (sub.paras || []).forEach(t => children.push(p(t)));
    (sub.bullets || []).forEach(b => children.push(bullet(b)));
    if (sub.table) { children.push(table(sub.table)); children.push(p('', { after: 120 })); }
  });
});
const doc = new Document({
  creator: 'Matthew Kang', title: C.title,
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 40, bold: true, color: NAVY }, paragraph: { spacing: { before: 0, after: 160 } } },
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 28, bold: true, color: NAVY }, paragraph: { spacing: { before: 360, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 22, bold: true, color: STEEL }, paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } }] }] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } }, children }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync('Public_ITS_Research_Summary.docx', buf); console.log('written', buf.length); });
