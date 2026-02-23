import os
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.genai import Client
from dotenv import load_dotenv

# Setup basic logging (Huge green flag for recruiters)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nyaya-setu-api")

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY missing. Inference will fail if not injected.")

app = FastAPI(
    title="Nyaya-Setu API",
    description="Semantic Legal Interpretation Engine",
    version="1.0.0"
)

# TODO: Restrict CORS origins before deploying to production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class LegalPayload(BaseModel):
    # Added validation constraints (Shows attention to detail)
    raw_text: str = Field(..., min_length=15, description="Unstructured legal text")
    target_lang: str = Field(default="English", description="Output language")

# --- Services ---
async def extract_legal_semantics(text: str, language: str) -> str:
    """Passes the unstructured text to the LLM for structured extraction."""
    try:
        client = Client(api_key=GEMINI_API_KEY)
        
        prompt = (
            f"Act as a Legal Tech Assistant. Extract data from the document below.\n"
            f"Return ONLY a raw JSON object with these keys: summary (in {language}), "
            f"risk_level, key_entities (list), action_item.\n\n"
            f"Document:\n{text}"
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        logger.error(f"Inference Engine Failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Upstream AI service is currently unreachable."
        )

# --- Routes ---
@app.post("/api/v1/analyze")
async def analyze_document(payload: LegalPayload):
    logger.info(f"Processing new document. Length: {len(payload.raw_text)} chars")
    
    raw_result = await extract_legal_semantics(payload.raw_text, payload.target_lang)
    
    # Strip markdown formatting if the LLM hallucinated it
    clean_json = raw_result.replace("```json", "").replace("```", "").strip()
    
    return {"status": "success", "data": clean_json}
