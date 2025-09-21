import httpx
import asyncio
from typing import Dict, List, Optional
from config import settings

class FactCheckService:
    """Service for checking against fact-checking databases"""
    
    def __init__(self):
        self.google_api_key = settings.google_fact_check_api_key
        self.timeout = settings.timeout_seconds
    
    async def check_all_databases(self, text: str) -> Dict:
        """Check text against all available fact-checking databases"""
        
        tasks = []
        
        # Google Fact Check Tools API
        if self.google_api_key:
            tasks.append(self._check_google_fact_check(text))
        
        # Add more fact-checking services here
        tasks.append(self._check_snopes_api(text))
        tasks.append(self._check_politifact_api(text))
        
        # Run all checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        combined_results = {
            "databases_checked": len(tasks),
            "results": [],
            "summary": {}
        }
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result.get("success"):
                combined_results["results"].append(result)
        
        # Generate summary
        combined_results["summary"] = self._generate_summary(combined_results["results"])
        
        return combined_results
    
    async def _check_google_fact_check(self, text: str) -> Dict:
        """Check Google Fact Check Tools API"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://factchecktools.googleapis.com/v1alpha1/claims:search",
                    params={
                        "key": self.google_api_key,
                        "query": text[:500],  # API has query length limits
                        "languageCode": "en",
                        "maxAgeDays": 365  # Only recent fact-checks
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    claims = data.get("claims", [])
                    
                    return {
                        "success": True,
                        "source": "Google Fact Check Tools",
                        "claims_found": len(claims),
                        "claims": claims[:5],  # Limit to top 5 results
                        "url": "https://toolbox.google.com/factcheck/"
                    }
                else:
                    return {
                        "success": False,
                        "source": "Google Fact Check Tools",
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "source": "Google Fact Check Tools",
                "error": str(e)
            }
    
    async def _check_snopes_api(self, text: str) -> Dict:
        """Check Snopes (placeholder - would need actual API access)"""
        
        # Snopes doesn't have a public API, but this shows the structure
        # In practice, you might scrape their search results or use a third-party service
        
        return {
            "success": True,
            "source": "Snopes",
            "claims_found": 0,
            "claims": [],
            "url": "https://www.snopes.com/",
            "note": "Manual verification recommended"
        }
    
    async def _check_politifact_api(self, text: str) -> Dict:
        """Check PolitiFact (placeholder - would need actual API access)"""
        
        # Similar to Snopes, PolitiFact doesn't have a public API
        # This is a placeholder showing how you'd structure the response
        
        return {
            "success": True,
            "source": "PolitiFact",
            "claims_found": 0,
            "claims": [],
            "url": "https://www.politifact.com/",
            "note": "Manual verification recommended"
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary of fact-checking database results"""
        
        total_claims = sum(result.get("claims_found", 0) for result in results)
        sources_checked = len(results)
        
        # Analyze claim ratings if available
        ratings = []
        for result in results:
            for claim in result.get("claims", []):
                # Extract ratings from Google Fact Check format
                for review in claim.get("claimReview", []):
                    rating = review.get("textualRating", "").lower()
                    if rating:
                        ratings.append(rating)
        
        # Categorize ratings
        positive_ratings = ["true", "correct", "accurate", "verified"]
        negative_ratings = ["false", "incorrect", "misleading", "pants on fire"]
        mixed_ratings = ["mixed", "half true", "mostly true", "mostly false"]
        
        rating_summary = {
            "positive": sum(1 for r in ratings if any(p in r for p in positive_ratings)),
            "negative": sum(1 for r in ratings if any(n in r for n in negative_ratings)),
            "mixed": sum(1 for r in ratings if any(m in r for m in mixed_ratings)),
            "total": len(ratings)
        }
        
        return {
            "total_claims_found": total_claims,
            "sources_checked": sources_checked,
            "rating_summary": rating_summary,
            "has_fact_checks": total_claims > 0
        }

