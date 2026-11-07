"""Post-process a pptxgenjs deck: pptxgenjs writes one <a:pPr> per text run, so a paragraph
that mixes bold and regular runs gets several paragraph-property blocks and the later
(bullet-less) one wins. Keep only the first <a:pPr> in each paragraph."""
import re, sys, zipfile, shutil, os
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
            zout.writestr(item, data)
    shutil.move(tmp, path)
    print(os.path.basename(path), 'removed', removed, 'duplicate pPr blocks')
for p in sys.argv[1:]:
    main(p)
