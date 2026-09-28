#!/usr/bin/env python3
"""Portable EDL renderer. All semantic decisions belong to the agent and user."""
import argparse, hashlib, json, math, os, shutil, subprocess, sys, tempfile, unicodedata
from pathlib import Path

def run(args, capture=False):
    return subprocess.run([str(x) for x in args], check=True, text=True, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None).stdout

def read(p): return json.loads(Path(p).read_text())
def write(p, data): Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def probe(p): return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p],True))
def duration(p): return float(probe(p)['format']['duration'])
def number(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def require(ok,msg):
    if not ok: raise ValueError(msg)
def resolve(base,p): return (base/Path(p)).resolve()
def words_load(p):
    words=read(p); prev=-1
    require(isinstance(words,list),'words must be an array')
    for w in words:
        require(isinstance(w,dict) and isinstance(w.get('w'),str) and w['w'].strip() and number(w.get('s')) and number(w.get('e')) and 0<=w['s']<w['e'],'invalid word')
        require(w['s']>=prev,'words not ordered');prev=w['s']
    return words

def timeline(segments, words, dur, fps=None):
    require(isinstance(segments,list) and bool(segments),'segments must be a non-empty array')
    mapped=[]; spans=[]; offset=0
    for seg in segments:
        require(isinstance(seg,dict),'segment must be an object')
        require('start' in seg and 'end' in seg,'segment needs start and end')
        a,b=seg['start'],seg['end']
        require(number(a) and number(b) and 0<=a<b<=dur+0.001,'segment outside source')
        for w in words:
            for boundary in (a,b):
                require(not w['s']+0.015<boundary<w['e']-0.015,'cut crosses word '+w['w'])
            # A word can be within the 15 ms edge tolerance while lying wholly
            # outside this segment. Keep only real intersections so rounding
            # never creates a zero-length caption at a cut.
            clipped_start=max(w['s'],a);clipped_end=min(w['e'],b)
            if clipped_start<clipped_end:
                mapped.append({'w':w['w'],'s':round(offset+clipped_start-a,6),'e':round(offset+clipped_end-a,6)})
        frames=max(1,math.ceil((b-a)*fps-1e-8)) if fps else None
        length=frames/fps if fps else b-a
        spans.append({'source_start':a,'source_end':b,'output_start':offset,'output_end':offset+length,'frames':frames,'tail_hold':length-(b-a),'reason':seg.get('reason','')})
        offset+=length
    return mapped,spans,offset

def group_words(words):
    result=[]; buf=[]
    def flush():
        if buf:
            result.append({'start':buf[0]['s'],'end':buf[-1]['e'],'text':' '.join(w['w'] for w in buf)});buf.clear()
    for w in words:
        if buf and (len(buf)>=4 or w['s']-buf[-1]['e']>0.30 or len(' '.join(x['w'] for x in buf)+w['w'])>26):flush()
        buf.append(w)
        if w['w'].endswith(('.',',','?','!',';',':')):flush()
    flush();return result

def intersect(a,b): return a[0]<b[0]+b[2] and b[0]<a[0]+a[2] and a[1]<b[1]+b[3] and b[1]<a[1]+a[3]
def active(a,b):return a['start']<b['end'] and b['start']<a['end']
def layout(plan,groups,total):
    safe=plan.get('safe_rect',[0.15,0.20,0.70,0.56]);require(len(safe)==4 and all(number(v) for v in safe),'invalid safe rect')
    sx,sy,sw,sh=safe;require(0<=sx<1 and 0<=sy<1 and sw>0 and sh>0 and sx+sw<=1 and sy+sh<=1,'safe rect outside frame')
    faces=plan.get('face_boxes',[]);cards=plan.get('cards',[]); y=plan.get('caption_y',0.71)
    require(number(y),'invalid caption_y')
    boxes=[]
    for c in cards:
        require(all(number(c.get(k)) for k in ['start','end','x','y','w','h']),'invalid card coordinates')
        require(isinstance(c.get('text'),str) and c['text'].strip(),'empty card text')
        require(0<=c['start']<c['end']<=total,'card time outside edit')
        require(c['w']>0 and c['h']>0,'invalid card dimensions')
        boxes.append((c,[c['x'],c['y'],c['w'],c['h']]))
    for g in groups:
        require(number(g.get('start')) and number(g.get('end')) and 0<=g['start']<g['end']<=total+0.001,'caption time outside edit')
        require(isinstance(g.get('text'),str) and len(g['text'])<=60 and '\n' not in g['text'],'split long caption into short groups')
        boxes.append((g,[sx,y-0.07,sw,0.07]))
    for face in faces:
        require(all(number(face.get(k)) for k in ['start','end','x','y','w','h']),'invalid face box')
        require(0<=face['start']<face['end']<=total and 0<=face['x']<1 and 0<=face['y']<1 and face['w']>0 and face['h']>0 and face['x']+face['w']<=1 and face['y']+face['h']<=1,'face box outside frame or edit')
    for item,box in boxes:
        x,yy,w,h=box
        require(x>=sx-1e-6 and yy>=sy-1e-6 and x+w<=sx+sw+1e-6 and yy+h<=sy+sh+1e-6,'text/card outside safe rect')
        for f in faces:
            require(not(active(item,f) and intersect(box,[f['x'],f['y'],f['w'],f['h']])),'text/card intersects supplied face box')
    for i,(a,ab) in enumerate(boxes):
        for b,bb in boxes[i+1:]:require(not(active(a,b) and intersect(ab,bb)),'overlapping text/card windows')

def stamp(t,ass=False):
    units=int(round(t*(100 if ass else 1000))); scale=100 if ass else 1000
    sec,frac=divmod(units,scale);m,s=divmod(sec,60);h,m=divmod(m,60)
    return f'{h}:{m:02}:{s:02}.{frac:02}' if ass else f'{h:02}:{m:02}:{s:02},{frac:03}'

def caption_font_size(text,width,max_size,safe_width):
    # Conservatively budget CJK/full-width glyphs as one em and Latin glyphs
    # by a typical Arial width. ASS does not expose glyph metrics to Python.
    units=0.0
    for char in text:
        east=unicodedata.east_asian_width(char)
        if east in ('W','F'):
            units+=1.0
        elif char.isspace():
            units+=0.34
        elif char in "ilI.,'`:;!|()[]{}":
            units+=0.34
        elif char.isupper():
            units+=0.68
        else:
            units+=0.58
    require(units>0,'caption text is empty')
    size=min(max_size,int(safe_width*width*.88/units))
    require(size>=8,'caption cannot fit inside safe margins; shorten the caption')
    return size

def captions(out,groups,width,height,plan):
    srt='\n\n'.join(f"{i+1}\n{stamp(g['start'])} --> {stamp(g['end'])}\n{g['text']}" for i,g in enumerate(groups))
    (out/'captions.srt').write_text(srt+'\n')
    fs=max(12,round(height*0.032)); y=round(plan.get('caption_y',0.71)*height)
    margin=round(width*plan.get('safe_rect',[.15,.2,.7,.56])[0])
    header=f'''[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{fs},&H00FFFFFF,&H0000FFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,2,0,2,{margin},{margin},0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    lines=[]
    for g in groups:
        text=g['text'].replace('\\','/').replace('{','(').replace('}',')')
        size=caption_font_size(text,width,fs,plan.get('safe_rect',[.15,.2,.70,.56])[2])
        lines.append(f"Dialogue: 0,{stamp(g['start'],True)},{stamp(g['end'],True)},Default,,0,0,0,,{{\\pos({width//2},{y})\\fs{size}}}{text}")
    (out/'captions.ass').write_text(header+'\n'.join(lines)+'\n')

def _render_into(planpath,final_outpath,workpath):
    pp=Path(planpath).resolve();plan=read(pp);base=pp.parent;final_out=Path(final_outpath).resolve();out=Path(workpath).resolve()
    require(isinstance(plan,dict),'edit plan must be an object')
    src=resolve(base,plan['source']);words=words_load(resolve(base,plan['words']))
    require(src.is_file(),'source video does not exist: '+str(src))
    meta=probe(src);videos=[s for s in meta['streams'] if s['codec_type']=='video'];audios=[s for s in meta['streams'] if s['codec_type']=='audio']
    require(videos and audios,'source needs video and audio')
    dur=float(meta['format']['duration'])
    require(all(w['e']<=dur+.1 for w in words),'transcript exceeds source duration')
    width=videos[0]['width'];height=videos[0]['height']
    rotation=next((x.get('rotation',0) for x in videos[0].get('side_data_list',[]) if 'rotation' in x),float(videos[0].get('tags',{}).get('rotate',0)))
    if round(rotation)%180:width,height=height,width
    width+=width%2;height+=height%2
    try:n,d=map(int,videos[0]['avg_frame_rate'].split('/'))
    except (ValueError,AttributeError):n,d=0,0
    fps=plan.get('fps',n/d if d else 30)
    require(number(fps) and 1<=fps<=120,'invalid output fps')
    mapped,spans,total=timeline(plan['segments'],words,dur,fps)
    groups=plan.get('caption_groups',group_words(mapped)) if plan.get('captions',True) else []
    require(isinstance(groups,list),'caption_groups must be an array')
    layout(plan,groups,total)
    saved_plan=dict(plan)
    for key in ['source','words','music']:
        if saved_plan.get(key):saved_plan[key]=os.path.relpath(resolve(base,saved_plan[key]),final_out)
    write(out/'plan.json',saved_plan);write(out/'words.json',mapped);write(out/'timeline.json',spans)
    captions(out,groups,width,height,plan)
    graph=[]
    for i,s in enumerate(spans):
        a,b=s['source_start'],s['source_end'];length=s['output_end']-s['output_start']
        graph.append(f'[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,pad=ceil(iw/2)*2:ceil(ih/2)*2,fps={fps},tpad=stop_mode=clone:stop_duration={2/fps},trim=end_frame={s["frames"]},setpts=N/({fps}*TB)[v{i}]')
        graph.append(f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration={length},afade=t=in:d=0.004,afade=t=out:st={max(0,length-.004)}:d=0.004[a{i}]')
    graph.append(''.join(f'[v{i}][a{i}]' for i in range(len(spans)))+f'concat=n={len(spans)}:v=1:a=1[v][a]')
    graph.append('[a]'+('highpass=f=70,afftdn=nf=-42:nr=6,' if plan.get('clean_audio',False) else '')+'anull[ac]')
    (out/'cut.ffgraph').write_text(';\n'.join(graph))
    run(['ffmpeg','-nostdin','-v','error','-n','-i',src,'-filter_complex_script',out/'cut.ffgraph','-map','[v]','-map','[ac]','-c:v','ffv1','-c:a','pcm_s24le',out/'clean.mkv'])
    cmd=['ffmpeg','-nostdin','-v','error','-n','-i','clean.mkv']; fg=[];v='0:v';audio='0:a';index=1
    has_ass=' ass ' in run(['ffmpeg','-hide_banner','-filters'],True)
    js_captions=bool(groups) and not has_ass
    if plan.get('cards') or js_captions:
        write(out/'graphics.json',{'width':width,'height':height,'fps':fps,'duration':total,'cards':plan.get('cards',[]),'captions':groups if js_captions else [],'caption_y':plan.get('caption_y',.71),'safe_rect':plan.get('safe_rect',[.15,.20,.70,.56])})
        run(['node',Path(__file__).with_name('graphics.cjs'),out/'graphics.json',out/'graphics'])
        cmd+=['-framerate',str(fps),'-i','graphics/%06d.png'];fg.append(f'[{v}][{index}:v]overlay=shortest=1[vcard]');v='vcard';index+=1
    if groups and not js_captions:fg.append(f'[{v}]ass=captions.ass[vtext]');v='vtext'
    if plan.get('music'):
        gain=plan.get('music_gain',.08);require(number(gain) and 0<=gain<=1,'invalid music gain')
        cmd+=['-stream_loop','-1','-i',str(resolve(base,plan['music']))]
        fg.append(f'[{index}:a]atrim=duration={total},asetpts=PTS-STARTPTS,volume={gain},afade=t=out:st={max(0,total-1)}:d=1[bed]')
        fg.append('[0:a][bed]amix=inputs=2:duration=first:normalize=0[mix]');audio='mix'
    fg.append(f'[{audio}]alimiter=limit=0.95:level=false[afinal]')
    cmd+=['-filter_complex',';'.join(fg),'-map',f'[{v}]' if v!='0:v' else v,'-map','[afinal]','-t',str(total),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart','candidate.mp4']
    subprocess.run(cmd,cwd=out,check=True)
    actual=duration(out/'candidate.mp4');require(abs(actual-total)<.10,'duration mismatch')
    check(out/'candidate.mp4')
    receipt={'status':'REVIEW_CANDIDATE','version':plan.get('version',final_out.name),'source_sha256':sha(src),'output_sha256':sha(out/'candidate.mp4'),'input_plan_sha256':sha(pp),'saved_plan_sha256':sha(out/'plan.json'),'timeline_sha256':sha(out/'timeline.json'),'expected_duration':total,'actual_duration':actual,'fps':fps,'face_check':'SUPPLIED_BOXES' if plan.get('face_boxes') else 'NOT_CHECKED','playback_review':'PENDING','user_acceptance':'PENDING','ffmpeg':run(['ffmpeg','-version'],True).splitlines()[0]}
    write(out/'receipt.json',receipt)
    return receipt

def render(planpath,outpath):
    final_out=Path(outpath).resolve()
    require(not os.path.lexists(final_out),'output exists; choose a new revision directory')
    final_out.parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='.'+final_out.name+'.rendering-',dir=final_out.parent))
    try:
        receipt=_render_into(planpath,final_out,work)
        # The completed directory appears only after all render and decode checks pass.
        os.rename(work,final_out)
        print(json.dumps(receipt))
    except BaseException:
        shutil.rmtree(work,ignore_errors=True)
        raise

def check(p):
    meta=probe(p);types=[s['codec_type'] for s in meta['streams']];require('video' in types and 'audio' in types,'missing audio/video')
    run(['ffmpeg','-nostdin','-v','error','-xerror','-i',p,'-f','null','-'])
    return {'decode':'PASS','duration':float(meta['format']['duration']),'streams':types,'acceptance':'NOT_INFERRED'}

def suggest(src,wj,out):
    words=words_load(wj);dur=duration(src);cuts=[]
    for prev,nxt in zip(words,words[1:]):
        if nxt['s']-prev['e']>.5:cuts.append((prev['e']+.12,nxt['s']-.12))
    segs=[];t=0
    for a,b in cuts:segs.append({'start':t,'end':a,'reason':'Candidate pause tightening; audition seam'});t=b
    segs.append({'start':t,'end':dur,'reason':'Keep remaining speech'})
    write(out,{'version':'v001','source':str(Path(src).resolve()),'words':str(Path(wj).resolve()),'segments':segs,'captions':True,'clean_audio':False,'note':'Pause proposal only; no semantic filler deletion performed.'})

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    r=sub.add_parser('render');r.add_argument('plan');r.add_argument('out')
    c=sub.add_parser('check');c.add_argument('video')
    s=sub.add_parser('suggest');s.add_argument('video');s.add_argument('words');s.add_argument('out')
    q=sub.add_parser('probe');q.add_argument('video');a=p.parse_args()
    if a.cmd=='render':render(a.plan,a.out)
    elif a.cmd=='check':print(json.dumps(check(a.video)))
    elif a.cmd=='probe':print(json.dumps(probe(a.video),indent=2))
    else:suggest(a.video,a.words,a.out)
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,subprocess.CalledProcessError) as e:
        print(str(e),file=sys.stderr)
        if isinstance(e,subprocess.CalledProcessError) and e.stderr:
            detail=e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else e.stderr
            print(detail.rstrip(),file=sys.stderr)
        sys.exit(1)