class SourceCredibilityService:
    """Service for assessing source credibility"""
    
    def __init__(self):
        self.credible_sources = self._load_credible_sources()
    
    def _load_credible_sources(self) -> Dict:
        """Load database of credible sources with ratings"""
        
        return {
            # News Organizations (High Credibility)
            "reuters.com": {"credibility": 0.95, "bias": "center", "type": "news"},
            "apnews.com": {"credibility": 0.94, "bias": "center", "type": "news"},
            "bbc.com": {"credibility": 0.92, "bias": "center-left", "type": "news"},
            "npr.org": {"credibility": 0.91, "bias": "center-left", "type": "news"},
            
            # Fact-Checkers (High Credibility)
            "snopes.com": {"credibility": 0.88, "bias": "center", "type": "fact-check"},
            "factcheck.org": {"credibility": 0.90, "bias": "center", "type": "fact-check"},
            "politifact.com": {"credibility": 0.87, "bias": "center-left", "type": "fact-check"},
            
            # Academic/Government (Very High Credibility)
            "nih.gov": {"credibility": 0.98, "bias": "center", "type": "government"},
            "cdc.gov": {"credibility": 0.97, "bias": "center", "type": "government"},
            "who.int": {"credibility": 0.96, "bias": "center", "type": "international"},
            
            # Low Credibility Sources (for reference)
            "infowars.com": {"credibility": 0.15, "bias": "right", "type": "conspiracy"},
            "naturalnews.com": {"credibility": 0.20, "bias": "right", "type": "pseudoscience"},
        }
    
    def assess_source_credibility(self, url: str) -> Dict:
        """Assess the credibility of a source URL"""
        
        if not url:
            return {"credibility": 0.5, "assessment": "unknown"}
        
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        # Check against known sources
        if domain in self.credible_sources:
            source_info = self.credible_sources[domain]
            return {
                "credibility": source_info["credibility"],
                "bias": source_info.get("bias", "unknown"),
                "type": source_info.get("type", "unknown"),
                "assessment": self._get_credibility_label(source_info["credibility"])
            }
        
        # Default assessment for unknown sources
        return {
            "credibility": 0.5,
            "bias": "unknown",
            "type": "unknown",
            "assessment": "unknown - verify independently"
        }
    
    def _get_credibility_label(self, score: float) -> str:
        """Convert credibility score to human-readable label"""
        
        if score >= 0.9:
            return "very high credibility"
        elif score >= 0.8:
            return "high credibility"
        elif score >= 0.6:
            return "moderate credibility"
        elif score >= 0.4:
            return "low credibility"
        else:
            return "very low credibility"
    
    async def find_related_sources(self, text: str, limit: int = 5) -> List[Dict]:
        """Find credible sources related to the topic"""
        
        # This would integrate with news APIs, academic databases, etc.
        # For now, return curated high-credibility sources
        
        high_credibility_sources = [
            {
                "title": "Reuters Fact Check",
                "url": "https://www.reuters.com/fact-check/",
                "credibility_score": 0.95,
                "description": "Professional fact-checking by Reuters journalists"
            },
            {
                "title": "Associated Press Fact Check",
                "url": "https://apnews.com/hub/ap-fact-check",
                "credibility_score": 0.94,
                "description": "Comprehensive fact-checking from AP News"
            },
            {
                "title": "FactCheck.org",
                "url": "https://www.factcheck.org/",
                "credibility_score": 0.90,
                "description": "Nonpartisan fact-checking by Annenberg Public Policy Center"
            },
            {
                "title": "Snopes",
                "url": "https://www.snopes.com/",
                "credibility_score": 0.88,
                "description": "Comprehensive fact-checking and myth-busting"
            },
            {
                "title": "PolitiFact",
                "url": "https://www.politifact.com/",
                "credibility_score": 0.87,
                "description": "Political fact-checking with Truth-O-Meter ratings"
            }
        ]
        
        return high_credibility_sources[:limit]