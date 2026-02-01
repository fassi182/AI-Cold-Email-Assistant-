from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from ai_logic import generate_cold_email

app = FastAPI(
    title="AI Cold Email Service",
    description="A modular API for generating professional cold emails.",
    version="2.0.0"
)

# --- Data Schemas ---
class EmailRequest(BaseModel):
    # Field gives you metadata and default values for better API documentation
    name: str = Field(default="Candidate", example="John Doe")
    role: str = Field(default="", example="Python Developer")
    company: str = Field(default="", example="TechCorp")
    portfolio_link: str = Field(default="", example="https://github.com/johndoe")
    resume_text: str = Field(default="", example="Experience in Python, FastAPI...")
    job_description: str = Field(default="", example="Looking for a dev with 3 years exp...")
    model_name: str = "llama-3.3-70b-versatile"
    temperature: float = 0.7

class EmailResponse(BaseModel):
    email: str
    status: str = "success"

# --- Endpoints ---

@app.post("/generate-email", response_model=EmailResponse)
async def generate_email_endpoint(payload: EmailRequest):
    """
    Takes user data and returns a generated email string using the LangChain logic.
    """
    try:
        # Pass data directly to your logic layer
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
        
        return {"email": email_content, "status": "success"}

    except Exception as e:
        # If the AI provider (Groq) is down or API key is wrong, return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Confirms the server is running."""
    return {"status": "alive", "version": "2.0.0"}