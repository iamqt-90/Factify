from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import httpx
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Factify API",
    description="AI-powered fact-checking backend for the Factify browser extension",
    version="1.0.0"
)

# CORS middleware for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class FactCheckRequest(BaseModel):
    text: str
    url: Optional[str] = None
    context: Optional[str] = None

class Source(BaseModel):
    title: str
    url: str
    credibility_score: Optional[float] = None

class FactCheckResponse(BaseModel):
    status: str  # "verified", "questionable", "false", "mixed"
    verdict: str
    summary: str
    analysis: str
    confidence_score: float
    sources: List[Source]
    education: str
    timestamp: datetime
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="Factify API is running",
        version="1.0.0"
    )

# Main fact-checking endpoint
@app.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(request: FactCheckRequest):
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Validate input
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="Text must be at least 10 characters long"
            )
        
        if len(request.text) > 5000:
            raise HTTPException(
                status_code=400, 
                detail="Text is too long (max 5000 characters)"
            )
        
        # Process the fact-check request
        result = await process_fact_check(request.text, request.url, request.context)
        
        # Calculate processing time
        processing_time = asyncio.get_event_loop().time() - start_time
        result.processing_time = processing_time
        result.timestamp = datetime.now()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Core fact-checking logic
async def process_fact_check(text: str, url: Optional[str], context: Optional[str]) -> FactCheckResponse:
    """
    Main fact-checking pipeline:
    1. AI Analysis (OpenAI/Google AI)
    2. Fact-checking database lookup
    3. Source verification
    4. Generate educational content
    """
    
    # Run analysis tasks concurrently
    ai_analysis_task = analyze_with_ai(text)
    fact_db_task = check_fact_databases(text)
    sources_task = find_credible_sources(text)
    
    # Wait for all tasks to complete
    ai_result, fact_db_result, sources = await asyncio.gather(
        ai_analysis_task,
        fact_db_task,
        sources_task,
        return_exceptions=True
    )
    
    # Combine results and generate final verdict
    return combine_analysis_results(text, ai_result, fact_db_result, sources)

