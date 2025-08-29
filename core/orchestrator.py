# core/orchestrator.py

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.memory_manager import MemoryManager
from core.state_manager import StateManager
from agents.planning.research_agent import ResearchAgent
from agents.planning.menu_creation_agent import MenuCreationAgent
from agents.planning.demand_forecasting_agent import DemandForecastingAgent
from agents.marketing.social_media_orchestration_agent import SocialMediaOrchestrationAgent
from agents.marketing.content_creation_agent import ContentCreationAgent
from database.supabase_client import SupabaseClient
from config.settings import settings

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MainOrchestrator:
    """
    Main orchestration engine that coordinates all agents and manages
    the overall business operations
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=settings.agent_temperature,
            model="gpt-4-turbo-preview",
            openai_api_key=settings.openai_api_key
        )
        
        self.memory_manager = MemoryManager()
        self.state_manager = StateManager()
        self.db_client = SupabaseClient()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Task queue
        self.task_queue: List[Dict[str, Any]] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("MainOrchestrator initialized successfully")
    
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all agent instances"""
        agents = {
            "research": ResearchAgent(
                llm=self.llm,
                memory_manager=self.memory_manager,
                db_client=self.db_client
            ),
            "menu_creation": MenuCreationAgent(
                llm=self.llm,
                memory_manager=self.memory_manager,
                db_client=self.db_client
            ),
            "demand_forecasting": DemandForecastingAgent(
                llm=self.llm,
                memory_manager=self.memory_manager,
                db_client=self.db_client
            ),
            "social_media": SocialMediaOrchestrationAgent(
                llm=self.llm,
                memory_manager=self.memory_manager,
                db_client=self.db_client
            ),
            "content_creation": ContentCreationAgent(
                llm=self.llm,
                memory_manager=self.memory_manager,
                db_client=self.db_client
            )
        }
        
        logger.info(f"Initialized {len(agents)} agents")
        return agents
    
    async def execute_planning_cycle(self) -> Dict[str, Any]:
        """
        Execute the main planning cycle:
        1. Research market and competitors
        2. Create/update menu based on research
        3. Forecast demand
        4. Create social media content
        5. Post to social channels
        """
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "started",
            "phases": {}
        }
        
        try:
            # Phase 1: Market Research
            logger.info("Starting Phase 1: Market Research")
            research_results = await self._execute_research_phase()
            results["phases"]["research"] = research_results
            
            # Phase 2: Menu Creation/Optimization
            logger.info("Starting Phase 2: Menu Creation")
            menu_results = await self._execute_menu_creation_phase(research_results)
            results["phases"]["menu_creation"] = menu_results
            
            # Phase 3: Demand Forecasting
            logger.info("Starting Phase 3: Demand Forecasting")
            forecast_results = await self._execute_forecasting_phase(menu_results)
            results["phases"]["forecasting"] = forecast_results
            
            # Phase 4: Content Creation
            logger.info("Starting Phase 4: Content Creation")
            content_results = await self._execute_content_creation_phase(menu_results)
            results["phases"]["content_creation"] = content_results
            
            # Phase 5: Social Media Posting
            logger.info("Starting Phase 5: Social Media Posting")
            posting_results = await self._execute_social_posting_phase(
                menu_results, 
                content_results
            )
            results["phases"]["social_posting"] = posting_results
            
            results["status"] = "completed"
            
            # Store results in database
            await self._store_cycle_results(results)
            
            logger.info("Planning cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Planning cycle failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    async def _execute_research_phase(self) -> Dict[str, Any]:
        """Execute market research phase"""
        research_agent = self.agents["research"]
        
        # Research topics
        topics = [
            "Colombian food delivery market trends 2024",
            "Popular ghost kitchen cuisines in Bogotá",
            "Food pricing strategies Colombia",
            "Competitor analysis ghost kitchens Colombia",
            "Customer preferences food delivery Colombia"
        ]
        
        research_results = {}
        for topic in topics:
            result = await research_agent.execute({
                "task": "research",
                "query": topic,
                "depth": "comprehensive"
            })
            research_results[topic] = result
        
        return research_results
    
    async def _execute_menu_creation_phase(
        self, 
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute menu creation/optimization phase"""
        menu_agent = self.agents["menu_creation"]
        
        menu_results = await menu_agent.execute({
            "task": "create_menu",
            "research_data": research_results,
            "constraints": {
                "max_items": 20,
                "price_range_cop": {"min": 15000, "max": 80000},
                "cuisine_focus": "fusion",
                "dietary_options": ["vegetarian", "gluten-free"]
            }
        })
        
        return menu_results
    
    async def _execute_forecasting_phase(
        self, 
        menu_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute demand forecasting phase"""
        forecast_agent = self.agents["demand_forecasting"]
        
        forecast_results = await forecast_agent.execute({
            "task": "forecast_demand",
            "menu_items": menu_results.get("items", []),
            "horizon_days": 30,
            "methods": ["time_series", "regression", "ml_ensemble"]
        })
        
        return forecast_results
    
    async def _execute_content_creation_phase(
        self, 
        menu_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute content creation phase"""
        content_agent = self.agents["content_creation"]
        
        content_results = {}
        platforms = ["instagram", "facebook", "whatsapp"]
        
        for platform in platforms:
            content = await content_agent.execute({
                "task": "create_content",
                "platform": platform,
                "menu_data": menu_results,
                "content_type": "menu_announcement",
                "language": "spanish",
                "tone": "casual_friendly"
            })
            content_results[platform] = content
        
        return content_results
    
    async def _execute_social_posting_phase(
        self, 
        menu_results: Dict[str, Any],
        content_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute social media posting phase"""
        social_agent = self.agents["social_media"]
        
        posting_results = await social_agent.execute({
            "task": "post_content",
            "content": content_results,
            "menu_data": menu_results,
            "schedule": "immediate",
            "boost_budget_cop": 50000
        })
        
        return posting_results
    
    async def _store_cycle_results(self, results: Dict[str, Any]) -> None:
        """Store planning cycle results in database"""
        await self.db_client.store_planning_cycle(results)
    
    async def run(self):
        """Main orchestrator run loop"""
        logger.info("Starting MainOrchestrator run loop")
        
        while True:
            try:
                # Execute planning cycle
                await self.execute_planning_cycle()
                
                # Wait before next cycle (e.g., daily)
                await asyncio.sleep(86400)  # 24 hours
                
            except KeyboardInterrupt:
                logger.info("Orchestrator shutdown requested")
                break
            except Exception as e:
                logger.error(f"Orchestrator error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down orchestrator")
        
        # Cancel running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(
            *self.running_tasks.values(), 
            return_exceptions=True
        )
        
        # Close database connections
        await self.db_client.close()
        
        logger.info("Orchestrator shutdown complete")