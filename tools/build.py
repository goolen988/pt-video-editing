#!/usr/bin/env python3
"""Allowlisted reproducible archives and a public source snapshot."""
import hashlib,json,re,shutil,zipfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOP=['ACCEPTANCE.md','README.md','START.md','SOURCES.md','sources.json','MAINTAINING.md','VALIDATION.md','LICENSE','THIRD_PARTY.md','VERSION','install.py']
DIRS=['skills','tools','tests','examples']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files():
 result=[ROOT/n for n in TOP]
 for d in DIRS:
  result.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='.DS_Store')
 return sorted(result)
def build():
 version=(ROOT/'VERSION').read_text().strip();assert re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-z0-9.]+)?',version)
 selected=files();secret=re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{24,}|-----BEGIN [A-Z ]*PRIVATE KEY-----')
 for p in selected:
  assert p.is_file() and not p.is_symlink(),p
  text=p.read_text();assert not secret.search(text),f'Possible secret: {p}'
  # Source programs may test for absolute local paths, but no actual home path is distributable.
  assert not re.search(r'/Users/[A-Za-z0-9_-]+/',text),f'Personal path: {p}'
 default_out = ROOT.parents[1]/'public/Video Editing/.local/builds' if ROOT.parent.name == 'dev' else ROOT/'.build'
 out=Path(os.environ.get('PT_BUILD_ROOT', str(default_out))).expanduser()/version
 if out.exists():shutil.rmtree(out)
 snapshot=out/'public';snapshot.mkdir(parents=True)
 for p in selected:
  target=snapshot/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 assets=[]
 for skill in ['pt-connect','pt-video-editing']:
  archive=out/f'{skill}-{version}.zip';items=[p for p in selected if (p.relative_to(ROOT).parts[:2]==('skills',skill) and 'evals' not in p.relative_to(ROOT).parts) or p.name in ['install.py','VERSION','SOURCES.md','sources.json','LICENSE','THIRD_PARTY.md'] and p.parent==ROOT]
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
   for p in items:
    name=str(Path(f'{skill}-{version}')/p.relative_to(ROOT));info=zipfile.ZipInfo(name,(2026,9,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,p.read_bytes())
  assets.append({'skill':skill,'name':archive.name,'sha256':digest(archive),'bytes':archive.stat().st_size,'url':f'https://github.com/goolen988/pt-video-editing/releases/download/v{version}/{archive.name}'})
 manifest={'version':version,'channel':'preview','repository':'goolen988/pt-video-editing','assets':assets,'files':{str(p.relative_to(ROOT)):digest(p) for p in selected},'verification':'See VALIDATION.md; no user acceptance or social publication implied.'}
 for p in [out/'release.json',snapshot/'release.json']:p.write_text(json.dumps(manifest,indent=2)+'\n')
 (out/'SHA256SUMS.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in assets))
 print(json.dumps({'build':str(out),'files':len(selected),'assets':assets},indent=2));return out
if __name__=='__main__':build()
