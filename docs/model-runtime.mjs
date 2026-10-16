/**
 * Minimal browser inference for the approved Python TF-IDF + Logistic Regression pipeline.
 * This is not a second ML model: it evaluates the exact exported vocabulary/IDF/weights.
 * Scope: text only; not an antivirus engine, header verification, or URL reputation service.
 */
const wordPattern = /[\p{L}\p{N}_]{2,}/gu;
const emailPattern = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi;
const urlPattern = /(?:https?:\/\/|www\.)\S+/gi;
const PROVIDERS = [
  "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com",
  "yahoo.com", "yahoo.it", "icloud.com", "me.com", "proton.me", "protonmail.com",
  "aol.com", "zoho.com", "gmx.com", "gmx.net", "libero.it", "virgilio.it",
  "alice.it", "tin.it", "tiscali.it", "tim.it", "fastwebnet.it", "aruba.it",
  "paypal.com", "amazon.com", "apple.com", "microsoft.com", "google.com",
  "poste.it", "intesasanpaolo.com", "unicredit.it"
];
const LEET = {"0":["o"],"1":["i","l"],"3":["e"],"4":["a"],"5":["s"],"7":["t"],"8":["b"],"9":["g"]};

export function preprocess(text) {
  // Align with src/phishing_utils.py: substitute URLs first, then email addresses.
  return String(text).replace(urlPattern, " URLTOKEN ").replace(emailPattern, " EMAILTOKEN ").replace(/\s+/g, " ").trim().toLowerCase();
}
export function tokenize(text) {
  return preprocess(text).match(wordPattern) || [];
}
export function compileModel(payload) {
  if (!payload || payload.format !== "phishlens-sklearn-v1" ||
      !Array.isArray(payload.features) || !Array.isArray(payload.idf) ||
      !Array.isArray(payload.coef) || payload.features.length !== payload.idf.length ||
      payload.features.length !== payload.coef.length || !Number.isFinite(payload.intercept) ||
      payload.features.length < 100) {
    throw new Error("The published model artifact is missing or incompatible.");
  }
  return {...payload, dictionary: new Map(payload.features.map((feature, index) => [feature, index]))};
}
export function predictEmail(model, emailText) {
  const raw = String(emailText ?? "").trim();
  if (raw.split(/\s+/).filter(Boolean).length < 5) {
    throw new Error("Please enter at least five words from the message.");
  }
  if (raw.length > 200000) throw new Error("Message exceeds the 200,000-character limit.");
  const tokens = tokenize(raw);
  const counts = new Map();
  function bump(term) {
    const idx = model.dictionary.get(term);
    if (idx !== undefined) counts.set(idx, (counts.get(idx) || 0) + 1);
  }
  for (let i = 0; i < tokens.length; i++) {
    bump(tokens[i]);
    if (i > 0) bump(tokens[i-1] + " " + tokens[i]);
  }
  if (!counts.size) throw new Error("The text contains no vocabulary features recognized by this model.");
  let normSquared = 0, logitContribution = 0;
  const usedFeatures = [];
  for (const [idx, count] of counts) {
    const tfidf = (1 + Math.log(count)) * model.idf[idx];
    normSquared += tfidf * tfidf;
    logitContribution += tfidf * model.coef[idx];
    usedFeatures.push({term:model.features[idx], contribution:tfidf * model.coef[idx]});
  }
  const norm = Math.sqrt(normSquared);
  const logit = model.intercept + (norm ? logitContribution / norm : 0);
  const proba = logit >= 0 ? 1 / (1 + Math.exp(-logit)) : Math.exp(logit) / (1 + Math.exp(logit));
  return {
    probability: proba,
    prediction: proba >= model.threshold ? "Phishing" : "Legitimate",
    recognized: counts.size,
    threshold: model.threshold,
    // Contributions are indicative: no causal claims about feature importance.
    topFeatures: usedFeatures.map(x=>({term:x.term,weight:x.contribution/norm}))
      .sort((a,b)=>Math.abs(b.weight)-Math.abs(a.weight)).slice(0,6),
  };
}
export function verifyExport(model) {
  const tests = model.self_tests || [];
  if (!tests.length) throw new Error("Reference test vectors missing.");
  const deviations = [];
  for (const test of tests) {
    const got = predictEmail(model, test.text).probability;
    deviations.push(Math.abs(got - test.probability));
  }
  const maxDifference = Math.max(...deviations);
  if (maxDifference > 0.003) throw new Error("Browser and Python predictions differ: " + maxDifference.toFixed(5));
  return {tests: tests.length,maxDifference};
}
function damerauDistance(a,b) {
  const d=Array.from({length:a.length+1},()=>Array(b.length+1).fill(0));
  for(let i=0;i<=a.length;i++)d[i][0]=i;
  for(let j=0;j<=b.length;j++)d[0][j]=j;
  for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++){
    const cost=a[i-1]===b[j-1]?0:1;
    d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+cost);
    if(i>1&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1])d[i][j]=Math.min(d[i][j],d[i-2][j-2]+1);
  }
  return d[a.length][b.length];
}
function closestProvider(domain) {
  if (PROVIDERS.includes(domain)) return null;
  let variants=new Set([domain]);
  for(const [digit,replacements] of Object.entries(LEET)){
    if(!domain.includes(digit))continue;
    const snapshot=Array.from(variants);
    for(const item of snapshot)for(const repl of replacements){
      if(variants.size<64) variants.add(item.split(digit).join(repl));
    }
  }
  for(const variant of variants)if(variant!==domain&&PROVIDERS.includes(variant))return variant;
  let nearest=null, best=999;
  for(const p of PROVIDERS){const d=damerauDistance(domain,p);if(d<best){nearest=p;best=d;}}
  return best<=1?nearest:null;
}
export function analyzeAddress(value) {
  const address=String(value??"").trim().replace(/^<|>$/g,"");
  if(!address) return {address,level:"invalid",messages:["No email address provided."],provider:null};
  const chunks=address.split("@");
  if(chunks.length!==2) return {address,level:"invalid",messages:["An email address must contain exactly one @ character."],provider:null};
  const domain=chunks[1].toLowerCase();
  const issues=[], cautions=[];
  if (/[,;]/.test(domain)) issues.push("Invalid separator in the domain (comma or semicolon).");
  if(!/^[A-Za-z0-9.!#$%&'*+/=?^_{|}~-]+@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$/.test(address)) issues.push("Address does not meet the standard ASCII format checked by this demo.");
  if(/[^\x00-\x7F]/.test(address)) cautions.push("Unicode characters: manual review for possible homoglyphs.");
  if(domain.includes("xn--")) cautions.push("Punycode/IDN domain: manual review suggested.");
  const provider=closestProvider(domain.replace(/[,;]/g,"."));
  if(provider) issues.push("Domain resembles "+provider+" (possible impersonation).");
  return {address,level:issues.length?"suspicious":cautions.length?"review":"no-obvious-issue",
    messages:[...issues,...cautions],provider};
}
export function scanAddresses(text) {
  const matches=String(text).match(/[A-Za-z0-9.!#$%&'*+/=?^_{|}~-]+@[^\s<>"']+/g) || [];
  const unique=new Set(matches.map(a=>a.replace(/[.,;!?]+$/,"")));
  return Array.from(unique).slice(0,100).map(analyzeAddress).filter(x=>x.level!=="no-obvious-issue");
}