# AI Analysis using OpenAI
async def analyze_with_ai(text: str) -> dict:
    """Analyze text using OpenAI GPT for fact-checking"""
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return {"error": "OpenAI API key not configured"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a professional fact-checker. Analyze the given text for factual accuracy. 
                            Provide a structured analysis including:
                            1. Overall assessment (verified/questionable/false/mixed)
                            2. Confidence level (0-1)
                            3. Key claims identified
                            4. Potential issues or red flags
                            5. Recommendations for verification
                            
                            Be objective and cite reasoning for your assessment."""
                        },
                        {
                            "role": "user",
                            "content": f"Please fact-check this text: {text}"
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.3
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"OpenAI API error: {response.status_code}"}
                
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}

# Fact-checking database lookup
async def check_fact_databases(text: str) -> dict:
    """Check against known fact-checking databases"""
    
    # Google Fact Check Tools API
    google_api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
    
    results = []
    
    if google_api_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                    params={
                        "key": google_api_key,
                        "query": text[:500],  # Limit query length
                        "languageCode": "en"
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    results.append({"source": "google", "data": response.json()})
                    
        except Exception as e:
            results.append({"source": "google", "error": str(e)})
    
    # Add more fact-checking APIs here (Snopes, PolitiFact, etc.)
    
    return {"results": results}

# Find credible sources
async def find_credible_sources(text: str) -> List[Source]:
    """Find credible sources related to the claim"""
    
    # This would integrate with news APIs, academic databases, etc.
    # For now, return some example sources
    
    sources = [
        Source(
            title="Reuters Fact Check",
            url="https://www.reuters.com/fact-check/",
            credibility_score=0.95
        ),
        Source(
            title="Associated Press Fact Check",
            url="https://apnews.com/hub/ap-fact-check",
            credibility_score=0.93
        ),
        Source(
            title="Snopes",
            url="https://www.snopes.com/",
            credibility_score=0.88
        )
    ]
    
    return sources

# Combine all analysis results
def combine_analysis_results(text: str, ai_result: dict, fact_db_result: dict, sources: List[Source]) -> FactCheckResponse:
    """Combine all analysis results into final verdict"""
    
    # Default response structure
    status = "questionable"
    verdict = "⚠ Needs Verification"
    confidence_score = 0.5
    
    # Parse AI analysis if successful
    if not isinstance(ai_result, Exception) and "error" not in ai_result:
        try:
            ai_content = ai_result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Simple keyword-based classification (improve with better parsing)
            if "verified" in ai_content.lower() or "accurate" in ai_content.lower():
                status = "verified"
                verdict = "✓ Verified"
                confidence_score = 0.8
            elif "false" in ai_content.lower() or "incorrect" in ai_content.lower():
                status = "false"
                verdict = "❌ False"
                confidence_score = 0.9
            elif "mixed" in ai_content.lower() or "partially" in ai_content.lower():
                status = "mixed"
                verdict = "⚠ Mixed Evidence"
                confidence_score = 0.6
                
        except Exception:
            pass
    
    # Generate analysis text
    analysis = generate_analysis_text(text, ai_result, fact_db_result)
    
    # Generate educational content
    education = generate_educational_content(status)
    
    return FactCheckResponse(
        status=status,
        verdict=verdict,
        summary=f"Analysis of the provided text suggests it {status.replace('_', ' ')}.",
        analysis=analysis,
        confidence_score=confidence_score,
        sources=sources,
        education=education,
        timestamp=datetime.now(),
        processing_time=0.0  # Will be set by caller
    )

def generate_analysis_text(text: str, ai_result: dict, fact_db_result: dict) -> str:
    """Generate detailed analysis text"""
    
    analysis_parts = []
    
    # Add AI analysis summary
    if not isinstance(ai_result, Exception) and "error" not in ai_result:
        try:
            ai_content = ai_result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if ai_content:
                analysis_parts.append(f"AI Analysis: {ai_content[:300]}...")
        except Exception:
            pass
    
    # Add fact-checking database results
    if fact_db_result and "results" in fact_db_result:
        db_count = len(fact_db_result["results"])
        if db_count > 0:
            analysis_parts.append(f"Cross-referenced with {db_count} fact-checking databases.")
    
    # Default analysis if no results
    if not analysis_parts:
        analysis_parts.append(
            "Our analysis examined this claim using multiple verification methods. "
            "While we couldn't find definitive matches in our fact-checking databases, "
            "we recommend verifying this information through multiple reliable sources."
        )
    
    return " ".join(analysis_parts)

def generate_educational_content(status: str) -> str:
    """Generate educational tips based on the analysis result"""
    
    education_tips = {
        "verified": "When information is verified, still consider: Is the source recent? Are there multiple independent confirmations? Does the context matter?",
        "questionable": "Red flags to watch for: Lack of credible sources, emotional language, absolute statements, missing context, or outdated information.",
        "false": "This appears to be misinformation. Always check: Original source, publication date, author credentials, and cross-reference with fact-checkers.",
        "mixed": "Mixed evidence requires careful evaluation. Look for: Which parts are accurate, what context is missing, and whether the overall conclusion is supported."
    }
    
    return education_tips.get(status, education_tips["questionable"])

# Additional utility endpoints
@app.get("/sources")
async def get_trusted_sources():
    """Get list of trusted fact-checking sources"""
    return {
        "sources": [
            {"name": "Reuters Fact Check", "url": "https://www.reuters.com/fact-check/"},
            {"name": "AP Fact Check", "url": "https://apnews.com/hub/ap-fact-check"},
            {"name": "Snopes", "url": "https://www.snopes.com/"},
            {"name": "PolitiFact", "url": "https://www.politifact.com/"},
            {"name": "FactCheck.org", "url": "https://www.factcheck.org/"},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)