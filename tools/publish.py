#!/usr/bin/env python3
"""One-command checked publication. --publish changes GitHub; default builds only."""
import argparse,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from build import ROOT,build
REPO='goolen988/pt-video-editing'
def run(args,cwd=None):return subprocess.run([str(x) for x in args],cwd=cwd,check=True,capture_output=True,text=True).stdout
p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');a=p.parse_args()
run([sys.executable,'-m','unittest','discover','-s',ROOT/'tests','-v'])
if 'Validation is in progress' in (ROOT/'VALIDATION.md').read_text():raise RuntimeError('Finish validation record before building a release')
out=build()
# Verify each packaged installer in clean directories before upload.
import zipfile,hashlib
manifest=json.loads((out/'release.json').read_text())
for asset in manifest['assets']:
 with tempfile.TemporaryDirectory() as d:
  staging=Path(d);z=zipfile.ZipFile(out/asset['name']);assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist());z.extractall(staging);package=next(staging.iterdir());project=staging/'project';project.mkdir();run([sys.executable,package/'install.py','--project',project,'--host','codex','--skill',asset['skill']])
if not a.publish:print('Built and clean-install checked. Add --publish to release.');sys.exit()
run(['gh','auth','status'])
exists=subprocess.run(['gh','repo','view',REPO,'--json','name'],capture_output=True,text=True)
if exists.returncode:
 if 'Could not resolve to a Repository' not in exists.stderr:raise RuntimeError(exists.stderr)
 run(['gh','repo','create',REPO,'--public','--description','Local talking-head editing skills: connect, edit, preview and revise.'])
version=manifest['version'];tag='v'+version
release=subprocess.run(['gh','release','view',tag,'--repo',REPO,'--json','isDraft'],capture_output=True,text=True)
if release.returncode==0:raise RuntimeError('Release tag already exists. Bump VERSION; published archives are immutable.')
if release.returncode and 'release not found' not in release.stderr.lower():raise RuntimeError(release.stderr)
# Fresh staging repo contains only the allowlisted snapshot; no private Git history.
with tempfile.TemporaryDirectory(prefix='pt-publish-') as d:
 stage=Path(d)/'repo';run(['gh','repo','clone',REPO,stage])
 for item in (out/'public').iterdir():
  dest=stage/item.name
  if item.is_dir():
   if dest.exists():shutil.rmtree(dest)
   shutil.copytree(item,dest)
  else:shutil.copy2(item,dest)
 run(['git','add','.'],stage)
 run(['git','-c','user.name=PT Skillset Publisher','-c','user.email=publisher@users.noreply.github.com','commit','-m',f'Release {tag}: connect and video editing skillsets'],stage)
 # New empty GitHub repositories may use the local default branch name.
 branch=run(['git','branch','--show-current'],stage).strip();run(['git','push','origin',f'{branch}:main'],stage)
 run(['gh','repo','edit',REPO,'--default-branch','main'])
 run(['gh','release','create',tag,'--repo',REPO,'--target','main','--draft','--title',f'PT Editing {version}','--notes-file',ROOT/'VALIDATION.md',*[out/x['name'] for x in manifest['assets']],out/'release.json',out/'SHA256SUMS.txt'])
 with tempfile.TemporaryDirectory(prefix='pt-download-check-') as verify:
  run(['gh','release','download',tag,'--repo',REPO,'--dir',verify])
  for x in manifest['assets']:assert hashlib.sha256((Path(verify)/x['name']).read_bytes()).hexdigest()==x['sha256']
 run(['gh','release','edit',tag,'--repo',REPO,'--draft=false','--latest'])
print('Published and downloaded-byte verified: https://github.com/'+REPO+'/releases/tag/'+tag)
