# integrations/external/perplexity_client.py

import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class PerplexityClient:
    """
    Client for interacting with Perplexity AI API for internet research
    """
    
    def __init__(self):
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info("Perplexity client initialized")
    
    async def search(
        self,
        query: str,
        search_depth: str = "comprehensive",
        include_sources: bool = True,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Perform a search using Perplexity AI
        
        Args:
            query: Search query
            search_depth: "basic" or "comprehensive"
            include_sources: Whether to include source citations
            max_tokens: Maximum tokens in response
            
        Returns:
            Search results with answer and sources
        """
        try:
            payload = {
                "model": "pplx-70b-online",
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "search_domain_filter": ["perplexity.ai"],
                "return_citations": include_sources,
                "search_recency_filter": "month"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse response
                        result = {
                            "query": query,
                            "answer": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "sources": [],
                            "related_questions": []
                        }
                        
                        # Extract sources if available
                        if include_sources and "citations" in data:
                            result["sources"] = data["citations"]
                        
                        logger.info(f"Perplexity search successful for: {query[:50]}...")
                        return result
                        
                    else:
                        error_msg = await response.text()
                        logger.error(f"Perplexity API error: {error_msg}")
                        return {"error": f"API error: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Perplexity search failed: {str(e)}")
            return {"error": str(e)}
    
    async def search_with_context(
        self,
        query: str,
        context: str,
        search_depth: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Perform a search with additional context
        
        Args:
            query: Main search query
            context: Additional context to guide the search
            search_depth: Search depth level
            
        Returns:
            Contextualized search results
        """
        enhanced_query = f"""
        Context: {context}
        
        Question: {query}
        
        Please provide a comprehensive answer based on current information from the internet.
        """
        
        return await self.search(enhanced_query, search_depth)
    
    async def multi_search(
        self,
        queries: List[str],
        search_depth: str = "standard"
    ) -> List[Dict[str, Any]]:
        """
        Perform multiple searches
        
        Args:
            queries: List of search queries
            search_depth: Search depth for all queries
            
        Returns:
            List of search results
        """
        results = []
        
        for query in queries:
            result = await self.search(query, search_depth)
            results.append(result)
        
        return results
    
    async def research_topic(
        self,
        topic: str,
        aspects: List[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive research on a topic covering multiple aspects
        
        Args:
            topic: Main research topic
            aspects: Specific aspects to research
            
        Returns:
            Comprehensive research findings
        """
        if not aspects:
            aspects = [
                "current trends",
                "market size and growth",
                "key players",
                "opportunities",
                "challenges",
                "future outlook"
            ]
        
        research_findings = {
            "topic": topic,
            "aspects": {}
        }
        
        for aspect in aspects:
            query = f"{topic} {aspect} Colombia 2024"
            result = await self.search(query, "comprehensive")
            research_findings["aspects"][aspect] = result
        
        # Synthesize findings
        synthesis_query = f"""
        Based on research about {topic} in Colombia, provide:
        1. Executive summary
        2. Key findings
        3. Strategic recommendations
        """
        
        synthesis = await self.search(synthesis_query, "comprehensive")
        research_findings["synthesis"] = synthesis
        
        return research_findings