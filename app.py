# app.py
import os
import re
import PyPDF2
import streamlit as st
from dotenv import load_dotenv


from ai_logic import generate_cold_email

# ---------- Setup ----------
st.set_page_config(page_title="AI Cold Email Assistant", page_icon="📧")
os.makedirs("static", exist_ok=True)

load_dotenv()  # only needed to ensure env is loaded for ai_logic

# ---------- UI ----------
st.title("📧 AI Cold Email Assistant for Job Applications")
st.caption(
    "Generate personalized cold emails using resumes and job descriptions.\n"
    "Provide ANY one of: Resume, Job Description, or Portfolio/LinkedIn/GitHub link."
)

name = st.text_input("Your Name")
role = st.text_input("Role you're applying for")
company = st.text_input("Company Name")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader(
        "Upload Resume (PDF or TXT)",
        type=["pdf", "txt"]
    )

with col2:
    portfolio_link = st.text_input(
        "Portfolio / LinkedIn / GitHub Link (optional)"
    )

job_description = st.text_area("Paste Job Description (optional)")

# ---------- Sidebar ----------
with st.sidebar:
    show_debug = st.checkbox("Show debug info", value=False)

    model_name = st.selectbox(
        "Groq model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
        ],
        index=0,
    )

    temperature = st.slider(
        "Creativity (temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )

generate_button = st.button("Generate Cold Email", type="primary")

# ---------- Helpers ----------
def clean(text: str) -> str:
    return (text or "").strip()

def read_resume(uploaded_file) -> str:
    """
    Read PDF or TXT resume and return plain text.
    File is saved to static/ to avoid Streamlit temp-buffer issues.
    """
    if not uploaded_file:
        return ""

    try:
        file_path = os.path.join("static", uploaded_file.name)
        data = uploaded_file.read()

        with open(file_path, "wb") as f:
            f.write(data)

        if uploaded_file.name.lower().endswith(".txt"):
            return data.decode("utf-8", errors="ignore")

        if uploaded_file.name.lower().endswith(".pdf"):
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""

            return re.sub(r"\n{3,}", "\n\n", text.strip())

    except Exception as e:
        st.error(f"Error reading resume: {e}")

    return ""

# ---------- Generate ----------
if generate_button:
    name_c = clean(name)
    role_c = clean(role)
    company_c = clean(company)
    link_c = clean(portfolio_link)
    jd_c = clean(job_description)

    resume_text = read_resume(resume_file)

    # At least one content source required
    have_source = bool(resume_text or jd_c or link_c)

    if not have_source:
        st.warning(
            "Please provide at least one source:\n"
            "• Resume\n• Job Description\n• Portfolio/LinkedIn/GitHub link"
        )
        st.stop()

    if show_debug:
        st.info(
            f"DEBUG → name='{name_c}', role='{role_c}', company='{company_c}', "
            f"resume_len={len(resume_text)}, jd_len={len(jd_c)}, link='{link_c}'"
        )

    try:
        with st.spinner("Generating cold email..."):
            email_text = generate_cold_email(
                name=name_c,
                role=role_c,
                company=company_c,
                portfolio_link=link_c,
                resume_text=resume_text,
                job_description=jd_c,
                model_name=model_name,
                temperature=temperature,
            )

        st.subheader("✅ Generated Cold Email")
        st.code(email_text, language="markdown")

    except Exception as e:
        st.error(f"Error generating email: {e}")
