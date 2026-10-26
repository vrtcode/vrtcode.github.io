/* Progressive enhancement only: the complete site works without this file. */
(() => {
  'use strict';
  const button = document.querySelector('.menu-button');
  const nav = document.getElementById('primary-nav');
  const narrow = matchMedia('(max-width:859px)');
  if (button && nav) {
    const close = (focus = false) => {
      button.setAttribute('aria-expanded', 'false');
      button.textContent = 'Menu';
      nav.hidden = narrow.matches;
      if (focus) button.focus();
    };
    const sync = () => { button.hidden = !narrow.matches; close(); };
    button.addEventListener('click', () => {
      if (button.getAttribute('aria-expanded') === 'true') close(true);
      else { nav.hidden = false; button.setAttribute('aria-expanded', 'true'); button.textContent = 'Close'; }
    });
    nav.addEventListener('click', event => {
      const a = event.target.closest('a');
      if (!a || !narrow.matches) return;
      const url = new URL(a.href);
      if (url.origin === location.origin && url.pathname === location.pathname && url.hash) {
        close();
        const target = document.getElementById(decodeURIComponent(url.hash.slice(1)));
        if (target) { target.setAttribute('tabindex', '-1'); target.focus({preventScroll:true}); }
      }
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') close(true);
    });
    narrow.addEventListener('change', sync);
    sync();
  }

  const host = document.getElementById('network-bg');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (!host || !window.requestAnimationFrame) return;
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  host.appendChild(canvas);
  let nodes = [], width = 0, height = 0, raf = 0;
  const pointer = {x:-9999,y:-9999,on:false};
  const setup = () => {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    width = innerWidth; height = innerHeight;
    canvas.width = width*dpr; canvas.height = height*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    const count = Math.min(120, Math.round(width*height/13000));
    nodes = Array.from({length:count}, () => {
      const x=Math.random()*width,y=Math.random()*height;
      return {hx:x,hy:y,x,y,vx:(Math.random()-.5)*.12,vy:(Math.random()-.5)*.12,r:Math.random()<.12?2.2:1.3,lime:Math.random()<.08};
    });
  };
  const draw = (time = 0) => {
    raf = 0;
    if (document.hidden) return;
    ctx.clearRect(0,0,width,height);
    for (const p of nodes) {
      if (!reduced.matches) {
        p.hx+=p.vx; p.hy+=p.vy;
        if(p.hx<0||p.hx>width)p.vx*=-1;
        if(p.hy<0||p.hy>height)p.vy*=-1;
      }
      let tx=p.hx,ty=p.hy;
      if(pointer.on&&!reduced.matches){
        const dx=pointer.x-p.hx,dy=pointer.y-p.hy,d=Math.hypot(dx,dy);
        if(d<210){const attraction=(1-d/210)*.45;tx+=dx*attraction;ty+=dy*attraction;}
      }
      p.x+=(tx-p.x)*.08;p.y+=(ty-p.y)*.08;
    }
    for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
      const a=nodes[i],b=nodes[j],d=Math.hypot(a.x-b.x,a.y-b.y);
      if(d<135){ctx.strokeStyle=`rgba(102,217,239,${(.16*(1-d/135)).toFixed(3)})`;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
    }
    if(pointer.on&&!reduced.matches)for(const p of nodes){
      const d=Math.hypot(pointer.x-p.x,pointer.y-p.y);
      if(d<147){ctx.strokeStyle=`rgba(102,217,239,${(.22*(1-d/147)).toFixed(3)})`;ctx.beginPath();ctx.moveTo(pointer.x,pointer.y);ctx.lineTo(p.x,p.y);ctx.stroke();}
    }
    for(const p of nodes){
      ctx.fillStyle=p.lime?'rgba(181,224,122,.55)':'rgba(102,217,239,.45)';
      ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.283);ctx.fill();
    }
    if(!reduced.matches)raf=requestAnimationFrame(draw);
  };
  const restart = () => { cancelAnimationFrame(raf); raf=0; draw(); };
  addEventListener('resize', () => { setup(); restart(); });
  addEventListener('pointermove', e => {if(e.pointerType==='mouse'){pointer.x=e.clientX;pointer.y=e.clientY;pointer.on=true;}},{passive:true});
  document.addEventListener('mouseleave',()=>{pointer.on=false;});
  document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(raf);raf=0;}else restart();});
  reduced.addEventListener('change',restart);
  addEventListener('pagehide',()=>{cancelAnimationFrame(raf);raf=0;});
  addEventListener('pageshow',restart);
  setup(); restart();
})();
