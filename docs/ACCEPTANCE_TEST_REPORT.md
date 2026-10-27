# Manual acceptance testing — 16 October 2026

**Project:** AI-Powered Phishing Email Detection Using Natural Language Processing and Machine Learning  
**Author:** Giulia Casaldi  
**Test environment:** Public GitHub Pages dashboard, `Email address` tab.  
**Evidence:** Interactive outputs observed and transcribed by the project author, 16 October 2026.  
**Type:** Black-box manual acceptance testing, supplemented by automated regression tests.

## Five completed manual checks

| # | Input entered by author | Expected result | Observed dashboard response | Assessment |
|---|---|---|---|---|
| 1 | `security@m1crosoft.com` | Flag lookalike of microsoft.com | Address anomaly identified; domain resembles microsoft.com | Pass |
| 2 | `support@paypa1.com` | Flag lookalike of paypal.com | Address anomaly identified; domain resembles paypal.com | Pass |
| 3 | `hello@gmail.com` | No obvious structural or lookalike anomaly | No obvious address anomaly | Pass |
| 4 | `test@@gmail.com` | Reject malformed address | Address anomaly identified; an email address must contain exactly one @ | Pass |
| 5 | `security@gmial.com` | Flag transposition of gmail.com | Address anomaly identified; domain resembles gmail.com | Pass |

**Result: 5/5 manual address-inspection cases behaved as expected.** The third result is a *limited negative check*, not an authentication or safety certificate.

## Code maintenance and regression coverage

The five observed input/output pairs are encoded in `scripts/verify_model.mjs`. Additional automated checks cover malformed separators, a trailing-dot lookalike, addresses exceeding the supported length, mixed text containing suspicious senders, machine-learning scores within [0,1], minimal text length, and Python-to-JavaScript probability equivalence.

Two hardening adjustments were made during the acceptance review:

1. Normalize a trailing period in the **diagnostic domain comparison** so a provider-lookalike suggestion is still possible, while preserving the invalid original address.
2. Reject excessively long address strings early to avoid unnecessary edit-distance comparisons on untrusted input.

The automated suite runs in `.github/workflows/build_browser_model.yml`. See the [latest GitHub Actions runs](https://github.com/gcasaldi/final-project-mia-university/actions).

## Additional mobile and file-upload checks — 27 October 2026

Two file-based checks were completed from an Android smartphone using the public GitHub Pages interface:

| Input | Observed result | Assessment |
|---|---|---|
| `phishing_test_email.txt` | Phishing, 98.76% model score, threshold 50%, 34 recognised features | Pass |
| `phishing_test_email.eml` | Phishing, 96.48% model score, threshold 50%, 68 recognised features | Pass |

During the `.eml` test, the separate deterministic address checker also flagged `security@m1crosoft.com` as a possible impersonation of `microsoft.com`.

The page remained readable and usable on the tested Android device. These checks confirm the plain-text `.txt` and `.eml` upload paths and basic responsive behaviour. They are interface-level acceptance checks and do not alter the Machine Learning evaluation metrics.

## Remaining optional presentation-level checks

| Test area | Procedure | Evidence to record |
|---|---|---|
| Trained text classifier | Use **Legitimate example** then **Analyze email** | Label, score, and feature explanation |
| Trained text classifier | Use **Phishing example** then **Analyze email** | Label, score, and feature explanation |
| Input validation | Try fewer than five words | Appropriate explanation, no prediction |
| MIME limitation | Choose a multipart or encoded .eml | Explicit unsupported-format warning |
| Performance | If desired, benchmark initial model loading and repeat classification | Cold-load and repeat latency |

**Interpretation:** A high score is the trained model's classification estimate on the supplied text, not a calibrated real-world probability of harm. Even when the address checker reports no anomaly or the text model predicts “Legitimate”, the email can still be malicious.

## Academic scope

Address-domain checks are deterministic and assessed separately. They are **not** included in the internal or external TF-IDF/Logistic Regression metrics reported in the V3 research notebook.
