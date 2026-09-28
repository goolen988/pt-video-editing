// Deterministic JavaScript card animation. Frame time is supplied, never wall-clock driven.
const fs=require('node:fs');const path=require('node:path');const {chromium}=require('playwright');
(async()=>{
 const spec=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const output=path.resolve(process.argv[3]);
 if(fs.existsSync(output))throw Error('Graphics output already exists');fs.mkdirSync(output,{recursive:true});
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
 for(const g of s.captions||[]){if(t<g.start||t>=g.end)continue;let size=s.height*.032;ctx.font=`700 ${size}px sans-serif`;while(ctx.measureText(g.text).width>s.width*.68&&size>8){size--;ctx.font=`700 ${size}px sans-serif`;}ctx.textAlign='center';ctx.textBaseline='bottom';ctx.lineWidth=Math.max(2,s.height*.002);ctx.strokeStyle='#101010';ctx.lineJoin='round';ctx.strokeText(g.text,s.width/2,s.caption_y*s.height);ctx.fillStyle='#ffffff';ctx.fillText(g.text,s.width/2,s.caption_y*s.height);}
 };},spec);
 for(let i=0;i<Math.ceil(spec.duration*spec.fps);i++){await page.evaluate(t=>window.drawFrame(t),i/spec.fps);await page.screenshot({path:path.join(output,String(i).padStart(6,'0')+'.png'),omitBackground:true});}
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
