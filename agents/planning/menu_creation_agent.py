# agents/planning/menu_creation_agent.py

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal

from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from tools.calculation_engine import CalculationEngine
from core.memory_manager import MemoryManager
from database.supabase_client import SupabaseClient
from config.settings import settings

logger = logging.getLogger(__name__)

class MenuCreationAgent(BaseAgent):
    """
    Agent responsible for creating and optimizing menu items based on
    research data, market trends, and business constraints
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        db_client: Optional[SupabaseClient] = None
    ):
        super().__init__(
            name="menu_creation_agent",
            llm=llm,
            memory_manager=memory_manager,
            db_client=db_client,
            template_path="prompts/templates/menu_creation_agent.yaml"
        )
        
        self.calculation_engine = CalculationEngine()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize menu creation specific tools"""
        return [
            Tool(
                name="calculate_pricing",
                func=self._calculate_pricing,
                description="Calculate optimal pricing for menu items"
            ),
            Tool(
                name="analyze_ingredients",
                func=self._analyze_ingredients,
                description="Analyze ingredient costs and availability"
            ),
            Tool(
                name="optimize_combinations",
                func=self._optimize_combinations,
                description="Optimize menu item combinations"
            ),
            Tool(
                name="calculate_margins",
                func=self._calculate_margins,
                description="Calculate profit margins for items"
            ),
            Tool(
                name="save_menu",
                func=self._save_menu,
                description="Save menu to database"
            )
        ]
    
    async def _execute_core(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute menu creation task
        
        Args:
            task: Task with research_data and constraints
            
        Returns:
            Created menu with items and pricing
        """
        research_data = task.get("research_data", {})
        constraints = task.get("constraints", {})
        
        logger.info("Creating optimized menu based on research")
        
        menu_result = {
            "version": datetime.utcnow().isoformat(),
            "status": "draft",
            "items": [],
            "categories": {},
            "pricing_strategy": {},
            "total_items": 0,
            "average_price_cop": 0
        }
        
        try:
            # Step 1: Analyze research to identify opportunities
            opportunities = await self._identify_opportunities(research_data)
            
            # Step 2: Generate menu items based on opportunities
            menu_items = await self._generate_menu_items(
                opportunities, 
                constraints
            )
            
            # Step 3: Calculate optimal pricing
            priced_items = await self._price_menu_items(
                menu_items,
                research_data,
                constraints
            )
            
            # Step 4: Optimize combinations and bundles
            optimized_menu = await self._optimize_menu(
                priced_items,
                constraints
            )
            
            # Step 5: Calculate margins and profitability
            final_menu = await self._finalize_menu(optimized_menu)
            
            menu_result["items"] = final_menu["items"]
            menu_result["categories"] = final_menu["categories"]
            menu_result["pricing_strategy"] = final_menu["pricing_strategy"]
            menu_result["total_items"] = len(final_menu["items"])
            menu_result["average_price_cop"] = final_menu["average_price"]
            
            # Step 6: Save menu to database
            await self._save_menu(menu_result)
            
            logger.info(f"Menu created: {menu_result['total_items']} items")
            
        except Exception as e:
            logger.error(f"Menu creation failed: {str(e)}")
            menu_result["error"] = str(e)
            menu_result["status"] = "failed"
        
        return menu_result
    
    async def _identify_opportunities(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify menu opportunities from research"""
        prompt = f"""
        Analyze the following market research and identify menu opportunities for a ghost kitchen in Colombia:
        
        Research Data: {json.dumps(research_data, indent=2)}
        
        Identify:
        1. Top 5 cuisine types with highest demand
        2. Price points that work best
        3. Dietary preferences to consider
        4. Unique selling propositions
        
        Return as JSON with keys: cuisines, price_points, dietary_needs, unique_propositions
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            return json.loads(response.content)
        except:
            return {
                "cuisines": ["Colombian Fusion", "International"],
                "price_points": {"low": 15000, "mid": 35000, "high": 60000},
                "dietary_needs": ["vegetarian", "gluten-free"],
                "unique_propositions": ["Fast delivery", "Premium ingredients"]
            }
    
    async def _generate_menu_items(
        self, 
        opportunities: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate menu items based on opportunities"""
        max_items = constraints.get("max_items", 20)
        
        prompt = f"""
        Create {max_items} menu items for a Colombian ghost kitchen based on:
        
        Opportunities: {json.dumps(opportunities)}
        Constraints: {json.dumps(constraints)}
        
        For each item provide:
        - name (Spanish and English)
        - description
        - category (appetizer, main, dessert, beverage)
        - estimated_cost_cop (ingredient cost)
        - preparation_time_minutes
        - dietary_tags
        - main_ingredients
        
        Return as JSON array.
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            items = json.loads(response.content)
            return items[:max_items]
        except:
            # Fallback menu items
            return self._get_default_menu_items()
    
    async def _price_menu_items(
        self,
        items: List[Dict[str, Any]],
        research_data: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Calculate optimal pricing for menu items"""
        price_range = constraints.get("price_range_cop", {})
        min_price = price_range.get("min", 15000)
        max_price = price_range.get("max", 80000)
        
        priced_items = []
        
        for item in items:
            # Calculate price based on cost and market data
            base_cost = item.get("estimated_cost_cop", 10000)
            
            # Use calculation engine for pricing optimization
            pricing_code = f"""
import json

base_cost = {base_cost}
min_price = {min_price}
max_price = {max_price}
category = "{item.get('category', 'main')}"

# Pricing multipliers by category
multipliers = {{
    "appetizer": 2.8,
    "main": 3.2,
    "dessert": 3.0,
    "beverage": 3.5
}}

multiplier = multipliers.get(category, 3.0)
suggested_price = base_cost * multiplier

# Apply tax
tax_rate = {settings.colombia_tax_rate}
price_with_tax = suggested_price * (1 + tax_rate)

# Round to nearest 1000
final_price = round(price_with_tax / 1000) * 1000

# Ensure within constraints
final_price = max(min_price, min(final_price, max_price))

result = {{
    "suggested_price": final_price,
    "margin_percentage": ((final_price - base_cost) / final_price) * 100,
    "profit_cop": final_price - base_cost
}}

print(json.dumps(result))
"""
            
            calc_result = await self.calculation_engine.execute(pricing_code)
            
            if calc_result.get("success"):
                pricing = json.loads(calc_result.get("output", "{}"))
                item["price_cop"] = pricing.get("suggested_price", 25000)
                item["margin_percentage"] = pricing.get("margin_percentage", 65)
                item["profit_cop"] = pricing.get("profit_cop", 15000)
            else:
                # Fallback pricing
                item["price_cop"] = base_cost * 3
            
            priced_items.append(item)
        
        return priced_items
    
    async def _optimize_menu(
        self,
        items: List[Dict[str, Any]],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize menu combinations and create bundles"""
        # Group items by category
        categories = {}
        for item in items:
            category = item.get("category", "other")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Create combo deals
        combos = []
        if "main" in categories and "beverage" in categories:
            for main in categories["main"][:3]:
                for beverage in categories["beverage"][:2]:
                    combo = {
                        "name": f"Combo: {main['name']} + {beverage['name']}",
                        "items": [main["name"], beverage["name"]],
                        "regular_price_cop": main["price_cop"] + beverage["price_cop"],
                        "combo_price_cop": int((main["price_cop"] + beverage["price_cop"]) * 0.85),
                        "savings_cop": int((main["price_cop"] + beverage["price_cop"]) * 0.15),
                        "category": "combo"
                    }
                    combos.append(combo)
        
        return {
            "items": items + combos,
            "categories": categories,
            "total_items": len(items) + len(combos),
            "combo_deals": len(combos)
        }
    
    async def _finalize_menu(self, menu_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize menu with calculations and strategy"""
        items = menu_data.get("items", [])
        
        # Calculate average price
        prices = [item.get("price_cop", 0) for item in items if "price_cop" in item]
        average_price = sum(prices) / len(prices) if prices else 0
        
        # Determine pricing strategy
        pricing_strategy = {
            "approach": "value-based",
            "average_price_cop": average_price,
            "min_price_cop": min(prices) if prices else 0,
            "max_price_cop": max(prices) if prices else 0,
            "combo_discount_percentage": 15,
            "target_margin_percentage": 65
        }
        
        return {
            "items": items,
            "categories": menu_data.get("categories", {}),
            "pricing_strategy": pricing_strategy,
            "average_price": average_price
        }
    
    async def _calculate_pricing(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Calculate optimal pricing for an item"""
        return await self._price_menu_items([item_data], {}, {})
    
    async def _analyze_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """Tool: Analyze ingredient costs and availability"""
        # This would connect to supplier APIs or databases
        return {
            "ingredients": ingredients,
            "total_cost_cop": 15000,
            "availability": "high"
        }
    
    async def _optimize_combinations(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tool: Optimize item combinations"""
        return await self._optimize_menu({"items": items}, {})
    
    async def _calculate_margins(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Calculate profit margins"""
        cost = item.get("estimated_cost_cop", 0)
        price = item.get("price_cop", 0)
        
        margin = ((price - cost) / price * 100) if price > 0 else 0
        profit = price - cost
        
        return {
            "margin_percentage": margin,
            "profit_cop": profit,
            "roi_percentage": (profit / cost * 100) if cost > 0 else 0
        }
    
    async def _save_menu(self, menu: Dict[str, Any]) -> Dict[str, Any]:
        """Save menu to database"""
        try:
            result = await self.db_client.store_menu(menu)
            logger.info(f"Menu saved: {result.get('id')}")
            return {"success": True, "menu_id": result.get("id")}
        except Exception as e:
            logger.error(f"Failed to save menu: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_default_menu_items(self) -> List[Dict[str, Any]]:
        """Get default menu items as fallback"""
        return [
            {
                "name": "Bandeja Paisa Express",
                "category": "main",
                "estimated_cost_cop": 12000,
                "price_cop": 35000
            },
            {
                "name": "Arepas Rellenas",
                "category": "appetizer", 
                "estimated_cost_cop": 5000,
                "price_cop": 15000
            },
            {
                "name": "Sancocho Delivery",
                "category": "main",
                "estimated_cost_cop": 10000,
                "price_cop": 28000
            }
        ]