from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Import your AI logic
from ai_logic import generate_cold_email

app = FastAPI(title="AI Cold Email Backend")

# ---------- Request Model ----------
class EmailRequest(BaseModel):
    name: str = ""
    role: str = ""
    company: str = ""
    portfolio_link: str = ""
    resume_text: str = ""
    job_description: str = ""
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7

# ---------- Endpoint ----------
@app.post("/generate-email")
async def generate_email(req: EmailRequest):
    try:
        email_text = generate_cold_email(
            name=req.name,
            role=req.role,
            company=req.company,
            portfolio_link=req.portfolio_link,
            resume_text=req.resume_text,
            job_description=req.job_description,
            model_name=req.model_name,
            temperature=req.temperature
        )
        return {"email": email_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
