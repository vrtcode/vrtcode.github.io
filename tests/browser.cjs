/* Optional browser QA: requires Playwright, but is not a build/runtime dependency. */
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const directory = path.resolve(process.env.VRT_TEST_SITE || path.join(root, 'dist'));
const manifest = JSON.parse(fs.readFileSync(path.join(directory, 'build-manifest.json')));
const out = path.resolve(process.env.VRT_REPORT_DIR || path.join(root,'test-results'));
const port = process.env.VRT_TEST_PORT || '8768';
const origin = `http://127.0.0.1:${port}`;
const base = origin + manifest.base_path;
const slugs = ['android-integrity','realtime-security','worker-lifecycle','mobile-sdk-analysis','push-integration-security','network-observability','ios-attestation'];
const routes = ['/',...slugs.map(s=>`/work/${s}/`),'/not-a-real-page/'];
const results = [];
const server = spawn(process.env.PYTHON || 'python3',[path.join(root,'serve.py'),'--directory',directory,'--port',port],{stdio:'ignore'});
let browser;
(async()=>{
  fs.mkdirSync(out,{recursive:true});
  for(let i=0;i<100;i++){
    assert.equal(server.exitCode,null,'Preview server exited before testing');
    try{const r=await fetch(base+'/');if(r.status===200)break;}catch{}
    if(i===99)throw new Error('Preview server did not become ready');
    await new Promise(r=>setTimeout(r,100));
  }
  browser=await chromium.launch({headless:true,...(process.env.BROWSER_EXECUTABLE?{executablePath:process.env.BROWSER_EXECUTABLE}:{})});
  for(const javascript of [true,false])for(const width of (process.env.VRT_POINTER_ONLY ? [] : [360,390,768,1440])){
    const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:javascript,reducedMotion:'reduce'});
    const page=await context.newPage();
    const errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',route=>{
      if(new URL(route.request().url()).origin!==origin){external.push(route.request().url());return route.abort();}
      return route.continue();
    });
    for(const route of routes){
      const response=await page.goto(base+route,{waitUntil:'networkidle'});
      assert.equal(response.status(),route.includes('not-a-real')?404:200,route);
      await page.evaluate(()=>document.fonts.ready);
      const state=await page.evaluate(()=>({
        lang:document.documentElement.lang,width:innerWidth,scroll:document.documentElement.scrollWidth,
        h1:[...document.querySelectorAll('h1')].map(e=>e.textContent),
        unresolved:document.body.innerText.includes('{{'),
        svg:[...document.querySelectorAll('svg')].every(s=>s.viewBox.baseVal.width===300),
        font:document.fonts.check('16px "IBM Plex Sans"'),
        caseNames:[...document.querySelectorAll('#work a[aria-label]')].every(a=>a.getAttribute('aria-label').includes([...a.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE).map(n=>n.textContent).join('').trim()))
      }));
      assert.equal(state.lang,'en');assert.equal(state.scroll,state.width,`${route} overflows at ${width}`);
      assert.equal(state.h1.length,1);assert.equal(state.unresolved,false);assert.equal(state.svg,true);assert.equal(state.font,true);assert.equal(state.caseNames,true,'Visible case-link words must be included in their accessible name');
      if(route==='/'){
        assert.match(state.h1[0],/Figure out what's/);
        if(width===390&&javascript){
          const menu=page.locator('.menu-button'),nav=page.locator('#primary-nav');
          assert.equal(await menu.isVisible(),true);assert.equal(await nav.isVisible(),false);
          await menu.click();assert.equal(await nav.isVisible(),true);
          await page.keyboard.press('Escape');assert.equal(await nav.isVisible(),false);
          assert.equal(await menu.evaluate(el=>document.activeElement===el),true);
          await menu.click();await page.locator('#primary-nav a[href$="#about"]').click();
          assert.equal(await nav.isVisible(),false);
          assert.equal(await page.evaluate(()=>document.activeElement.id),'about');
          await page.goto(base+'/');await page.evaluate(()=>document.fonts.ready);
        }
        if(width===390&&!javascript)assert.equal(await page.locator('#primary-nav').isVisible(),true);
        if(javascript&&(width===1440||width===390))await page.screenshot({path:path.join(out,`home-${width}.png`)});
      }
      if(route==='/work/android-integrity/'&&javascript&&width===1440)await page.screenshot({path:path.join(out,'case-1440.png')});
      results.push({javascript,width,route,status:response.status(),result:'PASS'});
    }
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    await context.close();
  }
  const context=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'reduce'});
  const page=await context.newPage();await page.goto(base+'/');
  const before=await page.locator('canvas').evaluate(c=>c.toDataURL());
  await page.waitForTimeout(300);
  const after=await page.locator('canvas').evaluate(c=>c.toDataURL());
  assert.equal(before,after,'Reduced-motion canvas must remain static');
  await context.close();
  const motionContext=await browser.newContext({viewport:{width:1440,height:900},reducedMotion:'no-preference'});
  const motionPage=await motionContext.newPage();
  await motionPage.addInitScript(()=>{
    // Observe canvas commands while driving real animation frames deterministically.
    const original=CanvasRenderingContext2D.prototype.arc;
    window.__observedArcs=[];
    CanvasRenderingContext2D.prototype.arc=function(x,y,...rest){window.__observedArcs.push({x,y});return original.call(this,x,y,...rest);};
    window.requestAnimationFrame=callback=>{window.__nextFrame=callback;return 1;};
    window.cancelAnimationFrame=()=>{};
  });
  await motionPage.goto(base+'/');
  const initial=await motionPage.evaluate(()=>{window.__observedArcs=[];window.__nextFrame(100);return window.__observedArcs[0];});
  assert.ok(initial,'Background must draw a node');
  const target={x:initial.x+(initial.x<1250?100:-100),y:initial.y};
  await motionPage.mouse.move(target.x,target.y);
  const moved=await motionPage.evaluate(()=>{
    for(let i=1;i<=20;i++){window.__observedArcs=[];window.__nextFrame(100+i*40);}
    return window.__observedArcs[0];
  });
  const movement=(moved.x-initial.x)*Math.sign(target.x-initial.x);
  assert.ok(movement>8,`Nodes must move toward the mouse, not merely draw lines; observed movement=${movement}`);
  const released=await motionPage.evaluate(()=>{
    document.dispatchEvent(new Event('mouseleave'));
    for(let i=21;i<=60;i++){window.__observedArcs=[];window.__nextFrame(100+i*40);}
    return window.__observedArcs[0];
  });
  const afterRelease=(released.x-initial.x)*Math.sign(target.x-initial.x);
  assert.ok(afterRelease<movement-5,'Nodes must relax away from the cursor target after mouse leave');
  await motionContext.close();
  const motion={reducedMotion:'PASS',pointerAttraction:'PASS',pointerReturn:'PASS',pointerMovementPx:Number(movement.toFixed(3)),pointerAfterReleasePx:Number(afterRelease.toFixed(3))};
  const report=process.env.VRT_POINTER_ONLY?{engine:'Chromium',scope:'pointer-only',...motion}:{engine:'Chromium',checks:results.length,allPassed:true,externalResourceRequests:0,...motion,menu:'PASS',results};
  fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(report,null,2)+'\n');
  console.log(process.env.VRT_POINTER_ONLY ? 'PASS: focused pointer attraction and reduced-motion checks (full route suite skipped).' : `PASS: ${results.length} page/viewport/JavaScript combinations; menu, fonts, SVGs, reduced motion, pointer attraction, real HTTP 404, and zero external resource requests.`);
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();server.kill('SIGTERM');});
