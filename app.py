import os
import re
import io
import PyPDF2
import streamlit as st

# Detect if we're running on Streamlit Cloud
ON_STREAMLIT_CLOUD = os.getenv("STREAMLIT_SERVER_PORT") is not None

# ---------- Setup ----------
st.set_page_config(page_title="AI Cold Email Assistant", page_icon="📧")
os.makedirs("static", exist_ok=True)  # ensure 'static/' exists

# ---------- UI ----------
st.title("📧 AI Cold Email Assistant for job applications")
st.caption("Generate personalized cold emails for job applications using resumes and job descriptions")
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
        "Model",
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

# ---------- Generate ----------
if generate_button:
    name_c = clean(name)
    role_c = clean(role)
    company_c = clean(company)
    jd_c = clean(job_description)
    link_c = clean(portfolio_link)
    resume_text = read_resume(resume_file)

    # Validation
    have_source = bool(resume_text.strip() or jd_c or link_c)
    if not have_source:
        st.warning("Please provide at least one source: Resume, Job Description, or Portfolio/LinkedIn/GitHub link.")
        st.stop()

    try:
        if ON_STREAMLIT_CLOUD:
            # ----- Call AI logic directly -----
            from ai_logic import generate_cold_email

            email_text = generate_cold_email(
                name=name_c,
                role=role_c,
                company=company_c,
                portfolio_link=link_c,
                resume_text=resume_text,
                job_description=jd_c,
                model_name=model_name,
                temperature=temperature
            )

        else:
            # ----- Call FastAPI backend locally -----
            import requests

            BACKEND_URL = "http://localhost:8000/generate-email"
            payload = {
                "name": name_c,
                "role": role_c,
                "company": company_c,
                "portfolio_link": link_c,
                "resume_text": resume_text,
                "job_description": jd_c,
                "model_name": model_name,
                "temperature": temperature
            }

            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()
            email_text = response.json().get("email", "Error: No email returned from backend")

        # Show result
        st.subheader("✅ Generated Cold Email")
        st.code(email_text, language="markdown")

    except Exception as e:
        st.error(f"Error generating email: {e}")
