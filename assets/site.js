(function(){var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');if(!b||!n)return;b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o)});n.addEventListener('click',function(e){if(e.target.tagName==='A'){n.classList.remove('open');b.setAttribute('aria-expanded','false')}});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&n.classList.contains('open')){n.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus()}})})();
(function(){var c=document.getElementById('chat');if(!c)return;var fab=c.querySelector('.chat-fab'),p=c.querySelector('.chat-panel'),log=c.querySelector('.chat-log'),opts=c.querySelector('.chat-opts'),started=false;
var Q='<a href="#quote" data-close>Open the quote form</a>';
var A={
prices:['How much does it cost?','Fixed prices, agreed in writing first. One-page website £99. Website, spreadsheet or script fixes from £19. Bigger sites get their own fixed quote. Those are totals. '+Q+' for an exact figure.'],
time:['How long does it take?','Small fixes: often a day or two. One-page site: usually a few days. Your quote gives a firm delivery date before you commit.'],
process:['How does it work?','1. Send a short written brief. 2. Get a fixed quote within 24 hours. 3. We build and send a preview. 4. Agreed revisions, then you get every file. '+Q+'.'],
calls:['Can we have a call?','We work in writing only. It keeps a clear record of what was agreed, you reply when it suits you, and small jobs scope faster that way. Every question gets a written answer, usually the same day.'],
what:['What do you build?','Websites and landing pages, Python scripts and automations, Excel and Google Sheets work, HTML/CSS/JS bug fixes and HTML email templates. Have a look at the <a href="#work" data-close>example sites</a>.'],
own:['Who owns the work?','You do. You get the full source files. Your domain and hosting stay in your name; we don\'t sell hosting.'],
pay:['How do I pay?','You get a fixed written quote first. Once you\'re happy, we send an invoice: 50% to start and 50% when you\'ve approved the finished site, paid by UK bank transfer. You only pay the balance once you\'ve signed it off, and everything is handed over to you once it\'s paid. Small fixes (£19) are paid in one go by bank transfer once you\'ve approved the fix. '+Q],
quote:['Get a quote','Great. The form takes about two minutes and you\'ll get a written fixed quote within 24 hours. '+Q+'.']};
var order=['prices','time','process','calls','what','own','pay','quote'];
function add(t,w){var d=document.createElement('div');d.className='msg '+w;d.innerHTML=t;log.appendChild(d);log.scrollTop=log.scrollHeight}
function menu(){opts.innerHTML='';order.forEach(function(k){var b=document.createElement('button');b.type='button';b.textContent=A[k][0];b.onclick=function(){add(A[k][0],'me');setTimeout(function(){add(A[k][1],'bot')},250)};opts.appendChild(b)})}
function open(o){p.hidden=!o;p.setAttribute('aria-modal',o?'true':'false');fab.setAttribute('aria-expanded',o?'true':'false');if(o){if(!started){started=true;add('Hi! Quick answers about NewCo Studio. Pick a question below, or jump straight to the '+Q.replace('Open the quote form','quote form')+'.','bot');menu()}var f=opts.querySelector('button');f&&f.focus()}}
fab.onclick=function(){open(p.hidden)};c.querySelector('.chat-x').onclick=function(){open(false);fab.focus()};
log.addEventListener('click',function(e){if(e.target.hasAttribute('data-close'))open(false)});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!p.hidden){open(false);fab.focus()}})})();
(function(){var K=['utm_source','utm_medium','utm_campaign','utm_content'],S=null;try{S=window.sessionStorage}catch(e){}
function get(k){try{return S&&S.getItem(k)||''}catch(e){return ''}}function set(k,v){try{S&&S.setItem(k,v)}catch(e){}}
var q=new URLSearchParams(location.search),fresh=false;
K.forEach(function(k){var v=(q.get(k)||'').trim().slice(0,100);if(v){set(k,v);fresh=true}});
if(!get('landing_path'))set('landing_path',location.pathname);
if(!get('referrer')){var r='';try{var u=new URL(document.referrer);if(u.origin!==location.origin)r=u.origin}catch(e){}if(r)set('referrer',r)}
var f=document.querySelector('form.qform');if(!f)return;
K.concat(['landing_path','referrer']).forEach(function(k){var i=f.querySelector('input[name="'+k+'"]');if(i)i.value=get(k)})})();
(function(){var f=document.querySelector('form.qform');if(!f)return;var r=f.querySelector('input[name="redirect"]');
function val(n){var i=f.querySelector('input[name="'+n+'"]');return i&&i.value?i.value.trim():''}
function paidSrc(){var c=val('utm_campaign'),s=val('utm_source'),m=val('utm_medium').toLowerCase(),cl=c.toLowerCase(),sl=s.toLowerCase();
var paid=/^(cpc|ppc|paid|paid_social|paidsocial)$/.test(m)||/^fbad/.test(cl)||/fbad|fbads|meta.?ad/.test(cl)||((/^(facebook|fb|instagram|ig|meta)$/.test(sl))&&(!!c||/^(cpc|ppc|paid|paid_social|paidsocial)$/.test(m)));
if(!paid)return'';var v=(c||s).slice(0,80).replace(/[^a-zA-Z0-9._-]/g,'');return v}
function applyRedirect(){if(!r)return;try{var u=new URL(r.value),p=paidSrc();if(p)u.searchParams.set('src',p);['utm_source','utm_campaign'].forEach(function(n){var v=val(n);if(v)u.searchParams.set(n,v)});r.value=u.toString()}catch(e){}}
applyRedirect();
f.addEventListener('submit',applyRedirect);
var m=document.querySelector('.mcta');if(!m||!('IntersectionObserver' in window))return;
new IntersectionObserver(function(es){es.forEach(function(e){m.classList.toggle('off',e.isIntersecting)})},{threshold:0.1}).observe(f)})();
