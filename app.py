import os
import re
import PyPDF2
import streamlit as st
import requests
from requests.exceptions import RequestException
from ai_logic import generate_email_locally

# ---------- Config ----------
st.set_page_config(page_title="AI Cold Email Assistant", page_icon="📧")
os.makedirs("static", exist_ok=True)

BACKEND_URL = "http://localhost:8000/generate-email"  # Local backend

# ---------- UI ----------
st.title("📧 AI Cold Email Assistant")
st.caption("Generate personalized cold emails using Resume, Job Description, or Portfolio Link")

name = st.text_input("Your Name")
role = st.text_input("Role you're applying for")
company = st.text_input("Company Name")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"])
with col2:
    portfolio_link = st.text_input("Portfolio / LinkedIn / GitHub Link (optional)")

job_description = st.text_area("Paste Job Description (optional)")

model_name = st.selectbox(
    "Groq model",
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"],
    index=0
)
temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.7, 0.1)

generate_button = st.button("Generate Cold Email", type="primary")

# ---------- Read Resume ----------
from ai_logic import read_resume, generate_email_locally

def read_resume_streamlit(uploaded_file):
    if not uploaded_file:
        return ""
    file_path = os.path.join("static", uploaded_file.name)
    data = uploaded_file.read()
    with open(file_path, "wb") as f:
        f.write(data)
    return read_resume(file_path)

# ---------- Generate ----------
if generate_button:
    resume_text = read_resume_streamlit(resume_file)

    payload = {
        "name": name,
        "role": role,
        "company": company,
        "portfolio_link": portfolio_link,
        "resume_text": resume_text,
        "job_description": job_description,
        "model_name": model_name,
        "temperature": temperature
    }

    email_text = ""
    # Try backend first
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        if response.status_code == 200:
            email_text = response.json().get("email", "")
        else:
            email_text = f"Backend error: {response.text}"
    except RequestException:
        # Backend unavailable, call AI logic directly
        email_text = generate_email_locally(
            name=name,
            role=role,
            company=company,
            portfolio_link=portfolio_link,
            resume_text=resume_text,
            job_description=job_description,
            model_name=model_name,
            temperature=temperature
        )

    st.subheader("✅ Generated Cold Email")
    st.code(email_text, language="markdown")
