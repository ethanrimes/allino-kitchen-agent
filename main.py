# main.py

import asyncio
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from core.orchestrator import MainOrchestrator
from config.settings import settings
from config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Optional[MainOrchestrator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    """
    global orchestrator
    
    # Startup
    logger.info("Starting Ghost Kitchen AI Platform")
    orchestrator = MainOrchestrator()
    
    # Start orchestrator in background
    asyncio.create_task(orchestrator.run())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ghost Kitchen AI Platform")
    if orchestrator:
        await orchestrator.shutdown()

# Create FastAPI app
app = FastAPI(
    title="Ghost Kitchen AI Platform",
    description="Autonomous AI-driven ghost kitchen management system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ghost Kitchen AI Platform",
        "version": "1.0.0"
    }

# Planning endpoints
@app.post("/planning/execute")
async def execute_planning_cycle(background_tasks: BackgroundTasks):
    """
    Trigger a full planning cycle
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Execute in background
    background_tasks.add_task(orchestrator.execute_planning_cycle)
    
    return {
        "status": "started",
        "message": "Planning cycle initiated"
    }

@app.get("/planning/status")
async def get_planning_status():
    """
    Get current planning status
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Get status from state manager
    status = orchestrator.state_manager.get_state("planning_status")
    
    return {
        "status": status or "idle",
        "last_execution": orchestrator.state_manager.get_state("last_planning_execution")
    }

# Research endpoints
@app.post("/research/execute")
async def execute_research(request: Dict[str, Any]):
    """
    Execute market research
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    query = request.get("query", "")
    depth = request.get("depth", "standard")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    research_agent = orchestrator.agents.get("research")
    if not research_agent:
        raise HTTPException(status_code=503, detail="Research agent not available")
    
    result = await research_agent.execute({
        "task": "research",
        "query": query,
        "depth": depth
    })
    
    return result

# Menu endpoints
@app.post("/menu/create")
async def create_menu(request: Dict[str, Any]):
    """
    Create or update menu based on research
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    research_data = request.get("research_data", {})
    constraints = request.get("constraints", {})
    
    menu_agent = orchestrator.agents.get("menu_creation")
    if not menu_agent:
        raise HTTPException(status_code=503, detail="Menu creation agent not available")
    
    result = await menu_agent.execute({
        "task": "create_menu",
        "research_data": research_data,
        "constraints": constraints
    })
    
    return result

@app.get("/menu/current")
async def get_current_menu():
    """
    Get current active menu
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    # Fetch from database
    menu = await orchestrator.db_client.get_current_menu()
    
    return menu

# Social media endpoints
@app.post("/social/post")
async def post_to_social_media(request: Dict[str, Any]):
    """
    Post content to social media channels
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    content = request.get("content", {})
    platforms = request.get("platforms", ["facebook", "instagram", "whatsapp"])
    boost_budget = request.get("boost_budget_cop", 0)
    
    social_agent = orchestrator.agents.get("social_media")
    if not social_agent:
        raise HTTPException(status_code=503, detail="Social media agent not available")
    
    result = await social_agent.execute({
        "task": "post_content",
        "content": {platform: content for platform in platforms},
        "menu_data": {},
        "schedule": "immediate",
        "boost_budget_cop": boost_budget
    })
    
    return result

# Order endpoints
@app.post("/orders/create")
async def create_order(order_data: Dict[str, Any]):
    """
    Create a new order
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    result = await orchestrator.db_client.create_order(order_data)
    
    return result

@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status_update: Dict[str, str]):
    """
    Update order status
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    result = await orchestrator.db_client.update_order_status(order_id, new_status)
    
    return result

# Analytics endpoints
@app.get("/analytics/sales")
async def get_sales_analytics(start_date: str, end_date: str):
    """
    Get sales analytics for date range
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    analytics = await orchestrator.db_client.get_sales_analytics(start_date, end_date)
    
    return analytics

@app.get("/analytics/performance")
async def get_performance_metrics():
    """
    Get overall platform performance metrics
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    memory_stats = orchestrator.memory_manager.get_memory_stats()
    
    return {
        "memory": memory_stats,
        "agents": {
            agent_name: len(agent.execution_history) 
            for agent_name, agent in orchestrator.agents.items()
        },
        "status": "operational"
    }

# Agent management endpoints
@app.get("/agents/status")
async def get_agents_status():
    """
    Get status of all agents
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    agents_status = {}
    for name, agent in orchestrator.agents.items():
        history = agent.get_execution_history(limit=1)
        agents_status[name] = {
            "last_execution": history[0] if history else None,
            "total_executions": len(agent.execution_history)
        }
    
    return agents_status

@app.post("/agents/{agent_name}/reset")
async def reset_agent(agent_name: str):
    """
    Reset a specific agent
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    agent = orchestrator.agents.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    
    await agent.reset()
    
    return {
        "status": "success",
        "message": f"Agent {agent_name} reset successfully"
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level=settings.log_level.lower()
    )