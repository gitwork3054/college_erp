(()=>{const intro=document.getElementById('erp-intro');if(!intro)return;const main=document.querySelector('.login-shell');let seen=false;try{seen=sessionStorage.getItem('erpBlueIntroPlayed')==='1'}catch(e){}
if(seen){intro.remove();return}if(main)main.inert=true;
let finished=false;function finish(){if(finished)return;finished=true;const skipHadFocus=intro.contains(document.activeElement);try{sessionStorage.setItem('erpBlueIntroPlayed','1')}catch(e){}intro.classList.add('dismissed');if(main)main.inert=false;if(skipHadFocus)document.getElementById('username')?.focus();setTimeout(()=>intro.remove(),550)}
intro.querySelector('button').addEventListener('click',finish);document.addEventListener('keydown',e=>{if(e.key==='Escape')finish()});const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;setTimeout(finish,reduced?300:2800);
})();
