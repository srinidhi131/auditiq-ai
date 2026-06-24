import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os

# ---------------------------------------------------

# PAGE CONFIG

# ---------------------------------------------------

st.set_page_config(
page_title="AuditIQ",
page_icon="🛡️",
layout="wide"
)

# ---------------------------------------------------

# GEMINI CONFIG

# ---------------------------------------------------

genai.configure(
api_key=st.secrets["GEMINI_API_KEY"]
)

# ---------------------------------------------------

# HEADER

# ---------------------------------------------------

st.title("🛡️ AuditIQ")
st.subheader("AI-Powered Regulatory Intelligence Copilot")

st.info("""
AuditIQ helps auditors, compliance teams, and risk managers
find answers across policies, regulations, audit findings,
and operational evidence in seconds instead of hours.
""")

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("🛡️ AuditIQ")

    st.markdown("### Product Overview")

    st.info("""
    AuditIQ helps auditors and compliance teams
    instantly search policies, audit findings,
    regulatory guidelines, and evidence documents.
    """)

    st.markdown("### Core Capabilities")

    st.markdown("""
    ✅ Compliance Assessment

    ✅ Audit Finding Analysis

    ✅ Evidence Retrieval

    ✅ Regulatory Intelligence

    ✅ Cross-Document Reasoning
    """)

    st.markdown("### Sample Dataset")

    st.caption(
        "4 sample compliance documents are preloaded."
    )

# ---------------------------------------------------

# SAMPLE QUESTIONS

# ---------------------------------------------------

st.markdown("### Suggested Questions")

st.markdown("""

* Which audit findings remain open?
* Does PAY-2026-102 comply with company policy?
* Show evidence supporting AUD-2026-001.
* What approvals are required for payments above ₹10 lakh?
* What compliance risks exist?
  """)

# ---------------------------------------------------

# SYSTEM PROMPT

# ---------------------------------------------------

SYSTEM_PROMPT = """
You are AuditIQ, an enterprise-grade Regulatory Intelligence Copilot.

CRITICAL RULE:
Use ONLY information contained in the provided documents.

Do NOT use external knowledge.

If information is unavailable, respond:

'No supporting evidence found in uploaded documents.'

Your role is to assist:

* Auditors
* Compliance officers
* Risk managers
* Finance teams

You analyze:

* Policies
* Regulatory guidelines
* Audit reports
* Transaction records
* Approval logs
* Supporting evidence

Always provide:

# Executive Summary

# Relevant Documents

# Evidence

# Compliance Assessment

# Business Risk

# Recommended Actions

# Confidence Score

Confidence Score Guidelines:

95-100%
Direct evidence exists and answer is explicitly stated.

80-94%
Strong evidence exists but some inference is required.

60-79%
Partial evidence exists.

40-59%
Weak evidence exists.

0-39%
No supporting evidence exists.

Always explain WHY the confidence score was assigned.

Always connect information across documents when possible.

For example:

Policy
↓
Audit Finding
↓
Transaction Evidence
↓
Compliance Assessment

When possible, identify:

COMPLIANCE STATUS:

- Compliant
- Partially Compliant
- Non-Compliant

Provide the status explicitly.
"""

# ---------------------------------------------------

# LOAD SAMPLE DOCUMENTS

# ---------------------------------------------------

document_text = ""

sample_folder = "sample_docs"

loaded_sample_docs = []

if os.path.exists(sample_folder):


    for file in os.listdir(sample_folder):

        if file.endswith(".pdf"):

            loaded_sample_docs.append(file)

            pdf_path = os.path.join(sample_folder, file)

            reader = PdfReader(pdf_path)

            text = ""

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted

            document_text += f"\n\nDOCUMENT: {file}\n{text}"


# ---------------------------------------------------

# DISPLAY LOADED SAMPLE DOCS

# ---------------------------------------------------

import os

with st.expander("📁 View & Download Sample Documents", expanded=True):

    for doc in loaded_sample_docs:

        pdf_path = os.path.join(sample_folder, doc)

        with open(pdf_path, "rb") as file:

            st.download_button(
                label=f"📄 {doc}",
                data=file,
                file_name=doc,
                mime="application/pdf"
            )

# ---------------------------------------------------

# USER DOCUMENT UPLOAD

# ---------------------------------------------------

st.markdown("### Upload Additional Documents (Optional)")

uploaded_files = st.file_uploader(
"Upload PDF files",
type="pdf",
accept_multiple_files=True
)

if uploaded_files:

    for pdf in uploaded_files:

        reader = PdfReader(pdf)

        text = ""

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

        document_text += f"\n\nDOCUMENT: {pdf.name}\n{text}"

    st.success(
        f"{len(uploaded_files)} additional document(s) loaded."
    )

col1, col2, col3 = st.columns(3)

col1.metric(
    "Sample Documents",
    len(loaded_sample_docs)
)

col2.metric(
    "Uploaded Documents",
    len(uploaded_files) if uploaded_files else 0
)

col3.metric(
    "Knowledge Sources",
    len(loaded_sample_docs) +
    (len(uploaded_files) if uploaded_files else 0)
)

# ---------------------------------------------------

# QUESTION INPUT

# ---------------------------------------------------

question = st.text_area(
"Ask an Audit or Compliance Question"
)

# ---------------------------------------------------

# ANALYZE BUTTON

# ---------------------------------------------------

if st.button("Analyze"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Reviewing compliance records..."):

            model = genai.GenerativeModel(
                "gemini-1.5-flash-8b"
            )

            prompt = f"""
            {SYSTEM_PROMPT}

            The following documents are the ONLY source of truth.

            DOCUMENTS:

            {document_text}

            USER QUESTION:

            {question}
            """

            try:
                response = model.generate_content(prompt)
                response_text = response.text

                if "non-compliant" in response_text.lower():
                    st.error("🔴 Compliance Status: Non-Compliant")
                elif "partially compliant" in response_text.lower():
                    st.warning("🟠 Compliance Status: Partially Compliant")
                elif "compliant" in response_text.lower():
                    st.success("🟢 Compliance Status: Compliant")

                st.markdown(response_text)

            except Exception as e:
                st.error("⚠️ AuditIQ is temporarily unable to process this request.")
                st.info("This is likely due to free-tier Gemini API quota limits. Please try again in a few minutes.")

# ---------------------------------------------------

# FOOTER

# ---------------------------------------------------

st.markdown("---")

st.caption(
"AuditIQ • AI-Powered Regulatory Intelligence Copilot"
)
