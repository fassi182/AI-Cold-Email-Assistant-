import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

# Import your AI logic
# Ensure ai_logic.py exists in the same directory
try:
    from ai_logic import generate_cold_email
except ImportError:
    def generate_cold_email(**kwargs):
        return "AI Logic not found. Please ensure ai_logic.py is present."

# ---------------- Load environment variables ----------------
load_dotenv()

# Get API keys from .env (Example: API_KEYS=secret1,secret2)
API_KEYS = os.getenv("API_KEYS", "mysecretkey").split(",")

# ---------------- Configure logging ----------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------- FastAPI app ----------------
app = FastAPI(
    title="AI Cold Email Generator API",
    description="Backend service for generating job application cold emails",
    version="1.0.0"
)

# ---------------- Rate limiter ----------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

# ---------------- Security Scheme ----------------
# This enables the "Authorize" button in Swagger UI
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token provided in the Authorization header.
    The 'credentials' object automatically strips the 'Bearer ' prefix.
    """
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(
            status_code=403, 
            detail="Invalid or unauthorized API key"
        )
    return token

# ---------------- Request and Response Models ----------------
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

# ---------------- Endpoints ----------------

@app.post("/generate-email", response_model=EmailResponse)
@limiter.limit("10/minute")
def generate_email_endpoint(
    request: Request,
    payload: EmailRequest,
    auth: str = Depends(verify_api_key)
):
    """
    Generate a cold email using AI logic. 
    Requires Bearer Token Authorization.
    """
    logging.info(f"Request from API key: {auth[:4]}***, role={payload.role}, company={payload.company}")
    
    try:
        email_content = generate_cold_email(
            name=payload.name,
            role=payload.role,
            company=payload.company,
            portfolio_link=payload.portfolio_link,
            resume_text=payload.resume_text,
            job_description=payload.job_description,
            model_name=payload.model_name,
            temperature=payload.temperature
        )
        return {"email": email_content}
    except Exception as e:
        logging.error(f"Error generating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "api_keys_loaded": len(API_KEYS)}