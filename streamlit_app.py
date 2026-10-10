from __future__ import annotations

import streamlit as st

from src.address_validator import (
    analyze_email_address,
    inspect_addresses_in_text,
)
from src.model_service import load_or_train_model, predict_text


st.set_page_config(
    page_title="Phishing Detection — MIA University",
    page_icon="🛡️",
    layout="wide",
)


INTERNAL_METRICS = {
    "Accuracy": "98.66%",
    "Precision": "98.38%",
    "Recall": "99.07%",
    "F1-score": "98.72%",
    "ROC-AUC": "99.89%",
}

EXTERNAL_METRICS = {
    "Accuracy": "89.85%",
    "Precision": "92.74%",
    "Recall": "88.28%",
    "F1-score": "90.46%",
    "ROC-AUC": "96.45%",
}


@st.cache_resource(show_spinner=False)
def get_model():
    return load_or_train_model()


def probability_bar(probability: float) -> None:
    st.progress(min(max(probability, 0.0), 1.0))
    st.caption(f"Phishing probability: {probability:.2%} · Decision threshold: 50%")


def address_findings_panel(text: str) -> None:
    findings = inspect_addresses_in_text(text)
    if not findings:
        st.success("No obvious suspicious email-address pattern was detected in the pasted text.")
        return

    st.warning(f"{len(findings)} suspicious address indicator(s) detected.")
    for item in findings:
        with st.expander(item["address"], expanded=True):
            st.write(f"**Verdict:** {item['risk']}")
            if item.get("closest_provider"):
                st.write(f"**Possible intended provider:** {item['closest_provider']}")
            for reason in item.get("reasons", []):
                st.write(f"- {reason}")
            for warning in item.get("warnings", []):
                st.write(f"- Warning: {warning}")


st.title("AI-Powered Phishing Email Detection")
st.caption("Master Final Project · MIA University · TF-IDF + Logistic Regression")

st.info(
    "This dashboard is a demonstrator of the approved Final Project implementation. "
    "The academic classifier remains TF-IDF + Logistic Regression; the address validator "
    "is a separate deterministic screening layer and is not mixed into the reported ML metrics."
)

tab_analyze, tab_address, tab_results, tab_method = st.tabs(
    ["Analyze email", "Check address", "Model performance", "Methodology"]
)

with tab_analyze:
    st.subheader("Analyze an email")
    st.write(
        "Paste a subject/body fragment. The model analyzes the linguistic content and "
        "returns the probability of phishing."
    )

    sample_choice = st.selectbox(
        "Optional example",
        ["—", "Legitimate example", "Phishing example"],
        index=0,
    )

    legitimate_sample = (
        "Hi Giulia, the project meeting has been scheduled for tomorrow at 10:00. "
        "Please let me know if the time works for you. Best regards."
    )
    phishing_sample = (
        "URGENT: Your Microsoft account has been suspended. Verify your identity immediately "
        "at security@m1crosoft.com to avoid permanent account closure."
    )

    initial_text = ""
    if sample_choice == "Legitimate example":
        initial_text = legitimate_sample
    elif sample_choice == "Phishing example":
        initial_text = phishing_sample

    email_text = st.text_area(
        "Email subject/body",
        value=initial_text,
        height=220,
        placeholder="Paste the email subject and body here...",
    )

    if st.button("Analyze email", type="primary", use_container_width=True):
        if not email_text.strip():
            st.warning("Paste an email before running the analysis.")
        else:
            try:
                with st.spinner("Loading the V3 model..."):
                    bundle = get_model()

                result = predict_text(bundle, email_text, threshold=0.50)

                if result["status"] != "ok":
                    st.warning(result["message"])
                else:
                    probability = result["phishing_probability"]
                    left, right = st.columns([1, 1])

                    with left:
                        st.metric("ML prediction", result["prediction"])
                        st.metric("Phishing probability", f"{probability:.2%}")
                        probability_bar(probability)
                        st.caption(f"Model source: {bundle.source}")

                    with right:
                        if result["prediction"] == "Phishing":
                            st.error(
                                "The TF-IDF + Logistic Regression model classified this text as phishing."
                            )
                        else:
                            st.success(
                                "The TF-IDF + Logistic Regression model classified this text as legitimate."
                            )

                        findings = inspect_addresses_in_text(email_text)
                        if findings:
                            st.error(
                                "The message also contains at least one suspicious email-address indicator."
                            )
                            overall = "SUSPICIOUS"
                        else:
                            overall = (
                                "SUSPICIOUS"
                                if result["prediction"] == "Phishing"
                                else "NO OBVIOUS PHISHING SIGNAL"
                            )
                        st.metric("Overall screening", overall)

                    st.divider()
                    st.subheader("Address indicators inside the message")
                    address_findings_panel(email_text)

            except Exception as exc:
                st.error(
                    "The model could not be initialized. On the first run, the dashboard needs "
                    "internet access to download the public Kaggle dataset and train the V3 baseline."
                )
                st.exception(exc)

