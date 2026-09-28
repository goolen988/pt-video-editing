#!/usr/bin/env python3
"""Build a local review page with version-bound, source-mapped feedback."""
import argparse
import hashlib
import html
import json
import math
import os
import shutil
from pathlib import Path
from urllib.parse import quote


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_context(render_dir, source_path):
    render_dir = Path(render_dir).resolve()
    source_path = Path(source_path).resolve()
    receipt_path = render_dir / 'receipt.json'
    candidate_path = render_dir / 'candidate.mp4'
    plan_path = render_dir / 'plan.json'
    timeline_path = render_dir / 'timeline.json'
    require(receipt_path.is_file(), 'receipt.json is missing; render a candidate first')
    require(candidate_path.is_file(), 'candidate.mp4 is missing')
    require(source_path.is_file(), 'source video does not exist: ' + str(source_path))
    receipt = json.loads(receipt_path.read_text())
    require(receipt.get('status') == 'REVIEW_CANDIDATE', 'render is not a review candidate')
    require(sha(candidate_path) == receipt.get('output_sha256'), 'candidate.mp4 hash does not match receipt')
    require(sha(source_path) == receipt.get('source_sha256'), 'source video hash does not match the rendered source')
    require(plan_path.is_file() and sha(plan_path) == receipt.get('saved_plan_sha256'), 'saved edit plan is missing or has changed')
    require(timeline_path.is_file(), 'timeline map is missing')
    timeline_sha = sha(timeline_path)
    if receipt.get('timeline_sha256'):
        require(timeline_sha == receipt['timeline_sha256'], 'timeline map has changed')
    timeline = json.loads(timeline_path.read_text())
    require(isinstance(timeline, list) and bool(timeline), 'timeline map must be a non-empty array')
    previous_end = 0.0
    for index, span in enumerate(timeline):
        require(isinstance(span, dict), 'timeline span must be an object')
        fields = ('source_start', 'source_end', 'output_start', 'output_end')
        require(all(finite(span.get(field)) for field in fields), 'timeline span has invalid times')
        require(0 <= span['source_start'] < span['source_end'], 'timeline source range is invalid')
        require(span['output_start'] >= 0 and span['output_start'] < span['output_end'], 'timeline output range is invalid')
        require(abs(span['output_start'] - previous_end) <= 1e-6, 'timeline output ranges are not contiguous')
        previous_end = span['output_end']
    expected = receipt.get('expected_duration')
    require(finite(expected) and abs(previous_end - expected) < 0.001, 'timeline duration does not match receipt')
    require(abs(previous_end - receipt.get('actual_duration', -1)) < 0.10, 'candidate duration does not match timeline')
    return render_dir, source_path, receipt, timeline, timeline_sha


def source_context_at(timeline, output_time):
    require(finite(output_time) and output_time >= 0, 'feedback time must be a non-negative number')
    index = next((i for i, span in enumerate(timeline)
                  if span['output_start'] <= output_time < span['output_end']), None)
    if index is None and abs(output_time - timeline[-1]['output_end']) < 0.001:
        index = len(timeline) - 1
    require(index is not None, 'feedback time falls outside the rendered edit')
    span = timeline[index]
    source_time = min(span['source_end'], span['source_start'] + output_time - span['output_start'])
    return {
        'segment_index': index,
        'source_time_seconds': round(source_time, 3),
        'source_range_seconds': [span['source_start'], span['source_end']],
        'output_range_seconds': [span['output_start'], span['output_end']],
        'segment_reason': span.get('reason', ''),
    }


def review_page(receipt, source_name, timeline_sha):
    seed = json.dumps({
        'version': receipt['version'],
        'output_sha256': receipt['output_sha256'],
        'status': 'unreviewed',
        'comments': [],
    }, ensure_ascii=False).replace('<', '\\u003c').replace('</', '<\\/')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Review your edit</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f2f0e9;color:#19352d;font:18px/1.5 system-ui}main{max-width:1100px;margin:auto;padding:32px}h1{font:52px Georgia;margin:10px 0}.players{display:grid;grid-template-columns:1fr 1fr;gap:24px}video{width:100%;height:440px;background:#111;border-radius:8px}textarea{width:100%;min-height:110px;padding:12px;font:inherit}button,select{font:inherit;padding:12px;border:1px solid #19352d;border-radius:5px;background:white;margin:8px 8px 8px 0}button{cursor:pointer}li{margin:12px 0}.note{font-size:14px}#saved{min-height:24px}@media(max-width:650px){.players{grid-template-columns:1fr}h1{font-size:38px}main{padding:18px}video{height:340px}}</style>
