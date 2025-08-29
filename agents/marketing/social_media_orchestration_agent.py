# agents/marketing/social_media_orchestration_agent.py

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from integrations.channels.facebook_integration import FacebookIntegration
from integrations.channels.instagram_integration import InstagramIntegration
from integrations.channels.whatsapp_integration import WhatsAppIntegration
from core.memory_manager import MemoryManager
from database.supabase_client import SupabaseClient
from config.settings import settings

logger = logging.getLogger(__name__)

class SocialMediaOrchestrationAgent(BaseAgent):
    """
    Agent responsible for orchestrating social media posts and campaigns
    across multiple channels (Facebook, Instagram, WhatsApp)
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        db_client: Optional[SupabaseClient] = None
    ):
        super().__init__(
            name="social_media_orchestration_agent",
            llm=llm,
            memory_manager=memory_manager,
            db_client=db_client,
            template_path="prompts/templates/social_media_agent.yaml"
        )
        
        # Initialize social media integrations
        self.facebook = FacebookIntegration()
        self.instagram = InstagramIntegration()
        self.whatsapp = WhatsAppIntegration()
        
        self.daily_budget_remaining = settings.daily_marketing_budget
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize social media specific tools"""
        return [
            Tool(
                name="post_to_facebook",
                func=self._post_to_facebook,
                description="Post content to Facebook page"
            ),
            Tool(
                name="post_to_instagram",
                func=self._post_to_instagram,
                description="Post content to Instagram"
            ),
            Tool(
                name="send_whatsapp_broadcast",
                func=self._send_whatsapp_broadcast,
                description="Send WhatsApp broadcast message"
            ),
            Tool(
                name="boost_post",
                func=self._boost_post,
                description="Boost a social media post with paid promotion"
            ),
            Tool(
                name="check_budget",
                func=self._check_budget,
                description="Check remaining marketing budget"
            ),
            Tool(
                name="analyze_engagement",
                func=self._analyze_engagement,
                description="Analyze post engagement metrics"
            )
        ]
    
    async def _execute_core(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute social media orchestration task
        
        Args:
            task: Task with content, menu_data, schedule, and boost_budget
            
        Returns:
            Posting results across all channels
        """
        content = task.get("content", {})
        menu_data = task.get("menu_data", {})
        schedule = task.get("schedule", "immediate")
        boost_budget_cop = task.get("boost_budget_cop", 0)
        
        logger.info(f"Orchestrating social media posts (budget: {boost_budget_cop} COP)")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "posts": {},
            "boosted": {},
            "total_reach": 0,
            "budget_spent_cop": 0,
            "status": "started"
        }
        
        try:
            # Step 1: Post to each platform
            for platform, platform_content in content.items():
                if platform == "facebook":
                    post_result = await self._post_to_facebook(platform_content)
                    results["posts"]["facebook"] = post_result
                    
                elif platform == "instagram":
                    post_result = await self._post_to_instagram(platform_content)
                    results["posts"]["instagram"] = post_result
                    
                elif platform == "whatsapp":
                    # Format menu for WhatsApp
                    whatsapp_content = await self._format_menu_for_whatsapp(
                        platform_content,
                        menu_data
                    )
                    broadcast_result = await self._send_whatsapp_broadcast(whatsapp_content)
                    results["posts"]["whatsapp"] = broadcast_result
            
            # Step 2: Boost posts if budget available
            if boost_budget_cop > 0 and await self._check_budget():
                boost_results = await self._execute_boost_strategy(
                    results["posts"],
                    boost_budget_cop
                )
                results["boosted"] = boost_results
                results["budget_spent_cop"] = boost_results.get("total_spent", 0)
            
            # Step 3: Calculate total reach
            total_reach = 0
            for platform_result in results["posts"].values():
                total_reach += platform_result.get("estimated_reach", 0)
            results["total_reach"] = total_reach
            
            results["status"] = "completed"
            
            # Store campaign results
            await self._store_campaign_results(results)
            
            logger.info(f"Social media orchestration completed. Reach: {total_reach}")
            
        except Exception as e:
            logger.error(f"Social media orchestration failed: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    async def _post_to_facebook(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Facebook"""
        try:
            # Format content for Facebook
            post_data = {
                "message": content.get("text", ""),
                "link": content.get("link"),
                "picture": content.get("image_url")
            }
            
            result = await self.facebook.post(post_data)
            
            return {
                "platform": "facebook",
                "post_id": result.get("id"),
                "url": result.get("url"),
                "estimated_reach": result.get("estimated_reach", 1000),
                "status": "posted"
            }
            
        except Exception as e:
            logger.error(f"Facebook posting failed: {str(e)}")
            return {"platform": "facebook", "status": "failed", "error": str(e)}
    
    async def _post_to_instagram(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Instagram"""
        try:
            # Format content for Instagram
            post_data = {
                "caption": content.get("text", ""),
                "image_url": content.get("image_url"),
                "hashtags": content.get("hashtags", [])
            }
            
            result = await self.instagram.post(post_data)
            
            return {
                "platform": "instagram",
                "post_id": result.get("id"),
                "url": result.get("url"),
                "estimated_reach": result.get("estimated_reach", 800),
                "status": "posted"
            }
            
        except Exception as e:
            logger.error(f"Instagram posting failed: {str(e)}")
            return {"platform": "instagram", "status": "failed", "error": str(e)}
    
    async def _send_whatsapp_broadcast(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send WhatsApp broadcast message"""
        try:
            # Get customer list for broadcast
            customers = await self.db_client.get_whatsapp_customers()
            
            broadcast_data = {
                "message": content.get("message", ""),
                "recipients": [c.get("whatsapp_id") for c in customers],
                "template_name": content.get("template_name"),
                "media_url": content.get("media_url")
            }
            
            result = await self.whatsapp.send_broadcast(broadcast_data)
            
            return {
                "platform": "whatsapp",
                "broadcast_id": result.get("id"),
                "recipients_count": len(customers),
                "estimated_reach": len(customers),
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"WhatsApp broadcast failed: {str(e)}")
            return {"platform": "whatsapp", "status": "failed", "error": str(e)}
    
    async def _format_menu_for_whatsapp(
        self,
        content: Dict[str, Any],
        menu_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format menu data for WhatsApp message"""
        menu_items = menu_data.get("items", [])
        
        message = content.get("text", "🍽️ *Menú del Día* 🍽️\n\n")
        
        # Group by category
        categories = {}
        for item in menu_items:
            cat = item.get("category", "otros")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        # Format message
        for category, items in categories.items():
            message += f"\n*{category.upper()}*\n"
            for item in items[:5]:  # Limit items per category
                name = item.get("name", "")
                price = item.get("price_cop", 0)
                message += f"• {name}: ${price:,.0f} COP\n"
        
        message += "\n📱 *Para ordenar, responde con el nombre del plato*"
        message += "\n🚚 *Entrega en 30-45 minutos*"
        
        return {
            "message": message,
            "template_name": "menu_broadcast"
        }
    
    async def _boost_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Boost a social media post with paid promotion"""
        platform = post_data.get("platform")
        post_id = post_data.get("post_id")
        budget_cop = post_data.get("budget_cop", 10000)
        
        try:
            if platform == "facebook":
                result = await self.facebook.boost_post(post_id, budget_cop)
            elif platform == "instagram":
                result = await self.instagram.boost_post(post_id, budget_cop)
            else:
                return {"status": "unsupported_platform"}
            
            return {
                "platform": platform,
                "post_id": post_id,
                "budget_cop": budget_cop,
                "estimated_additional_reach": result.get("estimated_reach", 500),
                "status": "boosted"
            }
            
        except Exception as e:
            logger.error(f"Post boost failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def _execute_boost_strategy(
        self,
        posts: Dict[str, Any],
        total_budget_cop: int
    ) -> Dict[str, Any]:
        """Execute strategic boost allocation across platforms"""
        # Allocate budget based on platform performance
        allocation = {
            "facebook": 0.4,  # 40% to Facebook
            "instagram": 0.4,  # 40% to Instagram
            "whatsapp": 0.2   # 20% to WhatsApp (if applicable)
        }
        
        boost_results = {}
        total_spent = 0
        
        for platform, post_result in posts.items():
            if platform in ["facebook", "instagram"] and post_result.get("status") == "posted":
                platform_budget = int(total_budget_cop * allocation.get(platform, 0))
                
                if platform_budget > 0:
                    boost_result = await self._boost_post({
                        "platform": platform,
                        "post_id": post_result.get("post_id"),
                        "budget_cop": platform_budget
                    })
                    
                    boost_results[platform] = boost_result
                    if boost_result.get("status") == "boosted":
                        total_spent += platform_budget
        
        boost_results["total_spent"] = total_spent
        self.daily_budget_remaining -= total_spent
        
        return boost_results
    
    async def _check_budget(self) -> bool:
        """Check if budget is available for campaigns"""
        return self.daily_budget_remaining > 0
    
    async def _analyze_engagement(self, post_id: str) -> Dict[str, Any]:
        """Analyze engagement metrics for a post"""
        # This would fetch real metrics from platform APIs
        return {
            "likes": 245,
            "comments": 32,
            "shares": 18,
            "reach": 1520,
            "engagement_rate": 0.194
        }
    
    async def _store_campaign_results(self, results: Dict[str, Any]) -> None:
        """Store campaign results in database"""
        try:
            await self.db_client.store_campaign(results)
            logger.info("Campaign results stored successfully")
        except Exception as e:
            logger.error(f"Failed to store campaign results: {str(e)}")