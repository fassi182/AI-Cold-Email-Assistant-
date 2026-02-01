# ai_logic.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Please set it in .env or cloud environment variables.")

# Prompt template
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
0) Also mention the subject according to job description/role or as given in description
1) Personalize to the role/company (if given)
2) Highlight 2–3 highly relevant skills/achievements from resume or link context
3) Keep it ~120–160 words, natural (not robotic), with a polite CTA
4) Close with "Best regards, {name}" if name is provided

Return only the email body (no subject line).
"""
)

def generate_cold_email(
    name: str,
    role: str,
    company: str,
    portfolio_link: str,
    resume_text: str,
    job_description: str,
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7
) -> str:
    """
    Core AI function used by FastAPI or any frontend.
    """
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=model_name,
        temperature=temperature
    )

    messages = PROMPT.format_messages(
        name=name or "",
        role=role or "",
        company=company or "",
        portfolio_link=portfolio_link or "",
        resume_text=resume_text or "",
        job_description=job_description or ""
    )

    response = llm.invoke(messages)
    return getattr(response, "content", str(response))
