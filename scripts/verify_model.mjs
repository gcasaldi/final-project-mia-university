import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { compileModel, predictEmail, verifyExport, analyzeAddress, scanAddresses, preprocess } from "../docs/model-runtime.mjs";

const artifact = JSON.parse(readFileSync("docs/model.json", "utf8"));
const model = compileModel(artifact);
const parity = verifyExport(model);
assert.ok(parity.tests >= 5, "At least five reference predictions are required");
assert.ok(parity.maxDifference < 0.003, "Python-to-browser score parity must be maintained");

for (const test of artifact.self_tests) {
  const prediction = predictEmail(model, test.text);
  assert.ok(Number.isFinite(prediction.probability) && prediction.probability >= 0 && prediction.probability <= 1);
  assert.equal(prediction.prediction, prediction.probability >= 0.5 ? "Phishing" : "Legitimate");
  assert.ok(prediction.recognized > 0);
}
assert.throws(() => predictEmail(model, "Hello"), /at least five words/);
assert.throws(() => predictEmail(model, "hello ".repeat(50000)), /200,000-character limit/);
assert.equal(preprocess("Please use https://example.com and contact user@gmail.com now."),
  "please use urltoken and contact emailtoken now.");

const addressTests = [
  // October 16 manual acceptance tests: all five scenarios reported by the project author.
  ["security@m1crosoft.com", "suspicious", "microsoft.com"],
  ["support@paypa1.com", "suspicious", "paypal.com"],
  ["hello@gmail.com", "no-obvious-issue", null],
  ["test@@gmail.com", "invalid", null],
  ["security@gmial.com", "suspicious", "gmail.com"],
  // Additional regression/edge cases.
  ["security@gma1l.com", "suspicious", "gmail.com"],
  ["contact@outlook.com", "no-obvious-issue", null],
  ["invalid@", "suspicious", null],
  ["", "invalid", null],
  ["suspicious@gmail,com", "suspicious", null],
  ["support@paypa1.com.", "suspicious", "paypal.com"],
  ["x@".concat("a".repeat(300))+".com", "invalid", null],
];
for (const [address, expectedLevel, expectedProvider] of addressTests) {
  const verdict = analyzeAddress(address);
  assert.equal(verdict.level, expectedLevel,
    `Wrong risk level for "${address}": ${verdict.level}`);
  if (expectedProvider) assert.equal(verdict.provider, expectedProvider);
}
const extracted = scanAddresses("From: team@gmail.com; Reply-To: help@paypa1.com. Contact security@m1crosoft.com.");
assert.equal(extracted.length, 2, "Embedded provider-lookalike addresses should be identified");
assert.ok(extracted.some(x => x.provider === "paypal.com"));
assert.ok(extracted.some(x => x.provider === "microsoft.com"));

console.log(`PASS: ${parity.tests} Python ↔ JavaScript classification parity vectors (max deviation ${parity.maxDifference.toFixed(8)}).`);
console.log(`PASS: ${addressTests.length} address regression cases, including all five user acceptance cases.`);
console.log("PASS: message preprocessing, prediction guardrails and mixed-message address extraction.");
