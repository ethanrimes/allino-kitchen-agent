# database/supabase_client.py

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client

from config.settings import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """
    Client for interacting with Supabase PostgreSQL database
    """
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        logger.info("Supabase client initialized")
    
    # Research & Planning Operations
    
    async def store_research_findings(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """Store research findings"""
        try:
            data = {
                "topic": findings.get("query", ""),
                "findings": findings,
                "sources": findings.get("sources", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("research_findings").insert(data).execute()
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to store research findings: {str(e)}")
            raise
    
    async def store_menu(self, menu: Dict[str, Any]) -> Dict[str, Any]:
        """Store menu version"""
        try:
            # Store menu version
            menu_data = {
                "status": menu.get("status", "draft"),
                "notes": f"Menu with {menu.get('total_items', 0)} items",
                "created_at": datetime.utcnow().isoformat()
            }
            
            menu_response = self.client.table("menu_versions").insert(menu_data).execute()
            menu_id = menu_response.data[0]["id"] if menu_response.data else None
            
            if menu_id:
                # Store individual items
                for item in menu.get("items", []):
                    item_data = {
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "base_cost_cop": item.get("estimated_cost_cop", 0),
                        "price_cop": item.get("price_cop", 0),
                        "active": True
                    }
                    
                    item_response = self.client.table("items").insert(item_data).execute()
                    
                    if item_response.data:
                        # Link item to menu
                        menu_item_data = {
                            "menu_id": menu_id,
                            "item_id": item_response.data[0]["id"]
                        }
                        self.client.table("menu_items").insert(menu_item_data).execute()
            
            return {"id": menu_id, "status": "success"}
            
        except Exception as e:
            logger.error(f"Failed to store menu: {str(e)}")
            raise
    
    # Order Management
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        try:
            data = {
                "customer_id": order_data.get("customer_id"),
                "channel": order_data.get("channel", "web"),
                "status": "pending",
                "total_cop": order_data.get("total_cop", 0),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("orders").insert(data).execute()
            
            if response.data:
                order_id = response.data[0]["id"]
                
                # Add order items
                for item in order_data.get("items", []):
                    item_data = {
                        "order_id": order_id,
                        "item_id": item.get("item_id"),
                        "qty": item.get("qty", 1),
                        "price_cop": item.get("price_cop", 0)
                    }
                    self.client.table("order_items").insert(item_data).execute()
                
                return response.data[0]
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to create order: {str(e)}")
            raise
    
    async def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Update order status"""
        try:
            data = {"status": status}
            response = self.client.table("orders").update(data).eq("id", order_id).execute()
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to update order status: {str(e)}")
            raise
    
    # Customer Management
    
    async def get_whatsapp_customers(self) -> List[Dict[str, Any]]:
        """Get customers with WhatsApp IDs"""
        try:
            response = self.client.table("customers").select("*").not_.is_("whatsapp_id", "null").execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Failed to get WhatsApp customers: {str(e)}")
            return []
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer"""
        try:
            data = {
                "name": customer_data.get("name", ""),
                "phone": customer_data.get("phone", ""),
                "whatsapp_id": customer_data.get("whatsapp_id"),
                "ig_handle": customer_data.get("ig_handle"),
                "fb_id": customer_data.get("fb_id"),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("customers").insert(data).execute()
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to create customer: {str(e)}")
            raise
    
    # Campaign Management
    
    async def store_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store marketing campaign data"""
        try:
            # Store in a generic campaigns table (you may want to create this)
            data = {
                "type": "social_media",
                "platforms": list(campaign_data.get("posts", {}).keys()),
                "budget_cop": campaign_data.get("budget_spent_cop", 0),
                "reach": campaign_data.get("total_reach", 0),
                "results": campaign_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Using decision_logs table as a temporary solution
            log_data = {
                "agent": "social_media_orchestration",
                "action": "campaign_executed",
                "context": campaign_data,
                "budget_cop": campaign_data.get("budget_spent_cop", 0),
                "outcome": {"reach": campaign_data.get("total_reach", 0)},
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("decision_logs").insert(log_data).execute()
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to store campaign: {str(e)}")
            raise
    
    # Agent & System Operations
    
    async def store_agent_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store agent execution record"""
        try:
            data = {
                "agent": execution_data.get("agent", ""),
                "action": execution_data.get("task", {}).get("task", ""),
                "context": execution_data.get("task", {}),
                "outcome": execution_data.get("result", {}),
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("decision_logs").insert(data).execute()
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to store agent execution: {str(e)}")
            raise
    
    async def store_planning_cycle(self, cycle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store planning cycle results"""
        try:
            data = {
                "agent": "main_orchestrator",
                "action": "planning_cycle",
                "context": {"phases": list(cycle_data.get("phases", {}).keys())},
                "outcome": cycle_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            response = self.client.table("decision_logs").insert(data).execute()
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to store planning cycle: {str(e)}")
            raise
    
    # Inventory Operations
    
    async def get_inventory_levels(self) -> List[Dict[str, Any]]:
        """Get current inventory levels"""
        try:
            response = self.client.table("inventory").select("*").execute()
            return response.data if response.data else []
            
        except Exception as e:
            logger.error(f"Failed to get inventory levels: {str(e)}")
            return []
    
    async def update_inventory(self, sku: str, qty_change: float, transaction_type: str) -> Dict[str, Any]:
        """Update inventory level and record transaction"""
        try:
            # Get current quantity
            current = self.client.table("inventory").select("qty").eq("sku", sku).execute()
            
            if current.data:
                current_qty = float(current.data[0]["qty"])
                new_qty = current_qty + qty_change
                
                # Update inventory
                self.client.table("inventory").update({"qty": new_qty}).eq("sku", sku).execute()
                
                # Record transaction
                txn_data = {
                    "sku": sku,
                    "kind": transaction_type,
                    "qty": qty_change,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                self.client.table("inventory_txns").insert(txn_data).execute()
                
                return {"sku": sku, "new_qty": new_qty}
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to update inventory: {str(e)}")
            raise
    
    # Analytics Operations
    
    async def get_sales_analytics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get sales analytics for a date range"""
        try:
            response = self.client.table("orders").select("*").gte("created_at", start_date).lte("created_at", end_date).execute()
            
            orders = response.data if response.data else []
            
            total_sales = sum(float(order.get("total_cop", 0)) for order in orders)
            order_count = len(orders)
            avg_order_value = total_sales / order_count if order_count > 0 else 0
            
            return {
                "total_sales_cop": total_sales,
                "order_count": order_count,
                "average_order_value_cop": avg_order_value,
                "orders": orders
            }
            
        except Exception as e:
            logger.error(f"Failed to get sales analytics: {str(e)}")
            return {}
    
    async def close(self):
        """Close database connection"""
        # Supabase client doesn't require explicit closing
        logger.info("Supabase client closed")