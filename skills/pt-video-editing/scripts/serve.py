#!/usr/bin/env python3
"""Loopback-only static server with single-range video seeking."""
import argparse,http.server,os,re
from functools import partial
from pathlib import Path
class Handler(http.server.SimpleHTTPRequestHandler):
 def send_head(self):
  path=Path(self.translate_path(self.path)).resolve();root=Path(self.directory).resolve()
  if not path.is_relative_to(root):self.send_error(403);return None
  self.remaining=None
  header=self.headers.get('Range')
  if not header or not path.is_file():return super().send_head()
  size=path.stat().st_size;m=re.fullmatch(r'bytes=(\d*)-(\d*)',header)
  if not m or not any(m.groups()):self.send_error(416);return None
  left,right=m.groups();start=int(left) if left else max(0,size-int(right));end=min(int(right),size-1) if left and right else size-1
  if start>end or start>=size:self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
  f=path.open('rb');f.seek(start);self.remaining=end-start+1
  self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(self.remaining));self.end_headers();return f
 def copyfile(self,source,output):
  if self.remaining is None:return super().copyfile(source,output)
  while self.remaining:
   block=source.read(min(65536,self.remaining))
   if not block:break
   output.write(block);self.remaining-=len(block)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory');p.add_argument('--port',type=int,default=8765);a=p.parse_args();server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),partial(Handler,directory=os.path.abspath(a.directory)));print(f'http://127.0.0.1:{server.server_port}/review.html',flush=True);server.serve_forever()
