"""Offline schema, local-link and generated Mermaid-structure checks."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from collections import Counter
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    data=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
    meta=json.loads((ROOT/'data/metadata.json').read_text(encoding='utf-8'))
    required={'family','id','title','status','entry','s1','s2','s3','s4','project','gate','next','source','resources','checked'}
    allowed={'现有','新兴分工','发展路径','未来假设'}
    ids=[]
    for t in data:
        id=t.get('id','<missing>');ids.append(id)
        for field in required:
            if not t.get(field):errors.append(f'{id}: missing {field}')
        if not re.fullmatch(r'[a-z][a-z0-9-]*',id):errors.append(f'{id}: invalid id')
        if t.get('status') not in allowed:errors.append(f'{id}: invalid status')
        if t.get('family') not in meta['familyChanges']:errors.append(f'{id}: unknown family')
        for key in [t.get('source'),*t.get('resources',[])]:
            if key not in meta['sources']:errors.append(f'{id}: unknown resource {key}')
    for id,n in Counter(ids).items():
        if n!=1:errors.append(f'duplicate route: {id}')
    for key,s in meta['sources'].items():
        if urlsplit(s.get('url','')).scheme!='https':errors.append(f'{key}: invalid HTTPS source')
    route_files=list((ROOT/'roadmaps').rglob('*.md'))
    if len(route_files)!=len(data):errors.append('route document count does not match data')
    if {f.stem for f in route_files}!=set(ids):errors.append('route filenames do not match ids')
    links=0;diagrams=0
    files=list(ROOT.rglob('*.md'))
    for file in files:
        text=file.read_text(encoding='utf-8')
        rel=str(file.relative_to(ROOT))
        fences=re.findall(r'^```.*$',text,re.M)
        if len(fences)%2:errors.append(f'{rel}: unmatched code fence')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            target=target.strip().strip('<>')
            parsed=urlsplit(target)
            if parsed.scheme or target.startswith('#'):continue
            links+=1
            dest=(file.parent/unquote(parsed.path)).resolve()
            if not dest.is_relative_to(ROOT):errors.append(f'{rel}: link escapes repository {target}')
            elif not dest.exists():errors.append(f'{rel}: broken local link {target}')
        for graph in re.findall(r'```mermaid\n(.*?)\n```',text,re.S):
            diagrams+=1
            if not graph.strip().startswith('flowchart '):errors.append(f'{rel}: unexpected graph syntax')
            definitions=re.findall(r'\b([A-Za-z][A-Za-z0-9_]*)\["[^"\n]*"\]',graph)
            if len(definitions)!=len(set(definitions)):errors.append(f'{rel}: duplicate Mermaid node')
            for a,b in re.findall(r'\b([A-Za-z][A-Za-z0-9_]*)\s*(?:-->|---|-\.->)\s*([A-Za-z][A-Za-z0-9_]*)\b',re.sub(r'\["[^"\n]*"\]','',graph)):
                if a not in definitions or b not in definitions:errors.append(f'{rel}: undefined Mermaid endpoint {a}/{b}')
    for id in meta['overrides']:
        if id not in ids:errors.append(f'AI override references unknown route {id}')
    result={'routes':len(data),'families':len(set(t['family'] for t in data)), 'markdown_files':len(files),'local_links':links,'mermaid_diagrams':diagrams,'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:sys.exit(1)

if __name__=='__main__':main()
