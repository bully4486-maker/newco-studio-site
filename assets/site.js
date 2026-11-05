(function(){var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');if(!b||!n)return;b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false')});n.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('open');b.setAttribute('aria-expanded','false')}});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&n.classList.contains('open')){n.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus()}})})();
(function(){var c=document.getElementById('chat');if(!c)return;var fab=c.querySelector('.chat-fab'),p=c.querySelector('.chat-panel'),log=c.querySelector('.chat-log'),opts=c.querySelector('.chat-opts'),started=false;
var Q='<a href="#quote" data-close>Open the quote form</a>';
var A={
prices:['How much does it cost?','Fixed prices, agreed in writing first. One-page website £99. Website, spreadsheet or script fixes from £19. Bigger sites get their own fixed quote. Prices as stated. VAT is not charged. '+Q+' for an exact figure.'],
time:['How long does it take?','Small fixes: often a day or two. One-page site: usually a few days. Your quote gives a firm delivery date before you commit.'],
process:['How does it work?','1. Send a short written brief. 2. Get a fixed quote within 24 hours. 3. We build and send a preview. 4. Agreed revisions, then you get every file. '+Q+'.'],
calls:['Can we have a call?','We work in writing only. It keeps a clear record of what was agreed, you reply when it suits you, and small jobs scope faster that way. Every question gets a written answer, usually the same day.'],
what:['What do you build?','Websites and landing pages, Python scripts and automations, Excel and Google Sheets work, HTML/CSS/JS bug fixes and HTML email templates. Have a look at the <a href="standards/" data-close>example sites</a>. Ready-made spreadsheets are on the <a href="spreadsheets/" data-close>Etsy shop page</a>.'],
own:['Who owns the work?','You do. You get the full source files. Your domain and hosting stay in your name; we don\'t sell hosting.'],
pay:['How do I pay?','You get a fixed written quote first. Once you\'re happy, we send an invoice: 50% to start and 50% when you\'ve approved the finished site, paid by UK bank transfer. You only pay the balance once you\'ve signed it off, and everything is handed over to you once it\'s paid. Small fixes (£19) are paid in one go by bank transfer once you\'ve approved the fix. Prices as stated. VAT is not charged. '+Q],
quote:['Get a quote','Great. The guided brief takes a few short steps. You can edit the scope preview before you send it. It is not an automatic price: you get a written fixed quote within 24 hours. '+Q+'.']};
var order=['prices','time','process','calls','what','own','pay','quote'];
function add(t,w){var d=document.createElement('div');d.className='msg '+w;d.innerHTML=t;log.appendChild(d);log.scrollTop=log.scrollHeight}
function menu(){opts.innerHTML='';order.forEach(function(k){var b=document.createElement('button');b.type='button';b.textContent=A[k][0];b.onclick=function(){add(A[k][0],'me');setTimeout(function(){add(A[k][1],'bot')},250)};opts.appendChild(b)})}
function open(o){p.hidden=!o;p.setAttribute('aria-modal',o?'true':'false');fab.setAttribute('aria-expanded',o?'true':'false');if(o){if(!started){started=true;add('Hi! Quick answers about NewCo Studio. Pick a question below, or jump straight to the '+Q.replace('Open the quote form','quote form')+'.','bot');menu()}var f=opts.querySelector('button');f&&f.focus()}}
fab.onclick=function(){open(p.hidden)};c.querySelector('.chat-x').onclick=function(){open(false);fab.focus()};
log.addEventListener('click',function(e){if(e.target.hasAttribute('data-close'))open(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!p.hidden){open(false);fab.focus()}})})();
(function(){var K=['utm_source','utm_medium','utm_campaign','utm_content'],S=null;try{S=window.sessionStorage}catch(e){}
function get(k){try{return S&&S.getItem(k)||''}catch(e){return ''}}function set(k,v){try{S&&S.setItem(k,v)}catch(e){}}
var q=new URLSearchParams(location.search);
K.forEach(function(k){var v=(q.get(k)||'').trim().slice(0,100);if(v)set(k,v)});
if(!get('landing_path'))set('landing_path',location.pathname);
if(!get('referrer')){var r='';try{var u=new URL(document.referrer);if(u.origin!==location.origin)r=u.origin}catch(e){}if(r)set('referrer',r)}
document.querySelectorAll('form.qform').forEach(function(f){
K.concat(['landing_path','referrer']).forEach(function(k){var i=f.querySelector('input[name="'+k+'"]');if(i&&!i.value)i.value=get(k)})})})();
(function(){
function val(f,n){var i=f.querySelector('[name="'+n+'"]');return i&&i.value?String(i.value).trim():''}
function paidSrc(f){var c=val(f,'utm_campaign'),s=val(f,'utm_source'),m=val(f,'utm_medium').toLowerCase(),cl=c.toLowerCase(),sl=s.toLowerCase();
var paid=/^(cpc|ppc|paid|paid_social|paidsocial)$/.test(m)||/^fbad/.test(cl)||/fbad|fbads|meta.?ad/.test(cl)||((/^(facebook|fb|instagram|ig|meta)$/.test(sl))&&(!!c||/^(cpc|ppc|paid|paid_social|paidsocial)$/.test(m)));
if(!paid)return'';return (c||s).slice(0,80).replace(/[^a-zA-Z0-9._-]/g,'')}
function applyRedirect(f){var r=f.querySelector('input[name="redirect"]');if(!r)return;try{var u=new URL(r.value),p=paidSrc(f);if(p)u.searchParams.set('src',p);['utm_source','utm_campaign'].forEach(function(n){var v=val(f,n);if(v)u.searchParams.set(n,v)});r.value=u.toString()}catch(e){}}
document.querySelectorAll('form.qform').forEach(function(f){applyRedirect(f);f.addEventListener('submit',function(){applyRedirect(f)})});
var m=document.querySelector('.mcta');if(!m||!('IntersectionObserver' in window))return;
var forms=document.querySelectorAll('form.qform');if(!forms.length)return;
var vis=[];
forms.forEach(function(f,i){vis[i]=false});
var io=new IntersectionObserver(function(es){es.forEach(function(e){var i=Number(e.target.getAttribute('data-q'));vis[i]=e.isIntersecting});var on=false;vis.forEach(function(v){if(v)on=true});m.classList.toggle('off',on)},{threshold:0.05});
forms.forEach(function(f,i){f.setAttribute('data-q',String(i));io.observe(f)})})();
(function(){
var guides={
'One-page website':'Guide price £99, confirmed in a written quote before any work. That guide includes one mobile-first page, your services, prices, photos and contact details, basic SEO, a favicon, a share image, the revisions named in the quote, and every file. Prices as stated. VAT is not charged. Payment is 50% to start and 50% after you sign off, by UK bank transfer. You own the files.',
'Website fix':'Guide price from £19, confirmed in a written quote before any work. That guide includes the change and a plain-English note of what changed. Prices as stated. VAT is not charged. A fix at this size is paid once, by UK bank transfer, after you approve it. You own the files.',
'Spreadsheet or script':'Priced from £19 when it is a small fix, or as its own fixed quote if it is larger. The figure is confirmed in writing before any work. Prices as stated. VAT is not charged. You own the files.',
'Multi-page website':'No guide price. You will get a fixed written quote for the pages you describe, within 24 hours. Prices as stated. VAT is not charged. Payment for a build is 50% to start and 50% after you sign off, by UK bank transfer. You own the files.'
};
function buildScope(f){
var job=valChecked(f,'job_type')||'Not chosen yet';
var assets=[];
f.querySelectorAll('input[name^="asset_"]:checked').forEach(function(b){assets.push(b.value)});
var deadline=valInput(f,'deadline');
var date=valInput(f,'deadline_date');
var lines=['Job: '+job, guides[job]||'The price is confirmed in a written quote. This preview is not a price.', 'Assets ready: '+(assets.length?assets.join(', '):'not stated'), 'Deadline: '+(deadline||'not stated')+(date?' ('+date+')':''), 'Please send a written fixed quote with the scope, the price and a delivery date. This note is the brief, not a price.'];
return lines.join('\n\n');
}
function valChecked(f,n){var i=f.querySelector('input[name="'+n+'"]:checked');return i?i.value:''}
function valInput(f,n){var i=f.querySelector('[name="'+n+'"]');return i&&i.value?i.value.trim():''}
document.querySelectorAll('form.qform.wizard').forEach(function(f){
var steps=Array.prototype.slice.call(f.querySelectorAll('.wiz-step'));
if(!steps.length)return;
var i=0, msg=f.querySelector('textarea[name="message"]'), dirty=false;
if(msg) msg.addEventListener('input',function(){dirty=true});
function show(n, moveFocus){
i=Math.max(0, Math.min(steps.length-1, n));
steps.forEach(function(s,idx){s.classList.toggle('on', idx===i)});
if(i===steps.length-1) fill(false);
if(moveFocus){var focus=steps[i].querySelector('input,select,textarea'); if(focus) focus.focus()}
}
function fill(force){
if(!msg)return;
if(!force && dirty && msg.value.trim()) return;
msg.value=buildScope(f);
if(force) dirty=false;
}
function stepError(step, text){
var err=step.querySelector('.wiz-error');
if(!err) return;
if(text){err.hidden=false; err.textContent=text} else err.hidden=true;
}
function validate(step){
var boxes=step.querySelectorAll('input[name^="asset_"]');
if(boxes.length){
var any=false; Array.prototype.forEach.call(boxes,function(b){if(b.checked)any=true});
if(!any){stepError(step,'Choose what you already have. “Nothing ready yet” is fine.'); boxes[0].focus(); return false}
stepError(step,'');
}
var fields=step.querySelectorAll('input,select,textarea');
for(var k=0;k<fields.length;k++){
if(!fields[k].checkValidity()){fields[k].reportValidity(); return false}
}
return true;
}
f.addEventListener('click',function(e){
var next=e.target.closest&&e.target.closest('.wiz-next');
var back=e.target.closest&&e.target.closest('.wiz-back');
var refresh=e.target.closest&&e.target.closest('.wiz-refresh');
if(next){e.preventDefault(); if(validate(steps[i])) show(i+1,true)}
else if(back){e.preventDefault(); show(i-1,true)}
else if(refresh){e.preventDefault(); fill(true); if(msg) msg.focus()}
});
f.addEventListener('change',function(e){
var t=e.target;
if(!t.name||t.name.indexOf('asset_')!==0) return;
if(t.name==='asset_none'&&t.checked){f.querySelectorAll('input[name^="asset_"]').forEach(function(b){if(b!==t)b.checked=false})}
else if(t.checked){var n=f.querySelector('input[name="asset_none"]'); if(n) n.checked=false}
});
f.classList.add('is-ready');
show(0,false);
});
document.querySelectorAll('form.qform').forEach(function(f){
var email=f.querySelector('input[name="email"]');
var phone=f.querySelector('input[name="phone"]');
if(email&&phone){
function sync(){
var ok=!!(email.value.trim()||phone.value.trim());
email.setCustomValidity(ok?'':'Enter an email address or a phone number. One is enough.');
}
email.addEventListener('input',sync);
phone.addEventListener('input',sync);
f.addEventListener('submit',function(e){
email.value=email.value.trim();
phone.value=phone.value.trim();
sync();
if(!email.checkValidity()){e.preventDefault(); email.reportValidity()}
});
}
var file=f.querySelector('input[type="file"]');
var sum=f.querySelector('input[name="fix_summary"]');
f.addEventListener('submit',function(e){
if(file){
var tooBig=file.files&&file.files[0]&&file.files[0].size>4*1024*1024;
file.setCustomValidity(tooBig?'That screenshot is over 4 MB. Please use a smaller image.':'');
if(tooBig){e.preventDefault(); file.reportValidity(); return}
}
if(sum){
var urlEl=f.querySelector('[name="page_url"]');
var whereEl=f.querySelector('[name="where_it_breaks"]');
var vpEl=f.querySelector('[name="viewport_notes"]');
var shot=file&&file.files&&file.files[0]?file.files[0].name:'(none)';
sum.value=['Fix ticket','Page: '+((urlEl&&urlEl.value.trim())||'(none)'),'Where it breaks: '+((whereEl&&whereEl.value)||''),'Viewport notes: '+((vpEl&&vpEl.value.trim())||'(none)'),'Screenshot: '+shot].join('\n');
}
});
})})();
(function(){
var ID='1727286912311143', loading=false, ready=false, waiters=[];
function stub(){
if(window.fbq) return;
var n=window.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!window._fbq) window._fbq=n; n.push=n; n.loaded=!0; n.version='2.0'; n.queue=[];
}
function markOn(){
document.querySelectorAll('[data-pixel-consent]').forEach(function(b){b.setAttribute('aria-pressed','true'); b.textContent='Facebook measurement is on'})
}
function loadPixel(){
if(ready){markOn(); return}
waiters.push(markOn);
if(loading) return;
loading=true;
stub();
var s=document.createElement('script');
s.async=true;
s.src='https://connect.facebook.net/en_US/fbevents.js';
s.onload=function(){
ready=true;
window.fbq('init', ID);
window.fbq('track','PageView');
var extra=(document.body.getAttribute('data-fbq')||'').split(',');
extra.forEach(function(ev){ev=ev.trim(); if(ev) window.fbq('track', ev)});
waiters.forEach(function(fn){try{fn()}catch(e){}});
waiters=[];
};
document.head.appendChild(s);
}
var armed=false;
function arm(){if(armed)return; armed=true; loadPixel()}
['pointerdown','keydown','touchstart'].forEach(function(ev){window.addEventListener(ev, arm, {capture:true, passive:true})});
document.addEventListener('click',function(e){
var t=e.target.closest&&e.target.closest('[data-pixel-consent]');
if(!t) return;
e.preventDefault();
try{localStorage.setItem('ncs_pixel','1')}catch(err){}
arm();
});
try{if(localStorage.getItem('ncs_pixel')==='1') arm()}catch(err){}
if(document.body.hasAttribute('data-fbq-idle')){
var go=function(){arm()};
if(window.requestIdleCallback) requestIdleCallback(go,{timeout:2000});
else window.addEventListener('load',function(){setTimeout(go,400)});
}
})();
