#!/usr/bin/env python3
"""Build a local review with source/candidate players and version-bound feedback."""
import argparse,html,json,os,shutil
from pathlib import Path
from urllib.parse import quote
p=argparse.ArgumentParser();p.add_argument('render');p.add_argument('--source',required=True);a=p.parse_args();r=Path(a.render).resolve();receipt=json.loads((r/'receipt.json').read_text())
source=Path(a.source).resolve();link=r/('source'+source.suffix)
if not link.exists():
 try:os.link(source,link)
 except OSError:shutil.copy2(source,link)
seed=json.dumps({'version':receipt['version'],'output_sha256':receipt['output_sha256'],'status':'unreviewed','comments':[]}).replace('<','\\u003c')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Review your edit</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f2f0e9;color:#19352d;font:18px/1.5 system-ui}main{max-width:1100px;margin:auto;padding:32px}h1{font:52px Georgia;margin:10px 0}.players{display:grid;grid-template-columns:1fr 1fr;gap:24px}video{width:100%;height:440px;background:#111;border-radius:8px}textarea{width:100%;min-height:110px;padding:12px;font:inherit}button,select{font:inherit;padding:12px;border:1px solid #19352d;border-radius:5px;background:white;margin:8px 8px 8px 0}button{cursor:pointer}li{margin:12px 0}.note{font-size:14px}#saved{min-height:24px}@media(max-width:650px){.players{grid-template-columns:1fr}h1{font-size:38px}main{padding:18px}video{height:340px}}</style>
<main><p>PT VIDEO EDITING / REVIEW CANDIDATE</p><h1>Watch it. Tell us what to change.</h1><p>Version <strong>VERSION</strong>. Comments refer to the edited video's time.</p><div class="players"><section><h2>Original</h2><video id="source" controls preload="metadata" src="SOURCE"></video></section><section><h2>This edit</h2><video id="edit" controls preload="metadata" src="candidate.mp4"></video></section></div>
<p><button id="match">Show this moment in original</button> <span id="time">0:00</span></p><label for="comment">Your feedback at this moment</label><textarea id="comment" placeholder="The title is too close to my face here."></textarea><button id="add">Add timestamped comment</button><ol id="comments"></ol><label for="decision">Your decision</label> <select id="decision"><option value="unreviewed">Still reviewing</option><option value="changes_requested">I'd like changes</option><option value="accepted">I accept this version</option></select><p id="saved" role="status"></p><button id="export">Download feedback for your agent</button><p class="note">Saved in this browser only. Download and give the JSON file to your agent to carry feedback back. Acceptance is not social publication.</p></main>
<script>
const seed=SEED;const key='pt-review:'+seed.output_sha256;let state=seed;try{state=JSON.parse(localStorage.getItem(key))||seed}catch{}
const edit=document.querySelector('#edit'),source=document.querySelector('#source'),comment=document.querySelector('#comment'),decision=document.querySelector('#decision');let mapping=[];fetch('timeline.json').then(r=>r.json()).then(x=>mapping=x);
const fmt=t=>Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
function save(){state.draft=comment.value;try{localStorage.setItem(key,JSON.stringify(state));document.querySelector('#saved').textContent='Saved in this browser.'}catch{document.querySelector('#saved').textContent='Browser storage unavailable — download feedback before leaving.'}}
function draw(){const list=document.querySelector('#comments');list.replaceChildren();for(const c of state.comments){const li=document.createElement('li'),b=document.createElement('button');b.textContent=fmt(c.time);b.onclick=()=>edit.currentTime=c.time;li.append(b,document.createTextNode(c.text));list.append(li)}decision.value=state.status}
comment.value=state.draft||'';comment.oninput=save;decision.onchange=()=>{state.status=decision.value;save()};
document.querySelector('#add').onclick=()=>{if(!comment.value.trim())return;state.comments.push({time:Number(edit.currentTime.toFixed(3)),text:comment.value.trim()});comment.value='';save();draw()};
edit.ontimeupdate=()=>document.querySelector('#time').textContent=fmt(edit.currentTime);
document.querySelector('#match').onclick=()=>{const t=edit.currentTime,s=mapping.find(s=>t>=s.output_start&&t<s.output_end);if(s){source.currentTime=Math.min(s.source_end,s.source_start+t-s.output_start);source.pause()}};
document.querySelector('#export').onclick=()=>{save();const body={...state,exported_at:new Date().toISOString()};const url=URL.createObjectURL(new Blob([JSON.stringify(body,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='feedback-'+state.version+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};draw();
</script></html>'''
page=page.replace('VERSION',html.escape(str(receipt['version']))).replace('SOURCE',quote(link.name)).replace('SEED',seed)
(r/'review.html').write_text(page);print(r/'review.html')
