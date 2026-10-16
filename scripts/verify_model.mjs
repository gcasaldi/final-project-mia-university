import { readFileSync } from "node:fs";
import { compileModel, predictEmail, verifyExport, analyzeAddress } from "../docs/model-runtime.mjs";

const artifact = JSON.parse(readFileSync("docs/model.json", "utf8"));
const model = compileModel(artifact);
const parity = verifyExport(model);
if (parity.tests < 4) throw new Error("Too few Python/JavaScript parity vectors.");
for (const item of artifact.self_tests) {
  const p = predictEmail(model, item.text).probability;
  if (!Number.isFinite(p) || p < 0 || p > 1) throw new Error("Invalid ML probability");
}
for (const test of [
  ["security@m1crosoft.com","suspicious"],
  ["support@paypa1.com","suspicious"],
  ["contact@gmail.com","no-obvious-issue"],
  ["invalid@","suspicious"],
]) {
  const result = analyzeAddress(test[0]);
  if (result.level !== test[1]) throw new Error("Address test failed: "+test[0]+" -> "+result.level);
}
console.log("PASS: browser model matches Python on",parity.tests,"test vectors.");
console.log("Maximum absolute probability difference:",parity.maxDifference.toFixed(7));
console.log("PASS: address validation smoke checks.");
