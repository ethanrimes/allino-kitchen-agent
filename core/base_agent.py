# core/base_agent.py

import asyncio
import logging
import yaml
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

from core.memory_manager import MemoryManager
from database.supabase_client import SupabaseClient
from config.settings import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all agents in the system.
    Provides common functionality and interface that all agents must implement.
    """
    
    def __init__(
        self,
        name: str,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        db_client: Optional[SupabaseClient] = None,
        template_path: Optional[str] = None
    ):
        self.name = name
        self.llm = llm or ChatOpenAI(
            temperature=settings.agent_temperature,
            model="gpt-4-turbo-preview",
            openai_api_key=settings.openai_api_key
        )
        
        self.memory_manager = memory_manager or MemoryManager()
        self.db_client = db_client or SupabaseClient()
        
        # Load agent template
        self.template = self._load_template(template_path)
        
        # Initialize conversation memory
        self.local_memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Create agent executor
        self.executor = self._create_executor()
        
        # Execution history
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized agent: {self.name}")
    
    def _load_template(self, template_path: Optional[str]) -> Dict[str, Any]:
        """Load agent template from YAML file"""
        if not template_path:
            template_path = f"prompts/templates/{self.name}.yaml"
        
        template_file = Path(template_path)
        if template_file.exists():
            with open(template_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Template not found: {template_path}")
            return self._get_default_template()
    
    def _get_default_template(self) -> Dict[str, Any]:
        """Get default agent template"""
        return {
            "system_prompt": f"You are {self.name}, an AI agent responsible for specific tasks.",
            "instructions": [
                "Analyze the given task carefully",
                "Use available tools to complete the task",
                "Provide clear and actionable results"
            ],
            "constraints": [],
            "examples": []
        }
    
    @abstractmethod
    def _initialize_tools(self) -> List[Tool]:
        """Initialize agent-specific tools"""
        pass
    
    def _create_executor(self) -> AgentExecutor:
        """Create the agent executor with tools and memory"""
        
        # Create system message from template
        system_message = self._build_system_message()
        
        # Create the agent
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=system_message
        )
        
        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.local_memory,
            verbose=settings.app_debug,
            max_iterations=settings.agent_max_iterations,
            handle_parsing_errors=True
        )
        
        return executor
    
    def _build_system_message(self) -> str:
        """Build system message from template"""
        template = self.template
        
        system_prompt = template.get("system_prompt", "")
        
        if template.get("instructions"):
            system_prompt += "\n\nInstructions:\n"
            for instruction in template["instructions"]:
                system_prompt += f"- {instruction}\n"
        
        if template.get("constraints"):
            system_prompt += "\n\nConstraints:\n"
            for constraint in template["constraints"]:
                system_prompt += f"- {constraint}\n"
        
        if template.get("examples"):
            system_prompt += "\n\nExamples:\n"
            for example in template["examples"]:
                system_prompt += f"{example}\n"
        
        return system_prompt
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task and return results
        
        Args:
            task: Dictionary containing task details
            
        Returns:
            Dictionary containing execution results
        """
        start_time = datetime.utcnow()
        
        try:
            # Log task execution
            logger.info(f"Agent {self.name} executing task: {task.get('task')}")
            
            # Pre-process task
            processed_task = await self.pre_process(task)
            
            # Execute main logic
            result = await self._execute_core(processed_task)
            
            # Post-process results
            final_result = await self.post_process(result)
            
            # Record execution
            execution_record = {
                "agent": self.name,
                "task": task,
                "result": final_result,
                "timestamp": start_time.isoformat(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "status": "success"
            }
            
            self.execution_history.append(execution_record)
            
            # Store in database
            await self._store_execution(execution_record)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {str(e)}")
            
            execution_record = {
                "agent": self.name,
                "task": task,
                "error": str(e),
                "timestamp": start_time.isoformat(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "status": "failed"
            }
            
            self.execution_history.append(execution_record)
            await self._store_execution(execution_record)
            
            raise
    
    @abstractmethod
    async def _execute_core(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core execution logic - must be implemented by each agent
        
        Args:
            task: Processed task dictionary
            
        Returns:
            Execution results
        """
        pass
    
    async def pre_process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pre-process task before execution
        Can be overridden by specific agents
        """
        # Add context from memory
        task["context"] = await self.memory_manager.get_relevant_context(
            query=str(task),
            agent=self.name
        )
        
        return task
    
    async def post_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process results after execution
        Can be overridden by specific agents
        """
        # Store important results in memory
        await self.memory_manager.store_memory(
            agent=self.name,
            content=result,
            importance=self._calculate_importance(result)
        )
        
        return result
    
    def _calculate_importance(self, result: Dict[str, Any]) -> float:
        """Calculate importance score for a result (0-1)"""
        # Base implementation - can be overridden
        if result.get("status") == "failed":
            return 0.8  # Failed tasks are important to remember
        
        if result.get("type") in ["menu_created", "forecast_generated", "order_placed"]:
            return 0.9  # Critical business decisions
        
        return 0.5  # Default importance
    
    async def _store_execution(self, execution_record: Dict[str, Any]) -> None:
        """Store execution record in database"""
        try:
            await self.db_client.store_agent_execution(execution_record)
        except Exception as e:
            logger.error(f"Failed to store execution record: {str(e)}")
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return self.execution_history[-limit:]
    
    async def reset(self):
        """Reset agent state"""
        self.local_memory.clear()
        self.execution_history.clear()
        logger.info(f"Agent {self.name} state reset")