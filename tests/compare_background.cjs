/* Code-level migration check against the reviewed, owner-supplied template. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
if(!process.argv[2])throw new Error('Usage: node tests/compare_background.cjs /path/to/reviewed-design.html');
const root=path.resolve(__dirname,'..');
const out=path.resolve(process.env.VRT_REPORT_DIR||path.join(root,'test-results'));fs.mkdirSync(out,{recursive:true});
const source=fs.readFileSync(process.argv[2],'utf8');
const method=source.slice(source.indexOf('  startNet() {'),source.indexOf('  stopNet() {'));
assert.ok(method.startsWith('  startNet() {')&&method.trim().endsWith('}'),'Expected reviewed background method was not found');
const target=fs.readFileSync(path.join(root,'assets/site.js'),'utf8');
function run(code,width,height,dpr,reduce,original){
 let commands=[],seed=1259,next;const handlers={},docHandlers={};
 const ctx=new Proxy({}, {set(o,k,v){commands.push(['set',k,v]);o[k]=v;return true;},get(o,k){return o[k]||((...args)=>commands.push([k,...args]));}});
 const canvas={style:{},getContext:()=>ctx};const host={appendChild:()=>{}};
 const math=Object.create(Math);math.random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const sandbox={Math:math,innerWidth:width,innerHeight:height,devicePixelRatio:dpr,
  matchMedia:()=>({matches:reduce,addEventListener:()=>{}}),requestAnimationFrame:cb=>{next=cb;return 1;},cancelAnimationFrame:()=>{},
  addEventListener:(name,cb)=>{handlers[name]=cb;},
  document:{hidden:false,querySelector:()=>null,getElementById:id=>id==='network-bg'?host:null,createElement:()=>canvas,addEventListener:(name,cb)=>{docHandlers[name]=cb;}},
  host};sandbox.window=sandbox;
 const context=vm.createContext(sandbox);
 if(original)vm.runInContext('const component={netRef:{current:host},'+method+'};component.startNet();',context);
 else vm.runInContext(code,context);
 return {take:()=>{const c=commands;commands=[];return c;},frame:()=>next(0),move:(x,y)=>handlers[original?'mousemove':'pointermove']({clientX:x,clientY:y,pointerType:'mouse'}),leave:()=>docHandlers.mouseleave(),resize:()=>handlers.resize(),size:()=>({width:canvas.width,height:canvas.height})};
}
const report=[];
for(const width of [390,1440])for(const dpr of [1,2,3])for(const reduce of [false,true]){
 const a=run('',width,1000,dpr,reduce,true),b=run(target,width,1000,dpr,reduce,false);
 let commandCount=0,steps=0;
 const compare=label=>{const x=a.take(),y=b.take();assert.deepEqual(y,x,`${width}/DPR${dpr}/reduce${reduce}/${label}`);commandCount+=x.length;steps++;};
 compare('initial');assert.deepEqual(b.size(),a.size());
 if(!reduce){
  for(let i=0;i<10;i++){a.frame();b.frame();compare('drift '+i);}
  a.move(width*.55,450);b.move(width*.55,450);
  for(let i=0;i<20;i++){a.frame();b.frame();compare('attract '+i);}
  a.leave();b.leave();
  for(let i=0;i<40;i++){a.frame();b.frame();compare('return '+i);}
 }else{a.resize();b.resize();compare('reduced-motion resize');}
 report.push({width,height:1000,dpr,reducedMotion:reduce,steps,commandCount,exactCommandMatch:true,canvasSize:b.size()});
}
fs.writeFileSync(path.join(out,'background-code-parity.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({configurations:report.length,totalSteps:report.reduce((n,r)=>n+r.steps,0),totalCommands:report.reduce((n,r)=>n+r.commandCount,0),allExact:true}));
