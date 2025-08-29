# agents/marketing/content_creation_agent.py

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.memory_manager import MemoryManager
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class ContentCreationAgent(BaseAgent):
    """
    Agent responsible for creating engaging content for social media platforms
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        db_client: Optional[SupabaseClient] = None
    ):
        super().__init__(
            name="content_creation_agent",
            llm=llm,
            memory_manager=memory_manager,
            db_client=db_client,
            template_path="prompts/templates/content_creation_agent.yaml"
        )
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize content creation tools"""
        return [
            Tool(
                name="generate_caption",
                func=self._generate_caption,
                description="Generate engaging caption for social media"
            ),
            Tool(
                name="create_hashtags",
                func=self._create_hashtags,
                description="Generate relevant hashtags"
            ),
            Tool(
                name="format_menu",
                func=self._format_menu,
                description="Format menu for social media post"
            )
        ]
    
    async def _execute_core(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content creation task
        
        Args:
            task: Task with platform, menu_data, content_type, language, tone
            
        Returns:
            Created content for the platform
        """
        platform = task.get("platform", "instagram")
        menu_data = task.get("menu_data", {})
        content_type = task.get("content_type", "menu_announcement")
        language = task.get("language", "spanish")
        tone = task.get("tone", "casual_friendly")
        
        logger.info(f"Creating {content_type} content for {platform}")
        
        content = {
            "platform": platform,
            "type": content_type,
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Generate content based on type
            if content_type == "menu_announcement":
                content.update(await self._create_menu_announcement(
                    platform, menu_data, language, tone
                ))
            elif content_type == "daily_special":
                content.update(await self._create_daily_special(
                    platform, menu_data, language, tone
                ))
            elif content_type == "engagement_post":
                content.update(await self._create_engagement_post(
                    platform, language, tone
                ))
            else:
                content.update(await self._create_generic_post(
                    platform, language, tone
                ))
            
            logger.info(f"Content created successfully for {platform}")
            
        except Exception as e:
            logger.error(f"Content creation failed: {str(e)}")
            content["error"] = str(e)
        
        return content
    
    async def _create_menu_announcement(
        self,
        platform: str,
        menu_data: Dict[str, Any],
        language: str,
        tone: str
    ) -> Dict[str, Any]:
        """Create menu announcement content"""
        
        # Extract menu highlights
        menu_items = menu_data.get("items", [])[:5]  # Top 5 items
        
        # Generate caption based on platform
        if platform == "instagram":
            caption = await self._generate_instagram_caption(menu_items, language)
            hashtags = await self._create_hashtags(platform, "food_delivery")
            
            return {
                "text": caption,
                "hashtags": hashtags,
                "image_url": "https://placeholder.com/menu.jpg",  # Would generate actual image
                "cta": "Link en bio para ordenar 🔗"
            }
        
        elif platform == "facebook":
            text = await self._generate_facebook_post(menu_items, language)
            
            return {
                "text": text,
                "link": "https://wa.me/573001234567",  # WhatsApp order link
                "image_url": "https://placeholder.com/menu.jpg"
            }
        
        elif platform == "whatsapp":
            message = await self._generate_whatsapp_message(menu_items, language)
            
            return {
                "message": message,
                "media_url": "https://placeholder.com/menu.jpg"
            }
        
        return {}
    
    async def _create_daily_special(
        self,
        platform: str,
        menu_data: Dict[str, Any],
        language: str,
        tone: str
    ) -> Dict[str, Any]:
        """Create daily special content"""
        
        # Select a random item for special
        menu_items = menu_data.get("items", [])
        if menu_items:
            special_item = menu_items[0]  # Would randomize in production
        else:
            special_item = {
                "name": "Plato del Día",
                "price_cop": 25000,
                "description": "Deliciosa opción especial"
            }
        
        discount_price = int(special_item.get("price_cop", 25000) * 0.8)
        
        text = f"""⭐ ¡Especial del Día! ⭐
        
{special_item.get('name', 'Plato Especial')}
Precio regular: ${special_item.get('price_cop', 25000):,} COP
HOY SOLO: ${discount_price:,} COP 🔥

⏰ Válido hasta las 9 PM
📱 Ordena ahora: wa.me/573001234567

#EspecialDelDia #Descuento #ComidaColombia"""
        
        return {
            "text": text,
            "image_url": "https://placeholder.com/special.jpg",
            "special_item": special_item,
            "discount_percentage": 20
        }
    
    async def _create_engagement_post(
        self,
        platform: str,
        language: str,
        tone: str
    ) -> Dict[str, Any]:
        """Create engagement-focused content"""
        
        engagement_posts = [
            {
                "text": "¿Cuál es tu comida colombiana favorita? 🇨🇴\nComéntanos abajo 👇",
                "type": "question"
            },
            {
                "text": "¡SORTEO! 🎉\nGana una cena para dos\n✅ Sigue nuestra cuenta\n✅ Dale like a este post\n✅ Etiqueta a un amigo",
                "type": "giveaway"
            },
            {
                "text": "Adivina el plato 🤔\n¿Qué ingredientes lleva una bandeja paisa?\nLos primeros 5 en acertar tienen 10% de descuento",
                "type": "quiz"
            }
        ]
        
        # Select random engagement post
        post = engagement_posts[0]  # Would randomize
        
        return {
            "text": post["text"],
            "engagement_type": post["type"],
            "image_url": "https://placeholder.com/engagement.jpg"
        }
    
    async def _generate_instagram_caption(
        self,
        menu_items: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate Instagram caption"""
        
        items_text = "\n".join([
            f"• {item.get('name', '')}" for item in menu_items[:3]
        ])
        
        caption = f"""🍽️ ¡Nuevo Menú Disponible! 🍽️

Nuestras delicias de hoy:
{items_text}

📍 Entrega en toda Bogotá
⏰ 30-45 minutos
💳 Pagos seguros

Ordena por WhatsApp 📱"""
        
        return caption
    
    async def _generate_facebook_post(
        self,
        menu_items: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate Facebook post"""
        
        items_text = "\n".join([
            f"🔸 {item.get('name', '')} - ${item.get('price_cop', 0):,} COP"
            for item in menu_items[:5]
        ])
        
        post = f"""¡Descubre nuestro menú del día! 🍴

{items_text}

✅ Ingredientes frescos
✅ Preparación al momento
✅ Entrega rápida y segura

Haz tu pedido ahora: wa.me/573001234567"""
        
        return post
    
    async def _generate_whatsapp_message(
        self,
        menu_items: List[Dict[str, Any]],
        language: str
    ) -> str:
        """Generate WhatsApp message"""
        
        # Group items by category
        categories = {}
        for item in menu_items:
            cat = item.get("category", "otros")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        message = "🍽️ *MENÚ DEL DÍA* 🍽️\n\n"
        
        for category, items in categories.items():
            message += f"*{category.upper()}*\n"
            for item in items[:3]:
                message += f"• {item.get('name', '')}: ${item.get('price_cop', 0):,} COP\n"
            message += "\n"
        
        message += "📱 *Para ordenar, responde con el nombre del plato*\n"
        message += "🚚 *Entrega en 30-45 minutos*\n"
        message += "💳 *Aceptamos todos los medios de pago*"
        
        return message
    
    async def _generate_caption(self, text: str) -> str:
        """Tool: Generate engaging caption"""
        # Use LLM to enhance caption
        prompt = f"Make this caption more engaging for social media: {text}"
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    async def _create_hashtags(self, platform: str, topic: str) -> List[str]:
        """Tool: Create relevant hashtags"""
        hashtags = {
            "instagram": [
                "#ComidaColombia", "#GhostKitchen", "#DomiciliosBogota",
                "#FoodDelivery", "#ComidaCasera", "#RestauranteVirtual",
                "#MenuDelDia", "#ComidaRapida", "#Foodie", "#Delicioso",
                "#EntregaRapida", "#PlatosColombiano", "#Gastronomia",
                "#ComidaSaludable", "#PromocionesComida"
            ],
            "facebook": [
                "#ComidaDomicilio", "#Bogota", "#MenuEspecial",
                "#OfertaDelDia", "#RestauranteOnline"
            ]
        }
        
        return hashtags.get(platform, [])[:15]
    
    async def _format_menu(self, menu_data: Dict[str, Any]) -> str:
        """Tool: Format menu for social media"""
        items = menu_data.get("items", [])
        formatted = "📋 MENÚ\n\n"
        
        for item in items[:10]:
            formatted += f"• {item.get('name', 'Item')}: ${item.get('price_cop', 0):,}\n"
        
        return formatted
    
    async def _create_generic_post(
        self,
        platform: str,
        language: str,
        tone: str
    ) -> Dict[str, Any]:
        """Create generic social media post"""
        
        return {
            "text": "¡Estamos aquí para servirte! 🍴\nOrdena ahora: wa.me/573001234567",
            "image_url": "https://placeholder.com/generic.jpg"
        }