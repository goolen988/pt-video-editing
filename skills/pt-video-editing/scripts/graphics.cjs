// Deterministic JavaScript card animation. Frame time is supplied, never wall-clock driven.
const fs=require('node:fs');const path=require('node:path');const {chromium}=require('playwright');
(async()=>{
 const spec=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const output=path.resolve(process.argv[3]);
 if(fs.existsSync(output))throw Error('Graphics output already exists');fs.mkdirSync(output,{recursive:true});
 const safe=spec.safe_rect||[0,0,1,1];
 if(!Array.isArray(safe)||safe.length!==4||safe.some(v=>!Number.isFinite(v))||safe[0]<0||safe[1]<0||safe[2]<=0||safe[3]<=0||safe[0]+safe[2]>1||safe[1]+safe[3]>1)throw Error('Invalid safe rectangle');
 const browser=await chromium.launch({headless:true});
 try{
 const page=await browser.newPage({viewport:{width:spec.width,height:spec.height},deviceScaleFactor:1});
 await page.setContent('<html><body style="margin:0;background:transparent"><canvas></canvas></body></html>');
 await page.evaluate(s=>{
 const canvas=document.querySelector('canvas');canvas.width=s.width;canvas.height=s.height;const ctx=canvas.getContext('2d');
 window.drawFrame=t=>{ctx.clearRect(0,0,s.width,s.height);
 for(const c of s.cards){if(t<c.start||t>=c.end)continue;
 const ease=1-Math.pow(1-Math.min(1,(t-c.start)/.25),3);const alpha=Math.min(ease,Math.max(0,(c.end-t)/.18));
 const x=c.x*s.width,y=c.y*s.height,w=c.w*s.width,h=c.h*s.height;
 ctx.save();ctx.globalAlpha=alpha;ctx.translate(x,y);ctx.fillStyle='#173d34';ctx.beginPath();ctx.roundRect(0,0,w,h,Math.min(18,h*.15));ctx.fill();
 ctx.fillStyle='#bcf078';ctx.fillRect(0,0,Math.max(1,w*ease),4);
 let size=Math.min(s.height*.042,h*.36),lines=[];
 const wrap=()=>{ctx.font=`700 ${size}px sans-serif`;lines=[];let line='';for(const word of c.text.split(/\s+/)){const next=line?line+' '+word:word;if(ctx.measureText(next).width>w*.88&&line){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);};
 wrap();while(size>8&&(lines.length*size*1.15>h*.82||lines.some(l=>ctx.measureText(l).width>w*.88))){size-=1;wrap();}
 if(lines.length*size*1.15>h*.82||lines.some(l=>ctx.measureText(l).width>w*.88))throw Error('Card text cannot fit; shorten it');
 ctx.fillStyle='#ffffff';ctx.textAlign='center';ctx.textBaseline='middle';lines.forEach((line,i)=>ctx.fillText(line,w/2,h/2+(i-(lines.length-1)/2)*size*1.15));ctx.restore();}
 for(const g of s.captions||[]){if(t<g.start||t>=g.end)continue;
 const rect=s.safe_rect||[0,0,1,1];const left=rect[0]*s.width,right=(rect[0]+rect[2])*s.width,top=rect[1]*s.height,bottom=(rect[1]+rect[3])*s.height;
 const baseline=s.caption_y*s.height,maxWidth=(right-left)*.88;let size=s.height*.032;ctx.textBaseline='bottom';
 const fits=()=>{ctx.font=`700 ${size}px sans-serif`;const m=ctx.measureText(g.text);return m.width<=maxWidth&&baseline-m.actualBoundingBoxAscent-s.height*.002>=top&&baseline+m.actualBoundingBoxDescent+s.height*.002<=bottom;};
 while(size>8&&!fits())size--;
 if(!fits())throw Error('Caption text cannot fit inside safe margins; shorten the caption');
 ctx.textAlign='center';ctx.lineWidth=Math.max(2,s.height*.002);ctx.strokeStyle='#101010';ctx.lineJoin='round';ctx.strokeText(g.text,s.width/2,baseline);ctx.fillStyle='#ffffff';ctx.fillText(g.text,s.width/2,baseline);}
 };},spec);
 for(let i=0;i<Math.ceil(spec.duration*spec.fps);i++){await page.evaluate(t=>window.drawFrame(t),i/spec.fps);await page.screenshot({path:path.join(output,String(i).padStart(6,'0')+'.png'),omitBackground:true});}
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
