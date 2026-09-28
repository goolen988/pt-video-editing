#!/usr/bin/env python3
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output');p.add_argument('--model',default='small');p.add_argument('--language',default=None);a=p.parse_args()
if Path(a.output).exists():raise SystemExit('Output exists; preserve it or choose a new filename')
from faster_whisper import WhisperModel
model=WhisperModel(a.model,device='cpu',compute_type='int8')
segments,info=model.transcribe(a.source,word_timestamps=True,language=a.language,vad_filter=True)
words=[{'w':w.word.strip(),'s':round(w.start,3),'e':round(w.end,3)} for s in segments for w in s.words or [] if w.end>w.start]
if not words:raise SystemExit('No speech found; inspect source audio before continuing')
Path(a.output).write_text(json.dumps(words,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'words':len(words),'language':info.language,'status':'TRANSCRIPT_NEEDS_REVIEW'}))
