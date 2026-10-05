/* College ERP · premium experience layer (theme, splash, effects). Independent of app.js logic. */
(()=>{
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches,root=document.documentElement;
const P={grid:'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
alert:'<path d="M12 3 2.5 20h19z"/><path d="M12 10v4M12 17.5v.01"/>',box:'<path d="m3 7 9-4 9 4-9 4z"/><path d="M3 7v10l9 4 9-4V7M12 11v10"/>',
bell:'<path d="M6 9a6 6 0 1 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9z"/><path d="M10 20a2 2 0 0 0 4 0"/>',chart:'<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
building:'<path d="M4 21V8l8-5 8 5v13M9 21v-6h6v6M4 21h16"/>',gear:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9 7 7M17 17l2.1 2.1M19.1 4.9 17 7M7 17l-2.1 2.1"/>',
archive:'<rect x="3" y="4" width="18" height="5" rx="1.5"/><path d="M5 9v10h14V9M10 13h4"/>',out:'<path d="M9 4H5v16h4M16 8l4 4-4 4M20 12H9"/>',
file:'<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',check:'<path d="m4 12.5 5 5L20 6.5"/>',
search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M19 5l-1.5 1.5M6.5 17.5 5 19"/>',
moon:'<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/>',plus:'<path d="M12 5v14M5 12h14"/>'};
const svg=n=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${P[n]||''}</svg>`;
const paint=()=>$$('[data-ico]').forEach(e=>{e.innerHTML=svg(e.dataset.ico)});

/* Theme (dark / light) with circular reveal */
function setTheme(m){root.dataset.theme=m;try{localStorage.setItem('erpTheme',m)}catch(e){}
 $$('#theme-toggle').forEach(b=>{b.innerHTML=svg(m==='dark'?'sun':'moon');b.title=m==='dark'?'Switch to light mode':'Switch to dark mode'})}
function flip(e){const m=root.dataset.theme==='light'?'dark':'light';
 if(!document.startViewTransition||reduce)return setTheme(m);
 root.style.setProperty('--tx',(e?.clientX??innerWidth/2)+'px');root.style.setProperty('--ty',(e?.clientY??30)+'px');
 document.startViewTransition(()=>setTheme(m))}
paint();setTheme(root.dataset.theme||'dark');$$('#theme-toggle').forEach(b=>b.addEventListener('click',flip));

/* Splash: play once per browser session; click to skip */
const sp=$('#splash');if(sp){try{sessionStorage.setItem('erpSplash','1')}catch(e){}
 sp.addEventListener('click',()=>root.classList.add('nosplash'));setTimeout(()=>sp.remove(),4400)}

/* Button ripple */
document.addEventListener('pointerdown',e=>{const b=e.target.closest?.('.primary,.secondary,.danger');if(!b||reduce)return;
 const r=b.getBoundingClientRect(),s=Math.max(r.width,r.height)/4,d=document.createElement('span');d.className='ripple';
 d.style.cssText=`width:${s*2}px;height:${s*2}px;left:${e.clientX-r.left-s}px;top:${e.clientY-r.top-s}px`;b.appendChild(d);setTimeout(()=>d.remove(),650)});

/* Cursor spotlight + 3D tilt */
const GL='.stat-card,.department-card,.report-grid article,.panel,.login-card',TL='.stat-card,.department-card';
document.addEventListener('pointermove',e=>{const c=e.target.closest?.(GL);if(!c)return;const r=c.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top;
 c.style.setProperty('--mx',x+'px');c.style.setProperty('--my',y+'px');
 if(!reduce&&c.matches(TL))c.style.transform=`perspective(800px) rotateX(${(y/r.height-.5)*-9}deg) rotateY(${(x/r.width-.5)*9}deg) translateY(-4px)`});
document.addEventListener('pointerout',e=>{const c=e.target.closest?.(TL);if(c&&!c.contains(e.relatedTarget))c.style.transform=''});

/* Count-up numbers */
if(!reduce)$$('.stat-card strong,.report-grid article>strong').forEach(el=>{const m=el.textContent.trim().match(/^(\d+)(%?)$/);if(!m)return;
 const to=+m[1],s=m[2],t0=performance.now();el.textContent='0'+s;
 const f=n=>{const p=Math.min(1,Math.max(0,(n-t0-250)/1200));el.textContent=Math.round(to*(1-(1-p)**3))+s;if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)});

/* Login: constellation canvas */
const cv=$('#fx');if(cv&&!reduce){const x=cv.getContext('2d');let w,h,pts=[],mx=-999,my=-999;
 const size=()=>{w=cv.width=cv.offsetWidth;h=cv.height=cv.offsetHeight;pts=Array.from({length:Math.round(w*h/16000)},()=>({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35}))};
 size();addEventListener('resize',size);cv.parentElement.addEventListener('pointermove',e=>{const r=cv.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top});
 (function loop(){x.clearRect(0,0,w,h);for(const p of pts){p.x=(p.x+p.vx+w)%w;p.y=(p.y+p.vy+h)%h;x.fillStyle='rgba(243,223,178,.8)';x.beginPath();x.arc(p.x,p.y,1.3,0,7);x.fill()}
  for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){const a=pts[i],b=pts[j],d=Math.hypot(a.x-b.x,a.y-b.y);if(d<120){x.strokeStyle=`rgba(255,77,109,${.28*(1-d/120)})`;x.beginPath();x.moveTo(a.x,a.y);x.lineTo(b.x,b.y);x.stroke()}}
  for(const p of pts){const d=Math.hypot(p.x-mx,p.y-my);if(d<170){x.strokeStyle=`rgba(243,223,178,${.5*(1-d/170)})`;x.beginPath();x.moveTo(p.x,p.y);x.lineTo(mx,my);x.stroke()}}
  requestAnimationFrame(loop)})()}

/* Login: demo account chips */
$$('.chip').forEach(c=>c.addEventListener('click',()=>{$('#username').value=c.dataset.u;$('#password').value='1234';$('#password').focus()}));

/* Quick "Download" buttons -> open Reports with the right dataset selected */
document.addEventListener('click',e=>{const b=e.target.closest('.dl-jump');if(!b||typeof showPage!=='function')return;
 showPage('reports');const ds=$('#download-dataset');if(ds){ds.value=b.dataset.dataset}
 setTimeout(()=>{const box=$('.download-box');if(box){box.scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'});box.classList.remove('flash');void box.offsetWidth;box.classList.add('flash')}},250)});

/* Command palette (Ctrl/Cmd + K) */
const ck=$('#cmdk');if(ck){const inp=$('#cmdk-input'),list=$('#cmdk-list');let items=[],sel=0;
 const all=()=>[...$$('.sidebar .nav').map(n=>({l:n.querySelector('b').textContent,i:n.querySelector('[data-ico]')?.dataset.ico,run:()=>n.click()})),
  ...$$('[onclick*="-modal"]').filter(b=>b.classList.contains('primary')).map(b=>({l:b.textContent.trim(),i:'plus',run:()=>b.click()})),
  {l:root.dataset.theme==='dark'?'Switch to light mode':'Switch to dark mode',i:root.dataset.theme==='dark'?'sun':'moon',run:()=>flip()}];
 const draw=()=>{list.innerHTML=items.map((o,k)=>`<div class="cmdk-item ${k===sel?'sel':''}" data-k="${k}"><span class="ico">${svg(o.i)}</span>${o.l}</div>`).join('')||'<div class="empty-state">No results</div>'};
 const open=()=>{ck.classList.add('open');inp.value='';items=all();sel=0;draw();inp.focus()},close=()=>ck.classList.remove('open');
 const go=k=>{const o=items[k];if(o){close();o.run()}};
 inp.addEventListener('input',()=>{items=all().filter(o=>o.l.toLowerCase().includes(inp.value.toLowerCase()));sel=0;draw()});
 list.addEventListener('click',e=>{const r=e.target.closest('.cmdk-item');if(r)go(+r.dataset.k)});
 ck.addEventListener('click',e=>{if(e.target===ck)close()});$('#cmd-open')?.addEventListener('click',open);
 addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();ck.classList.contains('open')?close():open()}
  else if(ck.classList.contains('open')){if(e.key==='Escape')close();else if(e.key==='ArrowDown'){e.preventDefault();sel=Math.min(items.length-1,sel+1);draw()}else if(e.key==='ArrowUp'){e.preventDefault();sel=Math.max(0,sel-1);draw()}else if(e.key==='Enter')go(sel)}})}
})();
