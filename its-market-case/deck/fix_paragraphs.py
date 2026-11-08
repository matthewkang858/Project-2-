"""Post-process a pptxgenjs deck: pptxgenjs writes one <a:pPr> per text run, so a paragraph
that mixes bold and regular runs gets several paragraph-property blocks and the later
(bullet-less) one wins. Keep only the first <a:pPr> in each paragraph.
Also sets the document properties that pptxgenjs fills with its own name (the deck's company
and subject come from build_deck_v3.js; the chart workbooks embedded in the deck name the
library as creator) to the author."""
import re, sys, zipfile, shutil, os, io
AUTHOR = 'Matthew Kang'
def fix_props(x):
    x = re.sub(r'<dc:creator>PptxGenJS</dc:creator>', '<dc:creator>%s</dc:creator>' % AUTHOR, x)
    x = re.sub(r'<cp:lastModifiedBy>PptxGenJS</cp:lastModifiedBy>', '<cp:lastModifiedBy>%s</cp:lastModifiedBy>' % AUTHOR, x)
    return x
def fix_embedded(data):
    """Rewrite docProps/core.xml inside an embedded chart workbook (an .xlsx inside the .pptx)."""
    src, out = io.BytesIO(data), io.BytesIO()
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            d = zin.read(item.filename)
            if item.filename == 'docProps/core.xml':
                d = fix_props(d.decode('utf-8')).encode('utf-8')
            zout.writestr(item, d)
    return out.getvalue()
PPR = re.compile(r'<a:pPr\b[^>]*/>|<a:pPr\b[^>]*>.*?</a:pPr>', re.S)
PARA = re.compile(r'<a:p>(.*?)</a:p>', re.S)
def fix_para(m):
    body = m.group(1)
    seen = [False]
    def keep_first(pm):
        if seen[0]:
            return ''
        seen[0] = True
        return pm.group(0)
    return '<a:p>' + PPR.sub(keep_first, body) + '</a:p>'
def main(path):
    tmp = path + '.tmp'
    removed = 0
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if re.match(r'ppt/(slides|slideLayouts|slideMasters)/[^/]+\.xml$', item.filename):
                x = data.decode('utf-8')
                before = len(PPR.findall(x))
                x = PARA.sub(fix_para, x)
                removed += before - len(PPR.findall(x))
                data = x.encode('utf-8')
            elif item.filename == 'docProps/core.xml':
                data = fix_props(data.decode('utf-8')).encode('utf-8')
            elif re.match(r'ppt/embeddings/[^/]+\.xlsx$', item.filename):
                data = fix_embedded(data)
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print(os.path.basename(path), 'removed', removed, 'duplicate pPr blocks')
for p in sys.argv[1:]:
    main(p)
