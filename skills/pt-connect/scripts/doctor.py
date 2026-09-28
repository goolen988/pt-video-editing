#!/usr/bin/env python3
import argparse,json,platform,shutil,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);a=p.parse_args();root=Path(a.workspace).expanduser().resolve()
result={'platform':platform.platform(),'workspace_exists':root.is_dir(),'write_verified':False,'tools':{},'browser_control':'HOST_CHECK_REQUIRED','playback_audio':'HOST_CHECK_REQUIRED','provider_auth':'NOT_CHECKED'}
if root.is_dir():
 try:
  with tempfile.TemporaryDirectory(prefix='.pt-probe-',dir=root) as d:
   f=Path(d)/'probe';f.write_text('ok');result['write_verified']=f.read_text()=='ok'
 except OSError as e:result['write_error']=type(e).__name__
for tool in ['python3','ffmpeg','ffprobe','node','yt-dlp']:
 exe=shutil.which(tool);result['tools'][tool]={'present':bool(exe)}
 if exe:
  try:result['tools'][tool]['version']=subprocess.run([exe,'-version' if tool in ['ffmpeg','ffprobe'] else '--version'],capture_output=True,text=True,timeout=10).stdout.splitlines()[0]
  except (OSError,IndexError,subprocess.TimeoutExpired):result['tools'][tool]['version']='UNKNOWN'
result['basic_tools_present']=all(result['tools'][t]['present'] for t in ['python3','ffmpeg','ffprobe'])
result['editing_verified']=False
print(json.dumps(result,indent=2))
