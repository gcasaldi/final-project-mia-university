# Professor Demo Dashboard

This Streamlit dashboard is a presentation layer for the V3 Final Project.

It does **not** change the scientific experiment. The core classifier remains:

```text
Email text -> preprocessing -> TF-IDF -> Logistic Regression
```

The dashboard provides:

- full email subject/body classification;
- phishing probability at the primary 0.50 threshold;
- deterministic suspicious-address checks;
- internal and external V3 performance results;
- a short explanation of the methodology and research scope.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On the first run, when no saved model artifacts exist, the dashboard downloads the same public Kaggle dataset used by the V3 notebook and trains the baseline model. Streamlit caches the trained model for subsequent interactions.

## Faster demo with saved artifacts

If the notebook-generated files are available, place:

```text
tfidf_vectorizer.joblib
logistic_regression.joblib
```

inside a local `artifacts/` directory before starting Streamlit.

The `artifacts/` directory is intentionally excluded from Git.

## Free deployment

The app is compatible with Streamlit Community Cloud. Keep the GitHub repository private and authorize Streamlit to access the repository when deploying.

Entrypoint:

```text
streamlit_app.py
```
