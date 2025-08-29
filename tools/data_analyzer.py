# tools/data_analyzer.py

import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """
    Data analysis tools for processing research and business data
    """
    
    def __init__(self):
        logger.info("Data analyzer initialized")
    
    async def analyze_competitors(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitor information
        
        Args:
            competitor_data: Raw competitor research data
            
        Returns:
            Structured competitor analysis
        """
        analysis = {
            "top_competitors": [],
            "pricing_insights": {},
            "strengths": [],
            "weaknesses": [],
            "opportunities": []
        }
        
        # Process each competitor query result
        for query, data in competitor_data.items():
            if "pricing" in query.lower():
                # Extract pricing insights
                analysis["pricing_insights"][query] = self._extract_pricing_info(data)
            
            elif "reviews" in query.lower():
                # Extract strengths and weaknesses from reviews
                review_analysis = self._analyze_reviews(data)
                analysis["strengths"].extend(review_analysis.get("strengths", []))
                analysis["weaknesses"].extend(review_analysis.get("weaknesses", []))
            
            elif "competitors" in query.lower():
                # Extract top competitors
                analysis["top_competitors"] = self._extract_competitors(data)
        
        # Identify opportunities based on weaknesses
        analysis["opportunities"] = self._identify_opportunities(
            analysis["weaknesses"],
            analysis["pricing_insights"]
        )
        
        return analysis
    
    async def analyze_trends(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market trends
        
        Args:
            trend_data: Raw trend research data
            
        Returns:
            Structured trend analysis
        """
        analysis = {
            "emerging_trends": [],
            "declining_trends": [],
            "stable_trends": [],
            "seasonal_patterns": [],
            "growth_opportunities": []
        }
        
        for query, data in trend_data.items():
            answer = data.get("answer", "")
            
            # Simple keyword-based trend extraction
            if "growing" in answer.lower() or "increasing" in answer.lower():
                analysis["emerging_trends"].append({
                    "trend": query,
                    "description": answer[:200]
                })
            
            if "declining" in answer.lower() or "decreasing" in answer.lower():
                analysis["declining_trends"].append({
                    "trend": query,
                    "description": answer[:200]
                })
            
            if "seasonal" in answer.lower():
                analysis["seasonal_patterns"].append({
                    "pattern": query,
                    "description": answer[:200]
                })
        
        return analysis
    
    def _extract_pricing_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pricing information from research data"""
        answer = data.get("answer", "")
        
        # Simple extraction - would use NLP in production
        pricing_info = {
            "range": "15,000 - 60,000 COP",  # Default range
            "average": "35,000 COP",
            "insights": answer[:300] if answer else "No pricing data available"
        }
        
        return pricing_info
    
    def _analyze_reviews(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer reviews to extract strengths and weaknesses"""
        answer = data.get("answer", "")
        
        # Simple keyword-based analysis
        strengths = []
        weaknesses = []
        
        positive_keywords = ["excellent", "great", "amazing", "fast", "delicious", "fresh"]
        negative_keywords = ["slow", "cold", "expensive", "poor", "bad", "late"]
        
        answer_lower = answer.lower()
        
        for keyword in positive_keywords:
            if keyword in answer_lower:
                strengths.append(f"Customers appreciate {keyword} service/food")
        
        for keyword in negative_keywords:
            if keyword in answer_lower:
                weaknesses.append(f"Customers complain about {keyword} issues")
        
        return {
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5]
        }
    
    def _extract_competitors(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract competitor names and basic info"""
        answer = data.get("answer", "")
        
        # Placeholder - would use entity extraction in production
        competitors = [
            {"name": "Rappi Turbo", "type": "Platform"},
            {"name": "Muy", "type": "Restaurant Chain"},
            {"name": "Local Ghost Kitchens", "type": "Direct Competitor"}
        ]
        
        return competitors
    
    def _identify_opportunities(
        self,
        weaknesses: List[str],
        pricing_insights: Dict[str, Any]
    ) -> List[str]:
        """Identify opportunities based on competitor weaknesses"""
        opportunities = []
        
        if any("slow" in w.lower() for w in weaknesses):
            opportunities.append("Fast delivery (under 30 minutes) as differentiator")
        
        if any("expensive" in w.lower() for w in weaknesses):
            opportunities.append("Competitive pricing with combo deals")
        
        if any("cold" in w.lower() for w in weaknesses):
            opportunities.append("Better packaging to maintain food temperature")
        
        # Add generic opportunities
        opportunities.extend([
            "Focus on underserved dietary preferences (vegan, keto)",
            "Leverage social media for brand building",
            "Implement loyalty program for repeat customers"
        ])
        
        return opportunities[:5]