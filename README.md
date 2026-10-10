# AI-Powered Phishing Email Detection Using NLP and Machine Learning

Master Final Project — MIA University

This repository contains the implementation and supporting material for the Final Project **“AI-Powered Phishing Email Detection Using Natural Language Processing and Machine Learning”**.

## Project scope

The project follows a deliberately simple and reproducible supervised-learning pipeline:

**Email text → preprocessing → TF-IDF → Logistic Regression → evaluation**

The academic experiment remains based on one supervised model, as defined in the approved project scope.

## Methodology

- Binary classification: phishing vs legitimate email
- Text preprocessing with URL and email-address tokenization
- Stratified **70% train / 15% validation / 15% test** split
- TF-IDF fitted **only on the training set**
- Logistic Regression as the supervised baseline
- Validation-only threshold selection
- Final untouched test-set evaluation
- False Positive / False Negative error analysis
- External validation on **TREC_07** from the Phishing Email Curated Datasets (Zenodo DOI: 10.5281/zenodo.8339691)
- Auxiliary deterministic validation for suspicious/typosquatted email domains; this layer is kept separate from the ML metrics

## Main results

### Internal test set — threshold 0.50

| Metric | Result |
|---|---:|
| Accuracy | 98.66% |
| Precision | 98.38% |
| Recall | 99.07% |
| F1-score | 98.72% |
| ROC-AUC | 99.89% |

### External validation — TREC_07

| Metric | Result |
|---|---:|
| Accuracy | 89.85% |
| Precision | 92.74% |
| Recall | 88.28% |
| F1-score | 90.46% |
| ROC-AUC | 96.45% |

The lower external score is treated as meaningful evidence about generalization and dataset bias rather than hidden by the internal split.

## Repository structure

```text
final-project-mia-university/
├── notebooks/
│   └── Final_Project_v3_Colab.ipynb
├── reports/
│   └── AI_Powered_Phishing_Final_Project_COMPLETE.docx
├── evidence/
│   └── Final_Project_v3_Colab_Evidence.pdf
├── results/
│   └── README.md
├── .gitignore
├── requirements.txt
└── README.md
```

## How to run

The recommended environment is **Google Colab**.

1. Open `notebooks/Final_Project_v3_Colab.ipynb`.
2. Run the notebook from the first cell.
3. The notebook downloads the original Kaggle dataset at runtime.
4. It downloads and verifies the TREC_07 external corpus from Zenodo.
5. Run all cells in order.
6. Generated artifacts are written to `/content/final_project_outputs` in Colab.

No dataset is committed to this repository.

## Reproducibility

The notebook uses a fixed random seed (`RANDOM_STATE = 42`) and saves:

- TF-IDF vectorizer
- Logistic Regression model
- metrics JSON
- False Positive examples
- False Negative examples
- address-validator configuration

## Notes

The deterministic address-validation layer is an auxiliary screening component. It is **not** a second supervised model and is not mixed into the primary thesis metrics.

Examples such as `m1crosoft.com`, `gma1l.com` and `gmial.com` are detected as suspicious provider-domain lookalikes.

## Author

Giulia Casaldi  
Master's Degree in Computer Science, Cybersecurity, Data Analytics and Artificial Intelligence — MIA University

## Status

Final Project implementation — V3.
