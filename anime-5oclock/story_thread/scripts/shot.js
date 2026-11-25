const { chromium } = require('playwright'); const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1422,height:892}});
for(const k of (process.argv[2]?[process.argv[2]]:['1-surge','2-konbini','3-train','4-lights','5-forecast'])){
 const svg=fs.readFileSync(__dirname+'/'+k+'.svg','utf8');
 await p.setContent('<html><body style="margin:0;background:#0d0b12">'+svg+'</body></html>');
 await p.waitForTimeout(300); await p.screenshot({path:__dirname+'/'+k+'.png'});}
await b.close();})();
