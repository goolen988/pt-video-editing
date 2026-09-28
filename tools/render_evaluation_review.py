#!/usr/bin/env python3
"""Use skill-creator's own viewer; add inline video playback without replacing its review UI."""
import argparse,base64,json,mimetypes,re,subprocess,sys
from pathlib import Path

def create(creator,workspace,output,benchmark=None,previous=None,inputs_map=None):
    cmd=[sys.executable,str(creator/'eval-viewer/generate_review.py'),str(workspace),'--skill-name','PT Video Editing + PT Connect','--static',str(output)]
    if benchmark:cmd+=['--benchmark',str(benchmark)]
    if previous:cmd+=['--previous-workspace',str(previous)]
    subprocess.run(cmd,check=True)
    page=output.read_text()
    # Standard generator represents MP4 as downloadable binary. Keep download and add a player.
    marker='} else if (file.type === "binary") {'
    add='''} else if (file.type === "binary") {
          if ((file.mime || "").startsWith("video/")) {
            const player = document.createElement("video");
            player.controls = true; player.preload = "metadata";
            player.src = file.data_uri;
            player.style.cssText = "display:block;width:100%;max-height:72vh;background:#111;margin-bottom:12px";
            content.appendChild(player);
          }
'''
    if marker not in page:raise RuntimeError('Viewer template changed; inspect before applying media enhancement')
    parts=page.split(marker)
    if len(parts)!=3:raise RuntimeError('Expected current and previous output renderer branches')
    page=parts[0]+add+parts[1]+add.replace('content.appendChild(player)','fc.appendChild(player)')+parts[2]
    match=re.search(r'const EMBEDDED_DATA = (.*);\n',page)
    if not match:raise RuntimeError('Cannot locate generated viewer data')
    data=json.loads(match.group(1))
    for run in data['runs']:
        for meta_path in workspace.glob('eval-*/eval_metadata.json'):
            if run['id'].startswith(meta_path.parent.name+'-'):
                meta=json.loads(meta_path.read_text());run['eval_id']=meta['eval_id'];run['prompt']=meta['prompt'];break
    if inputs_map:
        for item in json.loads(inputs_map.read_text()):
            asset=Path(item['path']).expanduser()
            uri='data:'+str(mimetypes.guess_type(asset.name)[0] or 'application/octet-stream')+';base64,'+base64.b64encode(asset.read_bytes()).decode()
            for run in data['runs']:
                if run['eval_id']==item['eval_id']:
                    run['outputs'].insert(0,{'name':'INPUT — '+item['label'],'type':'binary','mime':mimetypes.guess_type(asset.name)[0],'data_uri':uri})
    data['runs'].sort(key=lambda r:(r.get('eval_id') or 0,0 if 'with_skill' in r['id'] else 1,r['id']))
    replacement='const EMBEDDED_DATA = '+json.dumps(data,ensure_ascii=True).replace('<',r'\u003c').replace('>',r'\u003e').replace('&',r'\u0026')+';\n'
    page=page[:match.start()]+replacement+page[match.end():]
    # A static HTTP server returns 501 to POST; fetch does not reject HTTP errors.
    # Preserve the official feedback UI, but make its download fallback reliable.
    page=page.replace('}).then(() => {', '}).then(response => { if (!response.ok) throw new Error("Feedback server unavailable");')
    feedback_init='let feedbackMap = {};  // run_id -> feedback text'
    if feedback_init not in page:raise RuntimeError('Viewer feedback initialization changed')
    page=page.replace(feedback_init, 'const feedbackStorageKey = "pt-skill-review:" + location.pathname;\n    let feedbackMap = {};\n    try { feedbackMap = JSON.parse(localStorage.getItem(feedbackStorageKey) || "{}"); } catch (_) {}\n    function persistLocalFeedback() { try { localStorage.setItem(feedbackStorageKey, JSON.stringify(feedbackMap)); } catch (_) {} }')
    page=page.replace('// Build reviews array from map', 'persistLocalFeedback();\n      // Build reviews array from map')
    page=page.replace('// POST once with status: complete', 'persistLocalFeedback();\n      // POST once with status: complete')
    output.write_text(page)
    print(json.dumps({'viewer':str(output),'runs':len(data['runs']),'generator':'skill-creator/eval-viewer/generate_review.py','enhancement':'inline video + revised-first ordering + static feedback persistence/download; official UI retained'}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--creator',type=Path,required=True);p.add_argument('--workspace',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--benchmark',type=Path);p.add_argument('--previous',type=Path);p.add_argument('--inputs-map',type=Path);a=p.parse_args();create(a.creator,a.workspace,a.output,a.benchmark,a.previous,a.inputs_map)
