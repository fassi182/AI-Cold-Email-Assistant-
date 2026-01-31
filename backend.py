# backend.py
from fastapi import FastAPI
from pydantic import BaseModel
from ai_logic import generate_cold_email

app = FastAPI(title="AI Cold Email Backend")

class EmailRequest(BaseModel):
    name: str = ""
    role: str = ""
    company: str = ""
    portfolio_link: str = ""
    resume_text: str = ""
    job_description: str = ""
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7

class EmailResponse(BaseModel):
    email: str

@app.post("/generate-email", response_model=EmailResponse)
def generate_email(data: EmailRequest):
    email = generate_cold_email(
        name=data.name,
        role=data.role,
        company=data.company,
        portfolio_link=data.portfolio_link,
        resume_text=data.resume_text,
        job_description=data.job_description,
        model_name=data.model_name,
        temperature=data.temperature
    )
    return {"email": email}
