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

## Public academic browser dashboard

Public URL: https://gcasaldi.github.io/final-project-mia-university/

The GitHub Pages version includes actual **client-side TF-IDF + Logistic Regression prediction**. It uses the exported vocabulary, IDF array, coefficients, and intercept from the exact same supervised Python model in `src/model_service.py`. Inference runs locally in the visitor's browser: no email subject/body or file needs to be transmitted to a Python service. The published `docs/model.json` is a **model artifact**, not the source dataset.

The source implementation can be inspected in:

- `docs/index.html`, `docs/site.css`, `docs/site.js`: website and interface;
- `docs/model-runtime.mjs`: browser TF-IDF and Logistic Regression arithmetic;
- `scripts/export_browser_model.py`: reproducible sklearn model export, held-out evaluation, and numerical test vectors;
- `scripts/verify_model.mjs`: JavaScript/Python prediction parity checks;
- `.github/workflows/build_browser_model.yml`: automatic training, tests, and model artifact publication.

A visitor can paste a message, choose a plain-text TXT/EML file, or check an email address. The separate address checker is deterministic and is **not** part of the reported supervised model metrics. Encoded or multipart EML content is intentionally rejected because the static client does not contain a complete MIME parser.

To regenerate the model locally after installing dependencies, run:

```bash
python -m scripts.export_browser_model
node scripts/verify_model.mjs
```

The internal test metrics reported on the website are the documented original V3 results, which can be compared with the held-out metrics recalculated automatically during model export. The browser inference is validated using Python-generated examples and numeric tolerance before publication.

### Interpretation limits

This text-only classifier cannot inspect attachments, follow URLs, verify SPF/DKIM/DMARC, or authenticate sender identities. An ML label of `Legitimate` does not establish that an email is safe. The dashboard is a research demonstration and should not be used as a standalone security control.
