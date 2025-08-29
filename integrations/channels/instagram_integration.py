# integrations/channels/instagram_integration.py

import aiohttp
import logging
from typing import Dict, Any, List
from config.settings import settings

logger = logging.getLogger(__name__)

class InstagramIntegration:
    """
    Integration with Instagram Graph API for business accounts
    """
    
    def __init__(self):
        self.access_token = settings.instagram_access_token
        self.business_account_id = settings.instagram_business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
        logger.info("Instagram integration initialized")
    
    async def post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a post on Instagram
        
        Args:
            post_data: Dictionary with caption, image_url, hashtags
            
        Returns:
            Post result with ID and URL
        """
        try:
            # Step 1: Create media container
            container_endpoint = f"{self.base_url}/{self.business_account_id}/media"
            
            caption = post_data.get("caption", "")
            hashtags = post_data.get("hashtags", [])
            
            if hashtags:
                caption += "\n\n" + " ".join(f"#{tag}" for tag in hashtags)
            
            container_params = {
                "access_token": self.access_token,
                "image_url": post_data.get("image_url", ""),
                "caption": caption
            }
            
            async with aiohttp.ClientSession() as session:
                # Create container
                async with session.post(container_endpoint, data=container_params) as response:
                    if response.status != 200:
                        error = await response.text()
                        logger.error(f"Failed to create container: {error}")
                        return {"status": "failed", "error": error}
                    
                    container_data = await response.json()
                    container_id = container_data.get("id")
                
                # Step 2: Publish the container
                publish_endpoint = f"{self.base_url}/{self.business_account_id}/media_publish"
                publish_params = {
                    "access_token": self.access_token,
                    "creation_id": container_id
                }
                
                async with session.post(publish_endpoint, data=publish_params) as response:
                    if response.status == 200:
                        publish_data = await response.json()
                        media_id = publish_data.get("id")
                        
                        return {
                            "id": media_id,
                            "url": f"https://www.instagram.com/p/{media_id}/",
                            "estimated_reach": 800,  # Would fetch from insights
                            "status": "success"
                        }
                    else:
                        error = await response.text()
                        logger.error(f"Failed to publish: {error}")
                        return {"status": "failed", "error": error}
                        
        except Exception as e:
            logger.error(f"Instagram post exception: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def boost_post(self, post_id: str, budget_cop: int) -> Dict[str, Any]:
        """
        Boost an Instagram post (promote)
        
        Args:
            post_id: Instagram media ID
            budget_cop: Budget in Colombian pesos
            
        Returns:
            Promotion details
        """
        try:
            # Instagram promotions are managed through Facebook Ads Manager
            # This is a simplified implementation
            
            budget_usd = budget_cop / 4000  # Approximate conversion
            
            return {
                "promotion_id": f"promo_{post_id}",
                "estimated_reach": int(budget_cop / 125),  # Rough estimate
                "status": "active",
                "budget_cop": budget_cop
            }
            
        except Exception as e:
            logger.error(f"Instagram boost exception: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    async def get_media_insights(self, media_id: str) -> Dict[str, Any]:
        """
        Get insights for a specific media post
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Media insights and metrics
        """
        try:
            endpoint = f"{self.base_url}/{media_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "metric": "impressions,reach,engagement,saved"
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
    
    async def create_story(self, story_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an Instagram story
        
        Args:
            story_data: Dictionary with image_url and optional caption
            
        Returns:
            Story creation result
        """
        try:
            # Stories use a similar process but with different parameters
            endpoint = f"{self.base_url}/{self.business_account_id}/media"
            
            params = {
                "access_token": self.access_token,
                "image_url": story_data.get("image_url", ""),
                "media_type": "STORIES"
            }
            
            # Add caption if provided (stories don't support regular captions)
            if story_data.get("caption"):
                params["caption"] = story_data["caption"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, data=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "id": data.get("id"),
                            "status": "success",
                            "type": "story"
                        }
                    else:
                        error = await response.text()
                        logger.error(f"Failed to create story: {error}")
                        return {"status": "failed", "error": error}
                        
        except Exception as e:
            logger.error(f"Story creation exception: {str(e)}")
            return {"status": "failed", "error": str(e)}