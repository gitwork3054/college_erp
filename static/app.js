const pages = document.querySelectorAll('.page');
const navs = document.querySelectorAll('[data-page]');
const titles = {overview:['Dashboard','Overview of college operations and recent activity.'],complaints:['Complaints','Track and manage department complaints.'],inventory:['Inventory Requests','Manage departmental inventory requests.'],reports:['Reports','Review operational summaries and performance.'],departments:['Departments','College-wide department overview.']};

function showPage(id){
  pages.forEach(p=>p.classList.toggle('active-page',p.id===id));
  document.querySelectorAll('.nav').forEach(n=>n.classList.toggle('active',n.dataset.page===id));
  const t=titles[id]||titles.overview;
  document.getElementById('page-title').textContent=t[0];
  document.getElementById('page-subtitle').textContent=t[1];
  window.scrollTo({top:0,behavior:'smooth'});
}
navs.forEach(n=>n.addEventListener('click',()=>showPage(n.dataset.page)));
function updateClock(){document.getElementById('clock').textContent=new Intl.DateTimeFormat('en-IN',{dateStyle:'medium',timeStyle:'short'}).format(new Date())}
updateClock();setInterval(updateClock,30000);
function openModal(id){document.getElementById(id).classList.add('open')}
function closeModal(id){document.getElementById(id).classList.remove('open')}
function demoSubmit(e,message){e.preventDefault();closeModal(e.target.closest('.modal').id);e.target.reset();const t=document.getElementById('toast');t.textContent=message;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2600)}
window.addEventListener('click',e=>{if(e.target.classList.contains('modal'))e.target.classList.remove('open')});
