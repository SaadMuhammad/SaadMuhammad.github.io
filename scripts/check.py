"""Check the built site for broken local links, missing assets and duplicate IDs."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import posixpath
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
BASE=json.loads((ROOT/'site.json').read_text(encoding='utf-8')).get('base_path','').rstrip('/')

class Document(HTMLParser):
    def __init__(self,path):
        super().__init__();self.refs=[];self.ids=[];self.h1=0;self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        for key in ['href','src']:
            if a.get(key):self.refs.append(a[key])

def check():
    docs={path:Document(path) for path in OUT.rglob('*.html')}
    problems=[]
    for path,doc in docs.items():
        if len(doc.ids)!=len(set(doc.ids)):problems.append(f'{path}: duplicate IDs')
        if doc.h1!=1:problems.append(f'{path}: expected one h1, found {doc.h1}')
        for ref in doc.refs:
            parsed=urlsplit(ref)
            if parsed.scheme or parsed.netloc:continue
            local=unquote(parsed.path)
            if not local:target=path
            elif local.startswith('/'):
                if BASE and not local.startswith(BASE+'/'):problems.append(f'{path}: missing base_path: {ref}');continue
                target=OUT/local[len(BASE):].lstrip('/')
            else:target=path.parent/local
            target=Path(posixpath.normpath(str(target)))
            if target.is_dir():target=target/'index.html'
            if not target.exists():problems.append(f'{path.relative_to(OUT)}: missing {ref}')
            elif parsed.fragment and target in docs and unquote(parsed.fragment) not in docs[target].ids:
                problems.append(f'{path.relative_to(OUT)}: missing anchor {ref}')
    for name in ['feed.xml','sitemap.xml']:ET.parse(OUT/name)
    assert not problems,'\n'.join(problems)
    print(f'Checked {len(docs)} HTML pages: local links, fragments, images, scripts, styles, heading structure and XML feeds pass.')

if __name__=='__main__':check()
