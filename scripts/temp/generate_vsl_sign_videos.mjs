import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const outDir = path.join(root, "apps", "web_next", "public", "signs");
const require = createRequire(path.join(root, "apps", "web_next", "package.json"));
const { chromium } = require("@playwright/test");

const clips = [
  ["dau", "ĐAU", "hand-to-chest"],
  ["dau_dau", "ĐAU ĐẦU", "hand-to-head"],
  ["bung", "BỤNG", "hand-to-belly"],
  ["sot", "SỐT", "temp"],
  ["ho", "HO", "cough"],
  ["kho_tho", "KHÓ THỞ", "breath"],
  ["chong_mat", "CHÓNG MẶT", "dizzy"],
  ["thuoc", "THUỐC", "pill"],
  ["bac_si", "BÁC SĨ", "doctor"],
  ["khan_cap", "KHẨN CẤP", "alert"],
  ["nghi_ngoi", "NGHỈ NGƠI", "rest"],
  ["uong_nuoc", "UỐNG NƯỚC", "drink"],
  ["di_kham", "ĐI KHÁM", "doctor"],
  ["theo_doi", "THEO DÕI", "watch"],
];

const pageHtml = `<!doctype html>
<html><body style="margin:0;background:#07111f">
<canvas id="c" width="640" height="360"></canvas>
<script>
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
function ease(t){ return 0.5 - Math.cos(Math.PI * t) / 2; }
function drawHand(x,y,scale,rot,color){
  ctx.save(); ctx.translate(x,y); ctx.rotate(rot); ctx.scale(scale,scale);
  ctx.strokeStyle=color; ctx.fillStyle=color; ctx.lineWidth=12; ctx.lineCap="round"; ctx.lineJoin="round";
  ctx.beginPath(); ctx.arc(0,0,24,0,Math.PI*2); ctx.fill();
  for(let i=-2;i<=2;i++){
    ctx.beginPath(); ctx.moveTo(i*14,-18); ctx.lineTo(i*18,-82-Math.abs(i)*8); ctx.stroke();
    ctx.beginPath(); ctx.arc(i*18,-82-Math.abs(i)*8,8,0,Math.PI*2); ctx.fill();
  }
  ctx.beginPath(); ctx.moveTo(-30,4); ctx.lineTo(-70,-42); ctx.stroke();
  ctx.restore();
}
function label(text){
  ctx.fillStyle="rgba(255,255,255,.96)"; ctx.font="800 34px Arial"; ctx.textAlign="center"; ctx.fillText(text,320,320);
}
function body(){
  ctx.strokeStyle="rgba(196,181,253,.45)"; ctx.fillStyle="rgba(124,58,237,.08)"; ctx.lineWidth=6;
  ctx.beginPath(); ctx.arc(320,82,32,0,Math.PI*2); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(320,118); ctx.lineTo(320,228); ctx.moveTo(246,150); ctx.lineTo(394,150); ctx.moveTo(320,228); ctx.lineTo(270,292); ctx.moveTo(320,228); ctx.lineTo(370,292); ctx.stroke();
}
function icon(kind,t){
  const p=ease(Math.sin(t*Math.PI));
  body();
  let x=420,y=170,rot=-.4;
  if(kind==="hand-to-head"){ x=390-30*p; y=190-110*p; rot=-.8; }
  if(kind==="hand-to-belly"){ x=390-45*p; y=170+72*p; rot=-.2; }
  if(kind==="hand-to-chest"){ x=420-75*p; y=170+20*p; rot=-.6; }
  if(kind==="cough"){ x=430-80*p; y=190-75*p; rot=-.9; }
  if(kind==="breath"){ x=255+130*p; y=170; rot=.35; }
  if(kind==="temp"){ x=420-80*p; y=215-120*p; rot=-.9; }
  if(kind==="dizzy"){ x=320+Math.sin(t*14)*80; y=170+Math.cos(t*10)*30; rot=t*4; }
  if(kind==="pill"){ x=275+90*p; y=205-56*p; rot=.6; }
  if(kind==="doctor"){ x=245+150*p; y=210-65*p; rot=-.15; }
  if(kind==="alert"){ x=240+160*Math.abs(Math.sin(t*6)); y=174; rot=Math.sin(t*12)*.7; }
  if(kind==="rest"){ x=440-150*p; y=175+50*p; rot=-1.2; }
  if(kind==="drink"){ x=420-90*p; y=230-130*p; rot=-1.1; }
  if(kind==="watch"){ x=250+140*p; y=145+70*Math.sin(t*Math.PI*2); rot=.1; }
  drawHand(x,y,1.0,rot,"#5eead4");
}
window.recordClip = async ({text, kind}) => {
  const stream = canvas.captureStream(30);
  const rec = new MediaRecorder(stream, { mimeType: "video/webm;codecs=vp9" });
  const chunks = [];
  rec.ondataavailable = e => chunks.push(e.data);
  rec.start();
  const start = performance.now();
  await new Promise(resolve => {
    function frame(now){
      const elapsed = now - start;
      const t = Math.min(elapsed / 1350, 1);
      const g = ctx.createLinearGradient(0,0,640,360);
      g.addColorStop(0,"#07111f"); g.addColorStop(1,"#13233b");
      ctx.fillStyle=g; ctx.fillRect(0,0,640,360);
      ctx.fillStyle="rgba(94,234,212,.08)"; ctx.beginPath(); ctx.arc(320,180,130+Math.sin(t*8)*8,0,Math.PI*2); ctx.fill();
      icon(kind,t); label(text);
      if(elapsed < 1350) requestAnimationFrame(frame); else resolve();
    }
    requestAnimationFrame(frame);
  });
  rec.stop();
  await new Promise(resolve => rec.onstop = resolve);
  const blob = new Blob(chunks, { type: "video/webm" });
  const array = new Uint8Array(await blob.arrayBuffer());
  let binary = "";
  for (let i = 0; i < array.length; i++) binary += String.fromCharCode(array[i]);
  return btoa(binary);
};
</script></body></html>`;

await mkdir(outDir, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 640, height: 360 } });
await page.setContent(pageHtml);
for (const [token, text, kind] of clips) {
  const base64 = await page.evaluate(({ text, kind }) => window.recordClip({ text, kind }), { text, kind });
  await writeFile(path.join(outDir, `${token}.webm`), Buffer.from(base64, "base64"));
  console.log(`wrote ${token}.webm`);
}
await browser.close();
