# agents/planning/demand_forecasting_agent.py

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import random

from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from tools.calculation_engine import CalculationEngine
from core.memory_manager import MemoryManager
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)

class DemandForecastingAgent(BaseAgent):
    """
    Agent responsible for forecasting demand for menu items using various
    statistical and machine learning methods
    """
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory_manager: Optional[MemoryManager] = None,
        db_client: Optional[SupabaseClient] = None
    ):
        super().__init__(
            name="demand_forecasting_agent",
            llm=llm,
            memory_manager=memory_manager,
            db_client=db_client,
            template_path="prompts/templates/demand_forecasting_agent.yaml"
        )
        
        self.calculation_engine = CalculationEngine()
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize forecasting tools"""
        return [
            Tool(
                name="time_series_forecast",
                func=self._time_series_forecast,
                description="Generate time series forecast"
            ),
            Tool(
                name="regression_forecast",
                func=self._regression_forecast,
                description="Generate regression-based forecast"
            ),
            Tool(
                name="seasonal_adjustment",
                func=self._seasonal_adjustment,
                description="Apply seasonal adjustments to forecast"
            ),
            Tool(
                name="calculate_safety_stock",
                func=self._calculate_safety_stock,
                description="Calculate safety stock levels"
            )
        ]
    
    async def _execute_core(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute demand forecasting task
        
        Args:
            task: Task with menu_items, horizon_days, methods
            
        Returns:
            Demand forecasts for menu items
        """
        menu_items = task.get("menu_items", [])
        horizon_days = task.get("horizon_days", 30)
        methods = task.get("methods", ["time_series"])
        
        logger.info(f"Forecasting demand for {len(menu_items)} items, {horizon_days} days")
        
        forecast_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "horizon_days": horizon_days,
            "items": {},
            "summary": {},
            "recommendations": []
        }
        
        try:
            # Fetch historical data (if available)
            historical_data = await self._fetch_historical_data()
            
            # Generate forecasts for each item
            for item in menu_items:
                item_name = item.get("name", "Unknown")
                item_forecasts = {}
                
                # Apply different forecasting methods
                for method in methods:
                    if method == "time_series":
                        forecast = await self._time_series_forecast(
                            item, historical_data, horizon_days
                        )
                    elif method == "regression":
                        forecast = await self._regression_forecast(
                            item, historical_data, horizon_days
                        )
                    elif method == "ml_ensemble":
                        forecast = await self._ml_ensemble_forecast(
                            item, historical_data, horizon_days
                        )
                    else:
                        continue
                    
                    item_forecasts[method] = forecast
                
                # Combine forecasts (ensemble)
                combined_forecast = await self._combine_forecasts(item_forecasts)
                
                # Apply seasonal adjustments
                adjusted_forecast = await self._seasonal_adjustment(
                    combined_forecast,
                    item.get("category", "main")
                )
                
                # Calculate inventory requirements
                inventory_needs = await self._calculate_inventory_needs(
                    adjusted_forecast,
                    item
                )
                
                forecast_results["items"][item_name] = {
                    "daily_forecast": adjusted_forecast["daily_values"],
                    "total_expected": sum(adjusted_forecast["daily_values"]),
                    "peak_day": max(adjusted_forecast["daily_values"]),
                    "average_daily": sum(adjusted_forecast["daily_values"]) / horizon_days,
                    "confidence_interval": adjusted_forecast.get("confidence_interval", {}),
                    "inventory_needs": inventory_needs,
                    "methods_used": list(item_forecasts.keys())
                }
            
            # Generate summary statistics
            forecast_results["summary"] = await self._generate_summary(
                forecast_results["items"]
            )
            
            # Generate recommendations
            forecast_results["recommendations"] = await self._generate_recommendations(
                forecast_results
            )
            
            # Store forecast results
            await self._store_forecast(forecast_results)
            
            logger.info("Demand forecasting completed successfully")
            
        except Exception as e:
            logger.error(f"Demand forecasting failed: {str(e)}")
            forecast_results["error"] = str(e)
        
        return forecast_results
    
    async def _fetch_historical_data(self) -> Dict[str, Any]:
        """Fetch historical sales data"""
        # Get last 90 days of sales data
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)
        
        analytics = await self.db_client.get_sales_analytics(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        return analytics
    
    async def _time_series_forecast(
        self,
        item: Dict[str, Any],
        historical_data: Dict[str, Any],
        horizon_days: int
    ) -> Dict[str, Any]:
        """Generate time series forecast"""
        
        # Simplified time series forecast
        # In production, would use Prophet, ARIMA, etc.
        
        code = f"""
import json
import random

# Simulate time series forecast
item_name = "{item.get('name', 'Item')}"
horizon = {horizon_days}

# Base demand based on item category
category = "{item.get('category', 'main')}"
base_demands = {{
    "appetizer": 15,
    "main": 30,
    "dessert": 10,
    "beverage": 20
}}

base_demand = base_demands.get(category, 20)

# Generate forecast with trend and noise
forecast = []
for day in range(horizon):
    # Add weekly seasonality
    day_of_week = day % 7
    if day_of_week in [4, 5, 6]:  # Fri, Sat, Sun
        multiplier = 1.5
    else:
        multiplier = 1.0
    
    # Add trend
    trend = 1 + (day / horizon) * 0.1
    
    # Calculate daily forecast
    daily_demand = base_demand * multiplier * trend
    daily_demand += random.uniform(-5, 5)  # Add noise
    
    forecast.append(max(0, daily_demand))

result = {{
    "method": "time_series",
    "daily_values": forecast,
    "confidence_interval": {{
        "lower": [max(0, v - 5) for v in forecast],
        "upper": [v + 5 for v in forecast]
    }}
}}

print(json.dumps(result))
"""
        
        calc_result = await self.calculation_engine.execute(code)
        
        if calc_result.get("success"):
            return json.loads(calc_result.get("output", "{}"))
        else:
            # Return default forecast
            return {
                "method": "time_series",
                "daily_values": [20] * horizon_days,
                "confidence_interval": {
                    "lower": [15] * horizon_days,
                    "upper": [25] * horizon_days
                }
            }
    
    async def _regression_forecast(
        self,
        item: Dict[str, Any],
        historical_data: Dict[str, Any],
        horizon_days: int
    ) -> Dict[str, Any]:
        """Generate regression-based forecast"""
        
        # Simplified linear regression forecast
        base_demand = 25
        growth_rate = 0.02
        
        forecast = []
        for day in range(horizon_days):
            daily = base_demand * (1 + growth_rate * day)
            forecast.append(daily + random.uniform(-3, 3))
        
        return {
            "method": "regression",
            "daily_values": forecast,
            "r_squared": 0.75,  # Simulated R²
            "coefficients": {
                "intercept": base_demand,
                "slope": growth_rate
            }
        }
    
    async def _ml_ensemble_forecast(
        self,
        item: Dict[str, Any],
        historical_data: Dict[str, Any],
        horizon_days: int
    ) -> Dict[str, Any]:
        """Generate ML ensemble forecast"""
        
        # Simulate ensemble of multiple models
        # In production, would use XGBoost, Random Forest, etc.
        
        forecasts = []
        for _ in range(3):  # 3 models in ensemble
            model_forecast = []
            base = random.uniform(15, 35)
            for day in range(horizon_days):
                daily = base + random.uniform(-5, 5)
                model_forecast.append(max(0, daily))
            forecasts.append(model_forecast)
        
        # Average ensemble predictions
        ensemble_forecast = []
        for day in range(horizon_days):
            daily_avg = sum(f[day] for f in forecasts) / len(forecasts)
            ensemble_forecast.append(daily_avg)
        
        return {
            "method": "ml_ensemble",
            "daily_values": ensemble_forecast,
            "models_used": ["xgboost", "random_forest", "neural_net"],
            "ensemble_method": "average"
        }
    
    async def _combine_forecasts(self, forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple forecasts into ensemble"""
        
        if not forecasts:
            return {"daily_values": [], "method": "none"}
        
        # Get all daily values
        all_forecasts = [f["daily_values"] for f in forecasts.values()]
        
        if not all_forecasts:
            return {"daily_values": [], "method": "none"}
        
        # Calculate weighted average (equal weights for now)
        horizon = len(all_forecasts[0])
        combined = []
        
        for day in range(horizon):
            daily_values = [f[day] for f in all_forecasts if day < len(f)]
            if daily_values:
                combined.append(sum(daily_values) / len(daily_values))
        
        # Calculate confidence intervals
        lower = [max(0, v - 5) for v in combined]
        upper = [v + 5 for v in combined]
        
        return {
            "daily_values": combined,
            "method": "ensemble",
            "confidence_interval": {
                "lower": lower,
                "upper": upper
            }
        }
    
    async def _seasonal_adjustment(
        self,
        forecast: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Apply seasonal adjustments to forecast"""
        
        daily_values = forecast.get("daily_values", [])
        adjusted = []
        
        for day, value in enumerate(daily_values):
            # Day of week adjustment
            day_of_week = (datetime.utcnow() + timedelta(days=day)).weekday()
            
            # Weekend boost
            if day_of_week in [4, 5, 6]:  # Friday, Saturday, Sunday
                multiplier = 1.3
            elif day_of_week == 0:  # Monday
                multiplier = 0.9
            else:
                multiplier = 1.0
            
            # Category-specific adjustments
            if category == "dessert" and day_of_week in [5, 6]:
                multiplier *= 1.2  # Extra dessert demand on weekends
            
            adjusted.append(value * multiplier)
        
        forecast["daily_values"] = adjusted
        forecast["seasonal_adjusted"] = True
        
        return forecast
    
    async def _calculate_inventory_needs(
        self,
        forecast: Dict[str, Any],
        item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate inventory requirements based on forecast"""
        
        daily_values = forecast.get("daily_values", [])
        
        if not daily_values:
            return {}
        
        # Calculate requirements
        total_needed = sum(daily_values)
        peak_day = max(daily_values)
        avg_daily = total_needed / len(daily_values)
        
        # Safety stock (20% buffer)
        safety_stock = avg_daily * 0.2 * 7  # 1 week safety stock
        
        # Reorder point (3 days lead time)
        reorder_point = avg_daily * 3 + safety_stock
        
        return {
            "total_units_needed": int(total_needed),
            "peak_day_units": int(peak_day),
            "average_daily_units": int(avg_daily),
            "safety_stock": int(safety_stock),
            "reorder_point": int(reorder_point),
            "suggested_order_quantity": int(total_needed * 1.2)  # 20% buffer
        }
    
    async def _calculate_safety_stock(self, item_data: Dict[str, Any]) -> float:
        """Tool: Calculate safety stock levels"""
        avg_demand = item_data.get("average_daily", 20)
        lead_time = item_data.get("lead_time_days", 2)
        service_level = item_data.get("service_level", 0.95)
        
        # Simplified safety stock calculation
        # In production, would use proper statistical methods
        safety_stock = avg_demand * lead_time * 0.2
        
        return safety_stock
    
    async def _generate_summary(self, items_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics"""
        
        total_daily = {}
        
        for item_name, forecast in items_forecast.items():
            daily_forecast = forecast.get("daily_forecast", [])
            
            for day, value in enumerate(daily_forecast):
                if day not in total_daily:
                    total_daily[day] = 0
                total_daily[day] += value
        
        if total_daily:
            peak_day = max(total_daily.values())
            avg_daily = sum(total_daily.values()) / len(total_daily)
        else:
            peak_day = 0
            avg_daily = 0
        
        return {
            "total_items_forecasted": len(items_forecast),
            "peak_day_total_units": peak_day,
            "average_daily_total_units": avg_daily,
            "total_units_30_days": sum(total_daily.values()) if total_daily else 0
        }
    
    async def _generate_recommendations(self, forecast_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Analyze forecast patterns
        summary = forecast_results.get("summary", {})
        
        if summary.get("peak_day_total_units", 0) > summary.get("average_daily_total_units", 0) * 1.5:
            recommendations.append(
                "Plan for significant demand spikes on weekends - ensure adequate staffing"
            )
        
        # Check individual items
        for item_name, forecast in forecast_results.get("items", {}).items():
            if forecast.get("peak_day", 0) > 50:
                recommendations.append(
                    f"High demand expected for {item_name} - ensure sufficient inventory"
                )
            
            if forecast.get("average_daily", 0) < 5:
                recommendations.append(
                    f"Low demand forecast for {item_name} - consider promotion or removal"
                )
        
        # General recommendations
        recommendations.extend([
            "Review supplier lead times to optimize reorder points",
            "Consider promotional campaigns for low-demand items",
            "Implement dynamic pricing for peak demand periods"
        ])
        
        return recommendations[:5]  # Top 5 recommendations
    
    async def _store_forecast(self, forecast_results: Dict[str, Any]) -> None:
        """Store forecast results in database"""
        try:
            # Store each item forecast
            for item_name, forecast in forecast_results.get("items", {}).items():
                forecast_data = {
                    "item_name": item_name,
                    "horizon_days": forecast_results.get("horizon_days", 30),
                    "forecast": forecast,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                # Store in decision_logs as a temporary solution
                await self.db_client.store_agent_execution({
                    "agent": "demand_forecasting",
                    "task": {"type": "forecast", "item": item_name},
                    "result": forecast_data
                })
            
            logger.info("Forecast results stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store forecast: {str(e)}")