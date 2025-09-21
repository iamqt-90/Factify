import httpx
import asyncio
from typing import Dict, Optional
from config import settings

class AIService:
    """Service for AI-powered fact-checking analysis"""
    
    def __init__(self):
        self.openai_api_key = settings.openai_api_key
        self.timeout = settings.timeout_seconds
    
    async def analyze_text(self, text: str, context: Optional[str] = None) -> Dict:
        """Analyze text using AI for fact-checking"""
        
        if not self.openai_api_key:
            return {"error": "OpenAI API key not configured"}
        
        try:
            prompt = self._build_fact_check_prompt(text, context)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": prompt,
                        "max_tokens": 1200,
                        "temperature": 0.2,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return self._parse_ai_response(result)
                else:
                    return {"error": f"OpenAI API error: {response.status_code}"}
                    
        except asyncio.TimeoutError:
            return {"error": "AI analysis timed out"}
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def _build_fact_check_prompt(self, text: str, context: Optional[str] = None) -> list:
        """Build the prompt for AI fact-checking"""
        
        system_prompt = """You are a professional fact-checker with expertise in identifying misinformation, verifying claims, and assessing source credibility. 

Your task is to analyze the given text and provide a structured fact-check assessment.

Return your analysis as a JSON object with these fields:
{
  "status": "verified|questionable|false|mixed",
  "confidence": 0.0-1.0,
  "key_claims": ["claim1", "claim2"],
  "assessment": "detailed analysis of factual accuracy",
  "red_flags": ["flag1", "flag2"] or [],
  "verification_suggestions": ["suggestion1", "suggestion2"],
  "reasoning": "explanation of your assessment"
}

Guidelines:
- "verified": Strong evidence supports the claims
- "questionable": Insufficient evidence or requires more verification  
- "false": Evidence contradicts the claims
- "mixed": Some claims accurate, others not

Be thorough but concise. Focus on factual accuracy, not opinions."""

        messages = [{"role": "system", "content": system_prompt}]
        
        user_content = f"Please fact-check this text: {text}"
        if context:
            user_content += f"\n\nAdditional context: {context}"
            
        messages.append({"role": "user", "content": user_content})
        
        return messages
    
    def _parse_ai_response(self, response: Dict) -> Dict:
        """Parse and validate AI response"""
        
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if content:
                import json
                parsed = json.loads(content)
                
                # Validate required fields
                required_fields = ["status", "confidence", "assessment"]
                for field in required_fields:
                    if field not in parsed:
                        return {"error": f"Missing required field: {field}"}
                
                # Validate status values
                valid_statuses = ["verified", "questionable", "false", "mixed"]
                if parsed["status"] not in valid_statuses:
                    parsed["status"] = "questionable"
                
                # Validate confidence range
                confidence = parsed.get("confidence", 0.5)
                parsed["confidence"] = max(0.0, min(1.0, float(confidence)))
                
                return {"success": True, "data": parsed}
            else:
                return {"error": "Empty response from AI"}
                
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from AI"}
        except Exception as e:
            return {"error": f"Failed to parse AI response: {str(e)}"}

# Alternative AI services
class AnthropicService:
    """Alternative AI service using Anthropic Claude"""
    
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.timeout = settings.timeout_seconds
    
    async def analyze_text(self, text: str, context: Optional[str] = None) -> Dict:
        """Analyze text using Anthropic Claude"""
        
        if not self.api_key:
            return {"error": "Anthropic API key not configured"}
        
        # Implementation for Anthropic API
        # Similar structure to OpenAI service
        return {"error": "Anthropic service not implemented yet"}

class GoogleAIService:
    """Google AI service using Gemini"""
    
    def __init__(self):
        self.api_key = settings.google_ai_api_key
        self.timeout = settings.timeout_seconds
    
    async def analyze_text(self, text: str, context: Optional[str] = None) -> Dict:
        """Analyze text using Google Gemini"""
        
        if not self.api_key:
            return {"error": "Google AI API key not configured"}
        
        # Implementation for Google AI API
        # Similar structure to OpenAI service
        return {"error": "Google AI service not implemented yet"}

# Factory function to get AI service
def get_ai_service(service_type: str = "openai") -> AIService:
    """Get AI service instance"""
    
    services = {
        "openai": AIService,
        "anthropic": AnthropicService,
        "google": GoogleAIService
    }
    
    service_class = services.get(service_type, AIService)
    return service_class()