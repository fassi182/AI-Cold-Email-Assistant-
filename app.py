# app.py
import os
import re
import io
import PyPDF2
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate

# ---------- Setup ----------
st.set_page_config(page_title="AI Cold Email Assistant", page_icon="📧")
os.makedirs("static", exist_ok=True)  # ensure 'static/' exists

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("Please set your GROQ_API_KEY in a .env file or environment variables!")
    st.stop()

# ---------- UI ----------
st.title("📧 AI Cold Email Assistant (Groq Cloud)")
st.caption("Provide ANY one of: Resume, Job Description, or a Portfolio/LinkedIn/GitHub link. Name/Role/Company help personalize the email.")

name = st.text_input("Your Name")
role = st.text_input("Role you're applying for")
company = st.text_input("Company Name")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
with col2:
    portfolio_link = st.text_input("Portfolio / LinkedIn / GitHub Link (optional)")

job_description = st.text_area("Paste Job Description (optional)")

# Debug helper
with st.sidebar:
    show_debug = st.checkbox("Show debug info", value=False)
    model_name = st.selectbox(
        "Groq model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
        index=0
    )
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.7, 0.1)

generate_button = st.button("Generate Cold Email", type="primary")

# ---------- Helpers ----------
def nonempty(s) -> bool:
    return bool((s or "").strip())

def clean(s) -> str:
    return (s or "").strip()

def read_resume(uploaded_file) -> str:
    """Read PDF/TXT resume to text. Saves a copy under static/ to avoid temp-buffer issues."""
    if not uploaded_file:
        return ""
    try:
        file_path = os.path.join("static", uploaded_file.name)
        data = uploaded_file.read()
        with open(file_path, "wb") as f:
            f.write(data)

        if uploaded_file.name.lower().endswith(".txt"):
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                return data.decode("latin-1", errors="ignore")

        if uploaded_file.name.lower().endswith(".pdf"):
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text
            return re.sub(r"\n{3,}", "\n\n", text.strip())
    except Exception as e:
        st.error(f"Error reading resume: {e}")
    return ""

# ---------- LLM ----------
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name=model_name,           # uses sidebar selection
    temperature=temperature
)

PROMPT = ChatPromptTemplate.from_template(
    """
You are an expert career advisor.
Write a concise, friendly, and professional cold email for a job application.

Base the email on any provided sources below. If a source is missing, ignore it.
- Name: {name}
- Role: {role}
- Company: {company}
- Portfolio/Link: {portfolio_link}
- Resume Text: {resume_text}
- Job Description: {job_description}

Requirements:
0) also mentioned the subject according to job descperion/role or as given in descrption
1) Personalize to the role/company (if given).
2) Highlight 2–3 highly relevant skills/achievements drawn from resume or link context.
3) Keep it ~120–160 words, natural (not robotic), with a polite CTA.
4) Close with "Best regards, {name}" if name is provided.


Return only the email body (no subject line).
"""
)

# ---------- Generate ----------
if generate_button:
    name_c = clean(name)
    role_c = clean(role)
    company_c = clean(company)
    jd_c = clean(job_description)
    link_c = clean(portfolio_link)

    resume_text = read_resume(resume_file)

    # Validation that won't misfire:
    # 1) At least ONE content source (resume OR job description OR link)
    have_source = bool(resume_text.strip() or jd_c or link_c)

    # 2) Name/Role/Company are not strictly required, but recommended.
    #    If you want them required, set `require_identity = True`.
    require_identity = False
    missing = []
    if require_identity:
        if not name_c: missing.append("Name")
        if not role_c: missing.append("Role")
        if not company_c: missing.append("Company")

    if not have_source:
        st.warning("Please provide at least one source: Resume, Job Description, or Portfolio/LinkedIn/GitHub link.")
        st.stop()

    if missing:
        st.warning("Please fill: " + ", ".join(missing))
        st.stop()

    if show_debug:
        st.info(
            f"DEBUG → name:'{name_c}', role:'{role_c}', company:'{company_c}', "
            f"len(resume_text):{len(resume_text)}, len(job_description):{len(jd_c)}, link:'{link_c}'"
        )

    try:
        final = PROMPT.format_messages(
            name=name_c,
            role=role_c,
            company=company_c,
            portfolio_link=link_c,
            resume_text=resume_text,
            job_description=jd_c
        )
        resp = llm.invoke(final)
        email_text = getattr(resp, "content", str(resp))
        st.subheader("✅ Generated Cold Email")
        st.code(email_text, language="markdown")
    except Exception as e:
        st.error(f"Error generating email: {e}")
