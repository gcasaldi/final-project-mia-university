# Results

The notebook generates reproducible outputs at runtime rather than committing large generated artifacts to Git.

Expected outputs include:

- `metrics.json`
- `false_positives.csv`
- `false_negatives.csv`
- `tfidf_vectorizer.joblib`
- `logistic_regression.joblib`
- `address_validation_config.json`

In Google Colab these are written to:

```text
/content/final_project_outputs
```

## Reference results

### Internal test set @ 0.50
- Accuracy: 0.9866
- Precision: 0.9838
- Recall: 0.9907
- F1-score: 0.9872
- ROC-AUC: 0.9989

### TREC_07 external validation @ 0.50
- Accuracy: 0.8985
- Precision: 0.9274
- Recall: 0.8828
- F1-score: 0.9046
- ROC-AUC: 0.9645

Generated artifacts should be reproduced from the notebook rather than treated as source files.
