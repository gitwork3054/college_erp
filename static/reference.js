// Apply the requested medium typography once, then honor later Settings changes.
try{if(localStorage.getItem('erpCompactVersion')!=='20261007'){localStorage.setItem('erpFontWeight','medium');localStorage.setItem('erpFontSize','medium');localStorage.setItem('erpCompactVersion','20261007');document.getElementById('font-weight').value='medium';document.getElementById('font-size').value='medium';applyDisplayPreferences()}}catch(e){}
// Reference dashboard enhancements. Existing ERP actions remain in app.js.
const themeChoice=document.getElementById('theme-choice');
function setDashboardTheme(theme){document.documentElement.dataset.theme=theme;if(themeChoice)themeChoice.value=theme;try{localStorage.setItem('erpTheme',theme)}catch(e){}document.querySelectorAll('[data-dashboard-theme]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.dashboardTheme===theme)))}
setDashboardTheme(document.documentElement.dataset.theme||'light');themeChoice?.addEventListener('change',()=>setDashboardTheme(themeChoice.value));document.querySelectorAll('[data-dashboard-theme]').forEach(button=>button.onclick=()=>setDashboardTheme(button.dataset.dashboardTheme));
const profileToggle=document.getElementById('profile-toggle'),profileMenu=document.getElementById('profile-menu');function closeProfile(){profileMenu.hidden=true;profileToggle.setAttribute('aria-expanded','false')}profileToggle.onclick=()=>{profileMenu.hidden=!profileMenu.hidden;profileToggle.setAttribute('aria-expanded',String(!profileMenu.hidden))};document.addEventListener('click',e=>{if(!e.target.closest('.profile-wrap'))closeProfile()});profileMenu.querySelector('[data-page]').addEventListener('click',closeProfile);
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeProfile();document.querySelectorAll('.modal.open').forEach(modal=>closeModal(modal.id))}});
const searchBox=document.getElementById('module-search'),moduleQuery=document.getElementById('module-query'),moduleResults=document.getElementById('module-results');
function renderModules(){const query=moduleQuery.value.trim().toLowerCase();moduleResults.replaceChildren();const seen=new Set();document.querySelectorAll('.sidebar button[data-page]').forEach(nav=>{const label=nav.getAttribute('title'),id=nav.dataset.page;if(seen.has(id)||!label.toLowerCase().includes(query))return;seen.add(id);const button=document.createElement('button');button.textContent=label;button.onclick=()=>{showPage(id);searchBox.hidden=true};moduleResults.append(button)});if(!moduleResults.children.length)moduleResults.textContent='No matching workspace.'}
document.getElementById('open-search').onclick=()=>{searchBox.hidden=!searchBox.hidden;if(!searchBox.hidden){renderModules();moduleQuery.focus()}};moduleQuery.oninput=renderModules;
document.addEventListener('keydown',e=>{if(e.key==='Escape')searchBox.hidden=true;if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();document.getElementById('open-search').click()}});
document.addEventListener('click',e=>{if(!searchBox.contains(e.target)&&!e.target.closest('#open-search'))searchBox.hidden=true});
// Give keyboard users the same record preview as pointer users.
document.querySelectorAll('.record-row,.pio-row,.department-card').forEach(row=>{row.tabIndex=0;row.setAttribute('role','button');row.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();row.click()}})});
// Keep keyboard focus inside an open record dialog until it is closed.
document.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const modal=document.querySelector('.modal.open');if(!modal)return;const focusable=[...modal.querySelectorAll('button,input,select,textarea,a[href]')].filter(el=>!el.disabled&&el.offsetParent!==null);if(!focusable.length)return;const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}});

// Home-only enhancements; all module buttons retain the existing navigation.
(() => {
 const home=document.getElementById('overview'),greeting=document.getElementById('home-greeting'),date=document.getElementById('home-date'),toggle=document.getElementById('home-motion-toggle');
 if(!home||!greeting||!toggle)return;
 const locale=document.documentElement.lang||'en';
 const dateFormat=new Intl.DateTimeFormat(locale,{weekday:'short',day:'numeric',month:'short'});
 const timeFormat=new Intl.DateTimeFormat(locale,{hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:true});
 function updateHomeClock(){
   const now=new Date(),hour=now.getHours();
   greeting.textContent=`${hour<12?'Good morning':hour<17?'Good afternoon':'Good evening'}, ${greeting.dataset.name}.`;
   if(date){date.textContent=`${dateFormat.format(now)} · ${timeFormat.format(now)}`;date.dateTime=now.toISOString();date.title='Your local time · '+timeFormat.resolvedOptions().timeZone}
 }
 updateHomeClock();setInterval(()=>{if(!document.hidden)updateHomeClock()},1000);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateHomeClock()});
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');let paused=false;try{paused=localStorage.getItem('erpHomeMotion')==='paused'}catch(e){}
 function applyMotion(){const off=paused||reduced.matches;home.dataset.motion=off?'paused':'active';toggle.textContent=reduced.matches?'Motion reduced':paused?'Resume motion':'Pause motion';toggle.setAttribute('aria-pressed',String(off));toggle.setAttribute('aria-label',reduced.matches?'Motion reduced by system preference':paused?'Resume dashboard animations':'Pause dashboard animations');toggle.title=toggle.getAttribute('aria-label');toggle.disabled=reduced.matches}
 applyMotion();reduced.addEventListener?.('change',applyMotion);toggle.addEventListener('click',()=>{paused=!paused;try{localStorage.setItem('erpHomeMotion',paused?'paused':'active')}catch(e){}applyMotion()});
 if(matchMedia('(hover: hover) and (pointer: fine)').matches){home.querySelectorAll('.campus-tile').forEach(tile=>{tile.addEventListener('pointermove',event=>{if(paused||reduced.matches)return;const bounds=tile.getBoundingClientRect();tile.style.setProperty('--spot-x',`${Math.round(event.clientX-bounds.left)}px`);tile.style.setProperty('--spot-y',`${Math.round(event.clientY-bounds.top)}px`)});tile.addEventListener('pointerleave',()=>{tile.style.removeProperty('--spot-x');tile.style.removeProperty('--spot-y')})})}
})();
