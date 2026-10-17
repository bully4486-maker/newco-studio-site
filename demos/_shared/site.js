(()=>{
  const els=document.querySelectorAll('.reveal');
  const rm=matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(rm||!('IntersectionObserver' in window)){els.forEach(e=>e.classList.add('in'));}
  else{
    const io=new IntersectionObserver(es=>es.forEach(e=>{
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}
    }),{threshold:.12,rootMargin:'0px 0px -40px 0px'});
    els.forEach(e=>io.observe(e));
  }
  const f=document.querySelector('form[data-demo]');
  if(f)f.addEventListener('submit',e=>{
    e.preventDefault();
    const s=f.querySelector('[role=status]');
    s.textContent='This is a demo form, so nothing was sent and no details were stored.';
  });
  document.querySelectorAll('[data-year]').forEach(e=>e.textContent=new Date().getFullYear());

  const header=document.querySelector('header.nav');
  const toggle=document.querySelector('.nav-toggle');
  const nav=document.getElementById('main-nav');
  if(header&&toggle&&nav){
    const setOpen=open=>{
      header.classList.toggle('is-open',open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    toggle.addEventListener('click',()=>setOpen(!header.classList.contains('is-open')));
    nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setOpen(false)));
    document.addEventListener('keydown',e=>{ if(e.key==='Escape') setOpen(false); });
  }
})();
