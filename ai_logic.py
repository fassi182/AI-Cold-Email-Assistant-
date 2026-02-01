import os
from typing import Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# --- Configuration & Model Factory ---
def get_model(model_name: str, temperature: float):
    """
    Factory function to easily swap providers.
    In the future, you can add 'if model_name.startswith("gpt"): return ChatOpenAI(...)'
    """
    # Currently using Groq
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=model_name,
        temperature=temperature
    )

# --- Prompt Design ---
PROMPT = ChatPromptTemplate.from_template(
    """
You are an expert career advisor. 
Write a concise, friendly, and professional cold email for a job application.

- Name: {name}
- Role: {role}
- Company: {company}
- Portfolio/Link: {portfolio_link}
- Resume Text: {resume_text}
- Job Description: {job_description}

Requirements:
1) Mention a relevant subject line based on the details.
2) Personalize to the role/company.
3) Highlight 2–3 relevant skills/achievements.
4) Word count: 120–160 words.
5) Return ONLY the email body.

Best regards, {name}
"""
)

# --- Core Logic ---
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
    Uses LCEL (LangChain Expression Language) to chain the prompt, model, and parser.
    """
    
    # 1. Initialize the model via the factory
    llm = get_model(model_name, temperature)

    # 2. Define the Chain (Prompt -> LLM -> Output as String)
    # The '|' operator chains these components seamlessly
    chain = PROMPT | llm | StrOutputParser()

    # 3. Invoke the chain with a dictionary of inputs
    email_content = chain.invoke({
        "name": name or "Candidate",
        "role": role or "the position",
        "company": company or "your company",
        "portfolio_link": portfolio_link or "Not provided",
        "resume_text": resume_text or "Not provided",
        "job_description": job_description or "Not provided"
    })

    return email_content