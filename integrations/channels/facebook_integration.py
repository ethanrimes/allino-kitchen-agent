# integrations/channels/facebook_integration.py

import aiohttp
import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class FacebookIntegration:
    """
    Integration with Facebook Graph API for posting and managing content
    """
    
    def __init__(self):
        self.access_token = settings.facebook_access_token
        self.page_id = settings.facebook_page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        logger.info("Facebook integration initialized")
    
    async def post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a post on Facebook page
        
        Args:
            post_data: Dictionary with message, link, picture, etc.
            
        Returns:
            Post result with ID and URL
        """
        try:
            endpoint = f"{self.base_url}/{self.page_id}/feed"
            
            params = {
                "access_token": self.access_token,
                "message": post_data.get("message", ""),
            }
            
            if post_data.get("link"):
                params["link"] = post_data["link"]
            
            if post_data.get("picture"):
                params["picture"] = post_data["picture"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, data=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        post_id = data.get("id", "")
                        
                        return {
                            "id": post_id,
                            "url": f"https://www.facebook.com/{post_id}",
                            "estimated_reach": 1000,  # Would fetch from insights API
                            "status": "success"
                        }
                    else:
                        error = await response.text()
                        logger.error(f"Facebook post failed: {error}")
                        return {"status": "failed", "error": error}
                        
        except Exception as e:
            logger.error(f"Facebook post exception: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def boost_post(self, post_id: str, budget_cop: int) -> Dict[str, Any]:
        """
        Boost a Facebook post with paid promotion
        
        Args:
            post_id: Facebook post ID
            budget_cop: Budget in Colombian pesos
            
        Returns:
            Boost campaign details
        """
        try:
            # Convert COP to USD (approximate rate)
            budget_usd = budget_cop / 4000
            
            endpoint = f"{self.base_url}/act_{self.page_id}/campaigns"
            
            campaign_data = {
                "access_token": self.access_token,
                "name": f"Boost_{post_id}",
                "objective": "POST_ENGAGEMENT",
                "status": "ACTIVE",
                "special_ad_categories": "[]"
            }
            
            # This is simplified - actual implementation would create
            # campaign, ad set, and ad through multiple API calls
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, data=campaign_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "campaign_id": data.get("id"),
                            "estimated_reach": int(budget_cop / 100),  # Rough estimate
                            "status": "active"
                        }
                    else:
                        error = await response.text()
                        logger.error(f"Facebook boost failed: {error}")
                        return {"status": "failed", "error": error}
                        
        except Exception as e:
            logger.error(f"Facebook boost exception: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def get_post_insights(self, post_id: str) -> Dict[str, Any]:
        """
        Get insights for a specific post
        
        Args:
            post_id: Facebook post ID
            
        Returns:
            Post insights and metrics
        """
        try:
            endpoint = f"{self.base_url}/{post_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "metric": "post_impressions,post_engaged_users,post_reactions_by_type_total"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        insights = {}
                        for metric in data.get("data", []):
                            name = metric.get("name")
                            value = metric.get("values", [{}])[0].get("value", 0)
                            insights[name] = value
                        
                        return insights
                    else:
                        error = await response.text()
                        logger.error(f"Failed to get insights: {error}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Get insights exception: {str(e)}")
            return {}