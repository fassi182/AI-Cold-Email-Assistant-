# 🚀 AI Cold Email Assistant

An **AI-powered Cold Email Assistant** built using **Python, Fastapi,Streamlit, and Groq LLMs**.  
This tool helps users generate **personalized, professional cold emails** by combining their **resume, job description, and portfolio information**—making outreach faster, smarter, and recruiter-ready.

---

## 🚀 Live Demo
Check out the app here: https://vv6kbepru48uhndub3alxn.streamlit.app/
---

## ✨ Features

- 📄 Upload your **resume**
- 🧾 Paste a **job description**
- 🔗 Add your **portfolio / LinkedIn / GitHub link**
- 🤖 AI generates **custom cold emails**
- ⚡ Powered by **Groq LLMs** (fast inference)
- 🖥️ Clean and simple **Streamlit UI**
- 🛠️ REST API using **Fast API**
- 🔐 Secure API key handling via `.env`

---

## 🧠 How It Works

1. User uploads resume or provides text  
2. User enters job description  
3. AI analyzes skills, experience, and job requirements  
4. Generates a **tailored cold email**

---

## 🛠️ Tech Stack

- Python 3.10+
- Streamlit
- FastAPI REST API with Pydantic validation 
- Groq LLM API
- dotenv

---

## 📂 Project Structure

```
AI-Cold-Email-Assistant/
│
├── app.py
├── backend.py
├── ai_logic.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Installation & Setup for the ui 

```bash
git clone https://github.com/your-username/AI-Cold-Email-Assistant.git
cd AI-Cold-Email-Assistant
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---
## setup for access the endpoints of API
## Run Server

```bash
uvicorn main:app --reload
```
- Swagger docs: /docs

---

## API Endpoints

---
## POST /generate-email
```
{
  "name": "John Doe",
  "role": "Python Developer",
  "company": "TechCorp",
  "portfolio_link": "https://github.com/johndoe",
  "resume_text": "Experience in Python, FastAPI...",
  "job_description": "Looking for a dev with 3 years exp...",
  "model_name": "llama-3.3-70b-versatile",
  "temperature": 0.7
}
{
  "name": "John Doe",
  "role": "Python Developer",
  "company": "TechCorp",
  "portfolio_link": "https://github.com/johndoe",
  "resume_text": "Experience in Python, FastAPI...",
  "job_description": "Looking for a dev with 3 years exp...",
  "model_name": "llama-3.3-70b-versatile",
  "temperature": 0.7
}
```
---
## Response Example:
```
{
  "email": "Dear Hiring Manager, ...",
  "status": "success"
}
```

---
### GET /health
```
{
  "status": "alive",
  "version": "2.0.0"
}```
