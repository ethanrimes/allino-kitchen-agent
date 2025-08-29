# core/memory_manager.py

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import deque
import json

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages shared memory and context across all agents
    """
    
    def __init__(self, max_memories: int = 1000):
        self.short_term_memory = deque(maxlen=100)  # Recent interactions
        self.long_term_memory = []  # Important persistent memories
        self.context_store = {}  # Shared context between agents
        self.max_memories = max_memories
        
        logger.info("Memory manager initialized")
    
    async def store_memory(
        self,
        agent: str,
        content: Any,
        importance: float = 0.5,
        memory_type: str = "short_term"
    ) -> None:
        """
        Store a memory with importance scoring
        
        Args:
            agent: Agent that created the memory
            content: Memory content
            importance: Importance score (0-1)
            memory_type: "short_term" or "long_term"
        """
        memory = {
            "agent": agent,
            "content": content,
            "importance": importance,
            "timestamp": datetime.utcnow().isoformat(),
            "accessed_count": 0
        }
        
        if memory_type == "short_term" or importance < 0.7:
            self.short_term_memory.append(memory)
        else:
            self.long_term_memory.append(memory)
            # Maintain max size
            if len(self.long_term_memory) > self.max_memories:
                # Remove least important old memories
                self.long_term_memory.sort(key=lambda x: x["importance"])
                self.long_term_memory = self.long_term_memory[-self.max_memories:]
        
        logger.debug(f"Stored {memory_type} memory from {agent}")
    
    async def get_relevant_context(
        self,
        query: str,
        agent: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: Query to match against
            agent: Requesting agent
            max_results: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        all_memories = list(self.short_term_memory) + self.long_term_memory
        
        # Simple relevance scoring (would use embeddings in production)
        scored_memories = []
        query_lower = query.lower()
        
        for memory in all_memories:
            score = 0
            content_str = json.dumps(memory["content"]).lower()
            
            # Check for keyword matches
            for word in query_lower.split():
                if word in content_str:
                    score += 1
            
            # Boost score for recent memories
            memory_age = datetime.utcnow() - datetime.fromisoformat(memory["timestamp"])
            if memory_age < timedelta(hours=1):
                score += 2
            elif memory_age < timedelta(days=1):
                score += 1
            
            # Boost score for importance
            score += memory["importance"] * 2
            
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, memory in scored_memories[:max_results]:
            memory["accessed_count"] += 1
            results.append(memory)
        
        logger.debug(f"Retrieved {len(results)} relevant memories for {agent}")
        
        return results
    
    def set_context(self, key: str, value: Any) -> None:
        """
        Set shared context value
        
        Args:
            key: Context key
            value: Context value
        """
        self.context_store[key] = {
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def get_context(self, key: str) -> Optional[Any]:
        """
        Get shared context value
        
        Args:
            key: Context key
            
        Returns:
            Context value if exists
        """
        if key in self.context_store:
            return self.context_store[key]["value"]
        return None
    
    def get_all_context(self) -> Dict[str, Any]:
        """Get all shared context"""
        return {k: v["value"] for k, v in self.context_store.items()}
    
    async def consolidate_memories(self) -> None:
        """
        Consolidate and summarize memories to save space
        """
        # Group memories by agent and topic
        agent_memories = {}
        
        for memory in self.long_term_memory:
            agent = memory["agent"]
            if agent not in agent_memories:
                agent_memories[agent] = []
            agent_memories[agent].append(memory)
        
        # Summarize old memories (over 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        consolidated = []
        for agent, memories in agent_memories.items():
            old_memories = [
                m for m in memories 
                if datetime.fromisoformat(m["timestamp"]) < cutoff_date
            ]
            
            recent_memories = [
                m for m in memories 
                if datetime.fromisoformat(m["timestamp"]) >= cutoff_date
            ]
            
            # Keep recent memories as-is
            consolidated.extend(recent_memories)
            
            # Summarize old memories by type
            if old_memories:
                summary = {
                    "agent": agent,
                    "content": {
                        "type": "summary",
                        "period": f"Before {cutoff_date.isoformat()}",
                        "memory_count": len(old_memories),
                        "key_points": self._extract_key_points(old_memories)
                    },
                    "importance": 0.6,
                    "timestamp": cutoff_date.isoformat(),
                    "accessed_count": sum(m["accessed_count"] for m in old_memories)
                }
                consolidated.append(summary)
        
        self.long_term_memory = consolidated
        logger.info(f"Consolidated memories: {len(self.long_term_memory)} remaining")
    
    def _extract_key_points(self, memories: List[Dict[str, Any]]) -> List[str]:
        """Extract key points from a list of memories"""
        # Simple extraction - would use LLM in production
        key_points = []
        
        for memory in memories[:5]:  # Top 5 most important
            content = memory.get("content", {})
            if isinstance(content, dict):
                if "key_insights" in content:
                    key_points.extend(content["key_insights"][:2])
                elif "status" in content:
                    key_points.append(f"Status: {content['status']}")
        
        return key_points[:10]  # Limit to 10 points
    
    def clear_short_term_memory(self) -> None:
        """Clear short-term memory"""
        self.short_term_memory.clear()
        logger.info("Short-term memory cleared")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "context_keys": list(self.context_store.keys()),
            "total_memories": len(self.short_term_memory) + len(self.long_term_memory)
        }