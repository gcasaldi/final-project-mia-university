# Final Project — methodological alignment and remaining revisions (23 October 2026)

**Title:** AI-Powered Phishing Email Detection Using NLP and Machine Learning

This document supplements the already-submitted V3 notebook and Word report. It does **not** claim that a revised Word report has been sent, nor that new experiments have been executed.

## What is already evidenced in the repository
- Reproducible text preprocessing, TF-IDF and Logistic Regression baseline.
- Stratified 70/15/15 train/validation/test partition; model fitting and threshold selection separated from untouched test evaluation.
- Internal test metrics (accuracy 98.66%, precision 98.38%, recall 99.07%, F1 98.72%) and separate external TREC_07 metrics (accuracy 89.85%, precision 92.74%, recall 88.28%, F1 90.46%).
- False-positive and false-negative review, with deterministic address validation explicitly outside supervised ML metrics.

## Adjustments to incorporate into the final Word report

### 1. Clear quantitative comparison and interpretation
Present internal and external test results side by side. The F1 difference is **8.26 percentage points** (98.72% vs 90.46%); the accuracy difference is **8.81 percentage points** (98.66% vs 89.85%). These are *descriptive cross-dataset differences*, not a controlled causal estimate of domain shift. State that the external set is distinct and the degradation motivates further generalization analysis. Keep dataset size, class balance and sampling provenance alongside each result.

### 2. Generalization experiment (next block; not yet run)
Evaluate on a separately sourced, previously unseen corpus. Before fitting, check exact and near-duplicate messages across train/validation/test and external data, including normalization of subject/body and quoted threads. Preserve the untouched final test split. Report class distribution, precision, recall, F1 and confusion matrix at the fixed 0.50 threshold; optionally report ROC-AUC and PR-AUC. Do not tune the threshold using the external set. If comparing a validation-selected threshold, mark it explicitly and apply it unchanged to external data.

### 3. Critical error analysis
Review a privacy-safe sample of false positives and false negatives from both internal and external tests. Group errors by theme (e.g. legitimate urgency language, short messages, obfuscation, formatting, out-of-vocabulary terms). Distinguish observed patterns from hypotheses; report counts if available, and do not include private email contents.

### 4. Limitations and threats to validity
TF-IDF relies on lexical patterns; it does not verify sender identity, URL reputation, attachment safety, authentication headers, or semantic intent. Public datasets can contain duplicates, sampling biases, and historical language patterns. External performance depends on domain and prevalence; model scores are not necessarily calibrated real-world phishing probabilities. The browser demonstrator and lookalike-address checker are supplementary interfaces and not separate trained classifiers.

### 5. Conclusions and future work
Conclude that the baseline is effective **on the evaluated datasets**, while the external performance gap and false-negative risks limit deployment claims. Future work: cross-corpus validation, temporal splits, calibration checks, concept-drift monitoring, and a carefully controlled comparison with an alternative baseline *only if the supervisor approves scope expansion*.

## Word report verification checklist
- [ ] Results tables exactly match the notebook output and identify the evaluation dataset.
- [ ] Dataset origin, licenses/permissions, preprocessing and split strategy documented.
- [ ] Threshold-selection methodology does not leak test labels.
- [ ] Confusion matrices and example errors align with actual runs.
- [ ] Limitations, ethics/privacy, reproducibility and bibliography are present.
- [ ] No claim of completed new experiments without run artifacts.
- [ ] Supervisor approves the final submitted version.

**Status:** methodological addendum prepared; Word file requires direct review/editing against the latest submitted version.
