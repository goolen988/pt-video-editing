#!/usr/bin/env python3
"""Project-scoped skill install with rollback backup; never touches user edit files."""
import argparse,json,shutil,time
from pathlib import Path

def install(project,host,skill):
 root=Path(__file__).resolve().parent;src=root/'skills'/skill
 if not src.is_dir():raise ValueError('Skill not present in this package: '+skill)
 if any(p.is_symlink() for p in src.rglob('*')):raise ValueError('Symlink in package')
 project=Path(project).expanduser().resolve()
 if (project/'.pt-skill-backups').is_symlink():raise ValueError('Refusing symlink backup directory')
 if not project.is_dir():raise ValueError('Choose an existing authorized project directory')
 target=project/('.agents' if host=='codex' else '.claude')/'skills'/skill
 for p in [target,*target.parents]:
  if p==project:break
  if p.is_symlink():raise ValueError('Refusing symlink install target')
 target.parent.mkdir(parents=True,exist_ok=True);backup=None;stage=target.with_name(skill+'.staging-'+str(time.time_ns()))
 shutil.copytree(src,stage)
 try:
  if target.exists():
   backup=project/'.pt-skill-backups'/(skill+'-'+str(time.time_ns()));backup.parent.mkdir(exist_ok=True);target.rename(backup)
  stage.rename(target)
 except Exception:
  if backup and backup.exists() and not target.exists():backup.rename(target)
  raise
 return {'skill':skill,'version':(root/'VERSION').read_text().strip(),'installed':str(target),'backup':str(backup) if backup else None,'user_data':'untouched'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--host',choices=['codex','claude'],required=True);p.add_argument('--skill',choices=['pt-connect','pt-video-editing'],required=True);a=p.parse_args();print(json.dumps(install(a.project,a.host,a.skill),indent=2))
