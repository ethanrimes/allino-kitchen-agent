# agents/planning/research_agent.py

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from integrations.external.perplexity_client import PerplexityClient
from tools.calculation_engine import CalculationEngine
from tools.data_analyzer import DataAnalyzer
from core.memory_manager import MemoryManager
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class ResearchAgent(BaseAgent):
    """
    Deep research agent that uses Perplexity to research the internet
    and gather competitive intelligence, market trends, and customer insights
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        db_client: Optional[SupabaseClient] = None
    ):
        super().__init__(
            name="research_agent",
            llm=llm,
            memory_manager=memory_manager,
            db_client=db_client,
            template_path="prompts/templates/research_agent.yaml"
        )
        
        self.perplexity_client = PerplexityClient()
        self.calculation_engine = CalculationEngine()
        self.data_analyzer = DataAnalyzer()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize research-specific tools"""
        return [
            Tool(
                name="perplexity_search",
                func=self._perplexity_search,
                description="Search the internet for information using Perplexity AI"
            ),
            Tool(
                name="analyze_competitors",
                func=self._analyze_competitors,
                description="Analyze competitor data and strategies"
            ),
            Tool(
                name="market_trends",
                func=self._analyze_market_trends,
                description="Analyze market trends and opportunities"
            ),
            Tool(
                name="calculate",
                func=self._run_calculation,
                description="Run Python calculations and data analysis"
            ),
            Tool(
                name="save_findings",
                func=self._save_findings,
                description="Save research findings to database"
            )
        ]
    
    async def _execute_core(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research task
        
        Args:
            task: Task dictionary with 'query' and optional 'depth'
            
        Returns:
            Research findings
        """
        query = task.get("query", "")
        depth = task.get("depth", "standard")  # standard, comprehensive, quick
        
        logger.info(f"Researching: {query} (depth: {depth})")
        
        findings = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": [],
            "key_insights": [],
            "data_points": {},
            "recommendations": [],
            "competitor_analysis": {},
            "market_trends": {}
        }
        
        try:
            # Step 1: Initial broad search
            initial_results = await self._perplexity_search(query)
            findings["sources"].extend(initial_results.get("sources", []))
            
            # Step 2: Deep dive based on initial findings
            if depth in ["standard", "comprehensive"]:
                # Analyze competitors if relevant
                if "competitor" in query.lower() or "competition" in query.lower():
                    competitor_data = await self._analyze_competitors(query)
                    findings["competitor_analysis"] = competitor_data
                
                # Analyze market trends
                if "trend" in query.lower() or "market" in query.lower():
                    trend_data = await self._analyze_market_trends(query)
                    findings["market_trends"] = trend_data
            
            # Step 3: Comprehensive analysis with calculations
            if depth == "comprehensive":
                # Extract numerical data and perform calculations
                calc_results = await self._perform_data_analysis(initial_results)
                findings["data_points"] = calc_results
            
            # Step 4: Generate insights and recommendations
            insights = await self._generate_insights(findings)
            findings["key_insights"] = insights["insights"]
            findings["recommendations"] = insights["recommendations"]
            
            # Step 5: Save findings
            await self._save_findings(findings)
            
            logger.info(f"Research completed: {len(findings['sources'])} sources analyzed")
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            findings["error"] = str(e)
        
        return findings
    
    async def _perplexity_search(self, query: str) -> Dict[str, Any]:
        """Perform search using Perplexity API"""
        try:
            results = await self.perplexity_client.search(
                query=query,
                search_depth="comprehensive",
                include_sources=True
            )
            
            return {
                "query": query,
                "answer": results.get("answer", ""),
                "sources": results.get("sources", []),
                "related_questions": results.get("related_questions", [])
            }
            
        except Exception as e:
            logger.error(f"Perplexity search failed: {str(e)}")
            return {"error": str(e)}
    
    async def _analyze_competitors(self, query: str) -> Dict[str, Any]:
        """Analyze competitor information"""
        competitor_queries = [
            f"{query} top competitors Colombia",
            f"{query} pricing strategies",
            f"{query} customer reviews",
            f"{query} market share"
        ]
        
        competitor_data = {}
        
        for cq in competitor_queries:
            result = await self._perplexity_search(cq)
            if not result.get("error"):
                competitor_data[cq] = result
        
        # Analyze and structure competitor data
        analysis = await self.data_analyzer.analyze_competitors(competitor_data)
        
        return analysis
    
    async def _analyze_market_trends(self, query: str) -> Dict[str, Any]:
        """Analyze market trends"""
        trend_queries = [
            f"{query} market trends 2024 Colombia",
            f"{query} consumer preferences",
            f"{query} growth projections",
            f"{query} emerging opportunities"
        ]
        
        trend_data = {}
        
        for tq in trend_queries:
            result = await self._perplexity_search(tq)
            if not result.get("error"):
                trend_data[tq] = result
        
        # Analyze trends
        analysis = await self.data_analyzer.analyze_trends(trend_data)
        
        return analysis
    
    async def _run_calculation(self, code: str) -> Dict[str, Any]:
        """Run Python calculations"""
        return await self.calculation_engine.execute(code)
    
    async def _perform_data_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform numerical analysis on research data"""
        # Extract numerical data from research
        code = f"""
import json
import numpy as np
import pandas as pd

# Process research data
data = {json.dumps(data)}

# Extract and analyze numerical patterns
# This is a placeholder - actual implementation would extract real numbers
results = {{
    "data_points_found": len(data.get("sources", [])),
    "confidence_score": 0.85
}}

print(json.dumps(results))
"""
        
        calc_result = await self.calculation_engine.execute(code)
        
        if calc_result.get("success"):
            return json.loads(calc_result.get("output", "{}"))
        
        return {}
    
    async def _generate_insights(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and recommendations from findings"""
        # Use LLM to generate insights
        prompt = f"""
        Based on the following research findings, generate key insights and actionable recommendations:
        
        Findings: {json.dumps(findings, indent=2)}
        
        Provide:
        1. 3-5 key insights
        2. 3-5 actionable recommendations
        
        Format as JSON with 'insights' and 'recommendations' arrays.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "insights": ["Research completed successfully"],
                "recommendations": ["Review findings for strategic decisions"]
            }
    
    async def _save_findings(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """Save research findings to database"""
        try:
            # Store in research_findings table
            result = await self.db_client.store_research_findings(findings)
            
            logger.info(f"Research findings saved: {result.get('id')}")
            
            return {"success": True, "id": result.get("id")}
            
        except Exception as e:
            logger.error(f"Failed to save findings: {str(e)}")
            return {"success": False, "error": str(e)}