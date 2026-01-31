# app.py
import os
import re
import requests
import PyPDF2
import streamlit as st

BACKEND_URL = "http://localhost:8000/generate-email"

st.set_page_config(page_title="AI Cold Email Assistant", page_icon="📧")
os.makedirs("static", exist_ok=True)

st.title("📧 AI Cold Email Assistant for Job Applications")

name = st.text_input("Your Name")
role = st.text_input("Role you're applying for")
company = st.text_input("Company Name")

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
with col2:
    portfolio_link = st.text_input("Portfolio / LinkedIn / GitHub Link")

job_description = st.text_area("Paste Job Description")

with st.sidebar:
    model_name = st.selectbox(
        "Groq model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "gemma2-9b-it"]
    )
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7)

def read_resume(uploaded_file) -> str:
    if not uploaded_file:
        return ""
    path = os.path.join("static", uploaded_file.name)
    data = uploaded_file.read()
    with open(path, "wb") as f:
        f.write(data)

    if uploaded_file.name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")

    text = ""
    reader = PyPDF2.PdfReader(path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return re.sub(r"\n{3,}", "\n\n", text.strip())

if st.button("Generate Cold Email", type="primary"):
    resume_text = read_resume(resume_file)

    if not (resume_text or job_description or portfolio_link):
        st.warning("Please provide at least one source")
        st.stop()

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

    with st.spinner("Generating email..."):
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        email = response.json()["email"]

    st.subheader("✅ Generated Cold Email")
    st.code(email, language="markdown")