<main><p>PT VIDEO EDITING / REVIEW CANDIDATE</p><h1>Watch it. Tell us what to change.</h1><p>Version <strong>__REVIEW_VERSION__</strong>. Comments refer to the edited video's time.</p><div class="players"><section><h2>Original</h2><video id="source" controls preload="metadata" src="__SOURCE_URL__"></video></section><section><h2>This edit</h2><video id="edit" controls preload="metadata" src="candidate.mp4"></video></section></div>
<p><button id="match">Show this moment in original</button> <span id="time">0:00</span></p><label for="comment">Your feedback at this moment</label><textarea id="comment" placeholder="The title is too close to my face here."></textarea><button id="add">Add timestamped comment</button><ol id="comments"></ol><label for="decision">Your decision</label> <select id="decision"><option value="unreviewed">Still reviewing</option><option value="changes_requested">I'd like changes</option><option value="accepted">I accept this version</option></select><p id="saved" role="status"></p><button id="export">Download feedback for your agent</button><p class="note">Saved in this browser only. Download and give the JSON file to your agent to carry feedback back. Acceptance is not social publication.</p></main>
<script>
const seed=__REVIEW_SEED__;const revision={schema:'pt-video-editing-feedback/v2',version:seed.version,rendered_output:'candidate.mp4',output_sha256:seed.output_sha256,source_sha256:'__SOURCE_HASH__',input_plan_sha256:'__PLAN_HASH__',saved_plan_sha256:'__SAVED_PLAN_HASH__',timeline_sha256:'__TIMELINE_HASH__'};
const key='pt-review:'+seed.output_sha256;let state=seed;try{state=JSON.parse(localStorage.getItem(key))||seed}catch{}
const edit=document.querySelector('#edit'),source=document.querySelector('#source'),comment=document.querySelector('#comment'),decision=document.querySelector('#decision'),saved=document.querySelector('#saved');let mapping=null,timelineError=null;
const fmt=t=>Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
function setStatus(message){saved.textContent=message}
function save(){state.draft=comment.value;try{localStorage.setItem(key,JSON.stringify(state));setStatus('Saved in this browser.')}catch{setStatus('Browser storage unavailable — download feedback before leaving.')}}
function contextAt(t){if(!mapping)throw Error('Timeline map is still loading; wait a moment and export again.');const i=mapping.findIndex(s=>t>=s.output_start&&t<s.output_end);const index=i>=0?i:(Math.abs(t-mapping[mapping.length-1].output_end)<.001?mapping.length-1:-1);if(index<0)throw Error('A comment timestamp is outside the saved edit map.');const s=mapping[index];return{segment_index:index,source_time_seconds:Number(Math.min(s.source_end,s.source_start+t-s.output_start).toFixed(3)),source_range_seconds:[s.source_start,s.source_end],output_range_seconds:[s.output_start,s.output_end],segment_reason:s.reason||''}}
function draw(){const list=document.querySelector('#comments');list.replaceChildren();for(const c of state.comments){const li=document.createElement('li'),b=document.createElement('button');b.textContent=fmt(c.time);b.onclick=()=>edit.currentTime=c.time;li.append(b,document.createTextNode(c.text));list.append(li)}decision.value=state.status}
comment.value=state.draft||'';comment.oninput=save;decision.onchange=()=>{state.status=decision.value;save()};
document.querySelector('#add').onclick=()=>{if(!comment.value.trim())return;state.comments.push({time:Number(edit.currentTime.toFixed(3)),text:comment.value.trim()});comment.value='';save();draw()};
edit.ontimeupdate=()=>document.querySelector('#time').textContent=fmt(edit.currentTime);
document.querySelector('#match').onclick=()=>{try{const t=edit.currentTime,c=contextAt(t);source.currentTime=c.source_time_seconds;source.pause();setStatus('Original positioned at source '+fmt(c.source_time_seconds)+'.')}catch(e){setStatus(e.message)}};
document.querySelector('#export').onclick=()=>{try{if(timelineError)throw Error('Timeline map could not be loaded: '+timelineError);const body={...revision,status:state.status,draft:state.draft||'',comments:state.comments.map(c=>({...c,output_time_seconds:c.time,source_context:contextAt(c.time)})),exported_at:new Date().toISOString()};const url=URL.createObjectURL(new Blob([JSON.stringify(body,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='feedback-'+seed.version+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);setStatus('Feedback export includes this render hash and each comment’s source time.')}catch(e){setStatus(e.message)}};
fetch('timeline.json').then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(x=>{if(!Array.isArray(x)||!x.length)throw Error('empty timeline');mapping=x;setStatus('Timeline map loaded.')} ).catch(e=>{timelineError=e.message;setStatus('Timeline map unavailable; source matching and complete feedback export are disabled.')});draw();
</script></html>'''
    replacements = {
        '__REVIEW_VERSION__': html.escape(str(receipt['version'])),
        '__SOURCE_URL__': quote(source_name),
        '__SOURCE_HASH__': receipt['source_sha256'],
        '__PLAN_HASH__': receipt['input_plan_sha256'],
        '__SAVED_PLAN_HASH__': receipt['saved_plan_sha256'],
        '__TIMELINE_HASH__': timeline_sha,
        '__REVIEW_SEED__': seed,
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    return page


def build_review(render_dir, source_path):
    render_dir, source_path, receipt, timeline, timeline_sha = load_context(render_dir, source_path)
    source_name = f"source-{receipt['source_sha256'][:12]}{source_path.suffix}"
    source_link = render_dir / source_name
    if not source_link.exists():
        try:
            os.link(source_path, source_link)
        except OSError:
            shutil.copy2(source_path, source_link)
    require(sha(source_link) == receipt['source_sha256'], 'review source copy does not match receipt')
    page_path = render_dir / 'review.html'
    page_path.write_text(review_page(receipt, source_name, timeline_sha))
    return page_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('render')
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    print(build_review(args.render, args.source))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
