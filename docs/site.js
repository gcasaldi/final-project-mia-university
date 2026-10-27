import {compileModel,predictEmail,verifyExport,analyzeAddress,scanAddresses} from "./model-runtime.mjs";
const byId=id=>document.getElementById(id);
const elem=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
let model=null,modelError="Training artifact has not been published.",modelLoadMs=null;
const result=byId("analysis-result");
function report(title,description,level="neutral",items=[]){
  result.replaceChildren();
  const row=elem("div",undefined,"result-top"),body=elem("div");
  body.append(elem("div",title,"result-title"),elem("p",description,"result-description"));
  row.append(body,elem("span",level==="bad"?"Review needed":level==="good"?"No anomaly":"Information","result-chip "+level));
  result.append(row);
  if(items.length){const ul=elem("ul",undefined,"result-detail");items.forEach(x=>ul.append(elem("li",x)));result.append(ul);}
  result.hidden=false;
}
function emailResult(text,source){
  if(!model){report("Model unavailable","The validated machine-learning model is not available yet. "+modelError);return;}
  try{
    const predictionStart=performance.now();
    const r=predictEmail(model,text),bad=r.prediction==="Phishing";
    const predictionMs=performance.now()-predictionStart;
    report("Model classification · "+source,"Prediction generated locally using the exported TF-IDF and Logistic Regression parameters.",bad?"bad":"good");
    const chip=result.querySelector(".result-chip");
    chip.textContent=r.prediction;
    const row=elem("div",undefined,"score-row");
    row.append(elem("span","Phishing model score"),elem("strong",(r.probability*100).toFixed(2)+"%"));
    result.append(row);
    const bar=elem("div",undefined,"score-bar"),fill=elem("div");fill.style.width=(r.probability*100).toFixed(2)+"%";bar.append(fill);result.append(bar);
    const details=elem("div",undefined,"result-detail");
    details.append(elem("p","Classification threshold: 50% · recognized features: "+r.recognized));
    const addresses=scanAddresses(text);
    if(addresses.length){
      details.append(elem("p","The separate address checker also found "+addresses.length+" anomalous address(es):"));
      const ul=elem("ul");
      addresses.forEach(a=>ul.append(elem("li",a.address+" — "+a.messages.join("; "))));
      details.append(ul);
    }
    if(r.topFeatures.length){
      details.append(elem("p","Selected influential features in this prediction:"));
      const ul=elem("ul");
      r.topFeatures.slice(0,4).forEach(f=>ul.append(elem("li",f.term+" ("+(f.weight>=0?"+":"")+f.weight.toFixed(3)+")")));
      details.append(ul);
    }
    details.append(elem("p","Analysis time: "+predictionMs.toFixed(1)+" ms"+(modelLoadMs!==null?" · Model load this session: "+modelLoadMs.toFixed(0)+" ms":""));
    result.append(details,elem("p","Research classifier, not a security guarantee. This score is not a calibrated probability of harm or evidence that a sender is genuine.","result-footnote"));
  }catch(e){report("Cannot complete classification",e.message);}
}
function addressResult(){
  const r=analyzeAddress(byId("address-input").value);
  const bad=r.level==="suspicious"||r.level==="invalid";
  report(bad?"Address anomaly identified":r.level==="review"?"Manual review suggested":"No obvious address anomaly",
   "Deterministic address-only screening; no sender-identity or mailbox verification.",
   bad?"bad":"neutral",r.messages.length?r.messages:["No selected lookalike pattern found. An apparently valid address can still be used maliciously."]);
}
document.querySelectorAll("[data-panel]").forEach(tab=>{
  tab.addEventListener("click",()=>switchPanel(tab.dataset.panel));
  tab.addEventListener("keydown",event=>{
    if(!["ArrowLeft","ArrowRight"].includes(event.key))return;
    event.preventDefault();
    const names=["text","file","address"],i=names.indexOf(tab.dataset.panel);
    const next=names[(i+(event.key==="ArrowRight"?1:2))%3];
    switchPanel(next);byId("tab-"+next).focus();
  });
});
function switchPanel(name){
  for(const tab of document.querySelectorAll("[data-panel]")){
    const active=tab.dataset.panel===name;
    tab.setAttribute("aria-selected",String(active));tab.classList.toggle("active",active);
    tab.tabIndex=active?0:-1;byId("panel-"+tab.dataset.panel).hidden=!active;
  }
  result.hidden=true;
}
byId("analyze-text").addEventListener("click",()=>emailResult(byId("message-input").value,"message text"));
byId("clear-text").addEventListener("click",()=>{byId("message-input").value="";result.hidden=true;});
byId("example-legit").addEventListener("click",()=>{byId("message-input").value="Subject: Research meeting updates\n\nHello colleagues, please review the attached project discussion notes before Tuesday. Let me know if you have any feedback. Best regards.";});
byId("example-phish").addEventListener("click",()=>{byId("message-input").value="Subject: Suspicious account alert\n\nThis sample illustrates a deceptive message claiming an account problem and demanding immediate action. The address security@m1crosoft.com resembles a legitimate domain.";});
byId("analyze-address").addEventListener("click",addressResult);
byId("example-address").addEventListener("click",()=>{byId("address-input").value="security@m1crosoft.com";addressResult();});
byId("address-input").addEventListener("keydown",e=>{if(e.key==="Enter")addressResult();});
byId("email-file").addEventListener("change",e=>{
  const f=e.target.files?.[0];byId("file-name").textContent=f?f.name+" · "+(f.size/1024).toFixed(1)+" KB":"TXT or plain-text EML · up to 256 KB";
});
byId("analyze-file").addEventListener("click",async()=>{
  const f=byId("email-file").files?.[0];
  if(!f){report("Choose a file","Select a TXT or plain-text EML file first.");return;}
  if(!/\.(eml|txt)$/i.test(f.name)||f.size>262144){report("Unsupported file","Accepted: .txt or plain-text .eml, up to 256 KB.");return;}
  try{
    const content=await f.text();
    if(/Content-Type:\s*multipart\//i.test(content)||/Content-Transfer-Encoding:\s*(base64|quoted-printable)/i.test(content)){
      report("Encoded email format","This prototype cannot reliably extract text from encoded or multipart MIME messages. Paste decoded subject and body text in the Text tab.");return;
    }
    emailResult(content,"locally selected file");
  }catch(e){report("File reading error",e.message);}
});
async function init(){
  const loadStart=performance.now();
  try{
    const response=await fetch("./model.json",{cache:"default"});
    if(!response.ok)throw new Error("Model download returned "+response.status+".");
    const data=await response.json();
    const compiled=compileModel(data);
    const parity=verifyExport(compiled);
    model=compiled;
    modelLoadMs=performance.now()-loadStart;
    byId("model-status").className="status ready";
    byId("model-status-text").textContent="ML model ready · "+parity.tests+" checks passed · load "+modelLoadMs.toFixed(0)+" ms";
  }catch(error){
    modelError=error.message;
    byId("model-status").className="status error";
    byId("model-status-text").textContent="ML model not yet available";
  }
}
init();