with tab_address:
    st.subheader("Check an isolated email address")
    st.write(
        "This checker does not use the text classifier. It validates syntax and looks for "
        "obvious provider impersonation, transpositions and digit/letter substitutions."
    )

    address = st.text_input(
        "Email address",
        placeholder="microsoft@m1crosoft.com",
    )

    if st.button("Check address", use_container_width=True):
        if not address.strip():
            st.warning("Enter an email address first.")
        else:
            result = analyze_email_address(address)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Syntax valid", "Yes" if result["syntax_valid"] else "No")
            with c2:
                st.metric("Address verdict", result["risk"])

            if result["risk"] == "NO_OBVIOUS_ADDRESS_ANOMALY":
                st.success(
                    "No obvious address-level anomaly was detected. "
                    "This does not prove that the sender is trustworthy."
                )
            elif result["risk"] == "REVIEW":
                st.warning("The address should be reviewed manually.")
            else:
                st.error("The address is invalid or contains a suspicious lookalike pattern.")

            if result.get("closest_provider"):
                st.write(f"**Possible intended provider:** {result['closest_provider']}")

            for reason in result.get("reasons", []):
                st.write(f"- {reason}")
            for warning in result.get("warnings", []):
                st.write(f"- Warning: {warning}")

with tab_results:
    st.subheader("Validated model performance")
    st.write(
        "These are the V3 results already obtained in the Colab experiment. "
        "The dashboard does not recompute or alter the thesis metrics."
    )

    st.markdown("#### Internal untouched test set · threshold 0.50")
    cols = st.columns(5)
    for col, (label, value) in zip(cols, INTERNAL_METRICS.items()):
        col.metric(label, value)

    st.markdown("#### External validation · TREC_07 · threshold 0.50")
    cols = st.columns(5)
    for col, (label, value) in zip(cols, EXTERNAL_METRICS.items()):
        col.metric(label, value)

    st.caption(
        "The lower external score is intentionally reported because it provides evidence "
        "about generalization beyond the original aggregate dataset."
    )

    st.markdown("#### Error analysis")
    c1, c2 = st.columns(2)
    c1.metric("False Positives", "105")
    c2.metric("False Negatives", "60")
    st.write(
        "False Negatives are especially relevant in phishing detection because they represent "
        "malicious messages that were not flagged by the classifier."
    )

with tab_method:
    st.subheader("How the Final Project works")
    st.markdown(
        """
1. **Dataset cleaning** — remove invalid rows, contradictory duplicates and normalized duplicates.
2. **Train / validation / test split** — 70% / 15% / 15%, stratified.
3. **TF-IDF** — fitted only on the training set, with unigrams and bigrams.
4. **Logistic Regression** — single supervised baseline model.
5. **Threshold selection** — optional threshold tuned on validation only.
6. **Final evaluation** — untouched test set.
7. **External validation** — TREC_07 kept outside training.
8. **Error analysis** — False Positives and False Negatives.
        """
    )

    st.markdown("#### Scope")
    st.write(
        "The dashboard deliberately preserves the approved scope. It does not introduce "
        "a second machine-learning model, deep learning or an LLM. The deterministic "
        "address checker is an auxiliary demo/safety layer."
    )

    st.markdown("#### Reproducibility")
    st.code(
        "Email text → preprocessing → TF-IDF → Logistic Regression → probability → evaluation",
        language="text",
    )

st.divider()
st.caption(
    "Giulia Casaldi · Master's Degree in Computer Science, Cybersecurity, Data Analytics and Artificial Intelligence · MIA University"
)
