import os
import re
import PyPDF2
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# ---------- Load Environment ----------
load_dotenv()# Try local environment variable first
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# If not found, try Streamlit secrets
if not GROQ_API_KEY and "GROQ_API_KEY" in st.secrets.get("GROQ", {}):
    GROQ_API_KEY = st.secrets["GROQ"]["GROQ_API_KEY"]

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found! Set it in .env (local) or Streamlit Secrets (cloud).")
# ---------- Helpers ----------
def nonempty(s) -> bool:
    return bool((s or "").strip())

def clean(s) -> str:
    return (s or "").strip()

def read_resume(file_path) -> str:
    """Read PDF/TXT resume to text."""
    if not file_path:
        return ""
    try:
        text = ""
        if file_path.lower().endswith(".txt"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif file_path.lower().endswith(".pdf"):
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        return re.sub(r"\n{3,}", "\n\n", text.strip())
    except Exception as e:
        return f"Error reading file: {e}"

# ---------- AI Logic ----------
def generate_email_locally(name, role, company, portfolio_link, resume_text, job_description,
                           model_name="llama-3.3-70b-versatile", temperature=0.7):
    """Generate email directly using ChatGroq."""
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=model_name,
        temperature=temperature
    )

    PROMPT = ChatPromptTemplate.from_template("""
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
0) Also mention the subject according to job description/role.
1) Personalize to the role/company (if given).
2) Highlight 2–3 highly relevant skills/achievements drawn from resume or link context.
3) Keep it ~120–160 words, natural (not robotic), with a polite CTA.
4) Close with "Best regards, {name}" if name is provided.

Return only the email body (no subject line).
""")

    final = PROMPT.format_messages(
        name=clean(name),
        role=clean(role),
        company=clean(company),
        portfolio_link=clean(portfolio_link),
        resume_text=resume_text or "",
        job_description=job_description or ""
    )
    resp = llm.invoke(final)
    return getattr(resp, "content", str(resp))
