from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from ai_logic import generate_email_locally
from fastapi.middleware.cors import CORSMiddleware

# ---------- FastAPI App ----------
app = FastAPI(
    title="AI Cold Email Assistant Backend",
    description="API endpoints for generating personalized cold emails",
    version="1.0"
)

# Enable CORS so frontend can call API from different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or list of allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request Schema ----------
class EmailRequest(BaseModel):
    name: Optional[str] = ""
    role: Optional[str] = ""
    company: Optional[str] = ""
    portfolio_link: Optional[str] = ""
    resume_text: Optional[str] = ""
    job_description: Optional[str] = ""
    model_name: Optional[str] = "llama-3.3-70b-versatile"
    temperature: Optional[float] = 0.7

# ---------- Endpoint ----------
@app.post("/generate-email")
def generate_email(request: EmailRequest):
    """
    Generate a personalized cold email based on input data.
    """
    email_text = generate_email_locally(
        name=request.name,
        role=request.role,
        company=request.company,
        portfolio_link=request.portfolio_link,
        resume_text=request.resume_text,
        job_description=request.job_description,
        model_name=request.model_name,
        temperature=request.temperature
    )
    return {"email": email_text}
