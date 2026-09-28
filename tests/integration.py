"""Run actual media/JS pipeline in a fresh folder. Synthetic media is explicitly labeled."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];scripts=ROOT/'skills/pt-video-editing/scripts'
def run(a):subprocess.run([str(x) for x in a],check=True)
def write(p,d):p.write_text(json.dumps(d,indent=2))
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
run(['ffmpeg','-v','error','-n','-f','lavfi','-i','color=c=0x43536b:s=360x640:r=24:d=4','-f','lavfi','-i','sine=frequency=440:duration=4','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',out/'source.mp4'])
write(out/'words.json',[{'w':'Illustrative','s':.2,'e':.6},{'w':'sample.','s':.65,'e':1},{'w':'Clear','s':2.2,'e':2.5},{'w':'steps.','s':2.55,'e':3}])
plan={'version':'v001','source':'source.mp4','words':'words.json','segments':[{'start':2,'end':3.5,'reason':'Move complete highlight first'},{'start':0,'end':1.5,'reason':'Then context'}],'captions':True,'clean_audio':True,'cards':[{'start':.1,'end':1.4,'text':'SYNTHETIC TEST','x':.15,'y':.21,'w':.7,'h':.14}],'face_boxes':[{'start':0,'end':3,'x':.3,'y':.4,'w':.4,'h':.2}]}
write(out/'plan-v001.json',plan);run([sys.executable,scripts/'edit.py','render',out/'plan-v001.json',out/'v001'])
saved=json.loads((out/'v001/plan.json').read_text())
assert (out/'v001'/saved['source']).resolve()==(out/'source.mp4').resolve()
assert (out/'v001'/saved['words']).resolve()==(out/'words.json').resolve()
run([sys.executable,scripts/'review.py',out/'v001','--source',out/'source.mp4'])
plan['version']='v002';plan['segments'][0]['end']=3.8;plan['face_boxes'][0]['end']=3.3
write(out/'plan-v002.json',plan);run([sys.executable,scripts/'edit.py','render',out/'plan-v002.json',out/'v002'])
assert abs(json.loads((out/'v002/words.json').read_text())[2]['s']-(44/24+.2))<.00001
assert (out/'v001/candidate.mp4').exists()
print('INTEGRATION PASS: reordering, word remap, JS cards, captions, audio cleanup, preserved version, revision +0.3 seconds')
