# AI-Powered Phishing Email Detection Using NLP and Machine Learning

Master Final Project — MIA University

This private repository contains the implementation of the Final Project **“AI-Powered Phishing Email Detection Using Natural Language Processing and Machine Learning”**.

## Project scope

The academic experiment follows a deliberately simple and reproducible supervised-learning pipeline:

**Email text → preprocessing → TF-IDF → Logistic Regression → evaluation**

The project uses one supervised model, in line with the approved scope.

## Methodology

- Binary classification: phishing vs legitimate email
- Text preprocessing with URL and email-address tokenization
- Stratified **70% train / 15% validation / 15% test** split
- TF-IDF fitted **only on the training set**
- Logistic Regression as the supervised baseline
- Threshold selection performed on the validation set only
- Final untouched test-set evaluation
- False Positive / False Negative error analysis
- External validation on **TREC_07** from the Phishing Email Curated Datasets (Zenodo DOI: 10.5281/zenodo.8339691)
- Auxiliary deterministic email-address validation for malformed and lookalike domains

The deterministic address validator is kept separate from the ML metrics and is not presented as a second supervised model.

## Main results

### Internal test set @ threshold 0.50

| Metric | Result |
|---|---:|
| Accuracy | 98.66% |
| Precision | 98.38% |
| Recall | 99.07% |
| F1-score | 98.72% |
| ROC-AUC | 99.89% |

### External validation — TREC_07 @ threshold 0.50

| Metric | Result |
|---|---:|
| Accuracy | 89.85% |
| Precision | 92.74% |
| Recall | 88.28% |
| F1-score | 90.46% |
| ROC-AUC | 96.45% |

The external result is intentionally reported separately because it gives a more realistic view of generalization beyond the original aggregate dataset.

## Repository structure

```text
final-project-mia-university/
├── notebooks/
│   └── Final_Project_v3_Colab.ipynb
├── src/
│   ├── __init__.py
│   ├── address_validator.py
│   └── phishing_utils.py
├── tests/
│   └── test_address_validator.py
├── results/
│   └── README.md
├── .gitignore
├── requirements.txt
└── README.md
```

## How to run the full experiment

The recommended environment is **Google Colab**.

1. Open `notebooks/Final_Project_v3_Colab.ipynb`.
2. Run the notebook from the first cell.
3. The original Kaggle dataset is downloaded at runtime.
4. TREC_07 is downloaded from Zenodo and its checksum is verified.
5. Run the cells in order.
6. Generated artifacts are saved to `/content/final_project_outputs`.

The datasets and generated model artifacts are intentionally excluded from Git.

## Local reusable components

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the deterministic address-validator tests:

```bash
pytest -q
```

Example:

```python
from src.address_validator import analyze_email_address

print(analyze_email_address("microsoft@m1crosoft.com"))
```

The expected verdict is `INVALID_OR_SUSPICIOUS`, with `microsoft.com` identified as the likely impersonated domain.

## Reproducibility

The notebook uses `RANDOM_STATE = 42` and saves:

- TF-IDF vectorizer
- Logistic Regression model
- metrics JSON
- False Positive examples
- False Negative examples
- address-validator configuration

## Important interpretation

A syntactically valid email address is not automatically legitimate. The auxiliary validator detects obvious structural anomalies, one-edit provider typos, transpositions, and common digit/letter substitutions such as:

- `m1crosoft.com → microsoft.com`
- `gma1l.com → gmail.com`
- `gmial.com → gmail.com`
- `paypa1.com → paypal.com`

A result of `NO_OBVIOUS_ADDRESS_ANOMALY` means only that no obvious address-level anomaly was found; it does not prove sender identity.

## Author

Giulia Casaldi  
Master's Degree in Computer Science, Cybersecurity, Data Analytics and Artificial Intelligence — MIA University

## Status

Final Project implementation — V3.
