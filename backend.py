# backend.py
import os
import logging
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ai_logic import generate_cold_email
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Keys (comma-separated in env)
API_KEYS = os.getenv("API_KEYS", "").split(",")

# FastAPI app
app = FastAPI(
    title="AI Cold Email Generator API",
    description="Backend service for generating job application cold emails",
    version="1.0.0"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

# ---------------- Models ----------------
class EmailRequest(BaseModel):
    name: str | None = ""
    role: str | None = ""
    company: str | None = ""
    portfolio_link: str | None = ""
    resume_text: str | None = ""
    job_description: str | None = ""
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7

class EmailResponse(BaseModel):
    email: str

# ---------------- Auth ----------------
def verify_api_key(authorization: str = Header(None)):
    """
    Validate API key from header.
    Example: Authorization: Bearer team1-key
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
    
    key = authorization.replace("Bearer ", "")
    if key not in API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return key

# ---------------- Endpoint ----------------
@app.post("/generate-email", response_model=EmailResponse)
@limiter.limit("10/minute")  # limit per IP
def generate_email(payload: EmailRequest, auth: str = Depends(verify_api_key)):
    logging.info(f"Request from API key: {auth}, role={payload.role}, company={payload.company}")
    try:
        email = generate_cold_email(
            name=payload.name,
            role=payload.role,
            company=payload.company,
            portfolio_link=payload.portfolio_link,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            model_name=payload.model_name,
            temperature=payload.temperature
        )
        logging.info(f"Email generated successfully for {payload.role} at {payload.company}")
        return {"email": email}
    except Exception as e:
        logging.error(f"Error generating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))
