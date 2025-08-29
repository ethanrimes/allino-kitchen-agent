# tools/calculation_engine.py

import asyncio
import logging
import sys
import io
import json
from typing import Dict, Any, Optional
from contextlib import redirect_stdout, redirect_stderr
import traceback

logger = logging.getLogger(__name__)

class CalculationEngine:
    """
    Sandboxed Python code execution environment for calculations and analysis
    """
    
    def __init__(self):
        self.timeout_seconds = 10
        self.max_output_length = 10000
        logger.info("Calculation engine initialized")
    
    async def execute(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute Python code in a sandboxed environment
        
        Args:
            code: Python code to execute
            context: Optional context variables to inject
            
        Returns:
            Execution result with output, errors, and artifacts
        """
        try:
            # Create execution result container
            result = {
                "success": False,
                "output": "",
                "error": "",
                "artifacts": {},
                "execution_time": 0
            }
            
            # Prepare safe globals with limited imports
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "type": type,
                    "isinstance": isinstance,
                    "open": None,  # Disable file operations
                    "__import__": self._safe_import
                }
            }
            
            # Add context variables if provided
            if context:
                safe_globals.update(context)
            
            # Capture output
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Execute code with timeout
            import time
            start_time = time.time()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    # Execute the code
                    exec(code, safe_globals)
                    result["success"] = True
                except Exception as e:
                    result["error"] = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
            result["execution_time"] = time.time() - start_time
            
            # Capture outputs
            result["output"] = stdout_capture.getvalue()[:self.max_output_length]
            
            stderr_output = stderr_capture.getvalue()
            if stderr_output:
                result["error"] = stderr_output[:self.max_output_length]
            
            # Extract any artifacts (variables created in the code)
            artifacts = {}
            for key, value in safe_globals.items():
                if not key.startswith("__") and key not in ["print", "len", "range"]:
                    try:
                        # Try to serialize the value
                        if isinstance(value, (str, int, float, bool, list, dict)):
                            artifacts[key] = value
                        else:
                            artifacts[key] = str(value)
                    except:
                        artifacts[key] = "<non-serializable>"
            
            result["artifacts"] = artifacts
            
            logger.info(f"Code execution completed in {result['execution_time']:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Calculation engine error: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "artifacts": {},
                "execution_time": 0
            }
    
    def _safe_import(self, name, *args, **kwargs):
        """
        Safe import function that only allows specific modules
        """
        allowed_modules = [
            "math",
            "statistics",
            "json",
            "datetime",
            "collections",
            "itertools",
            "functools",
            "decimal",
            "fractions",
            "random",
            "re",
            "numpy",
            "pandas"
        ]
        
        if name in allowed_modules:
            return __import__(name, *args, **kwargs)
        else:
            raise ImportError(f"Module '{name}' is not allowed in the sandbox")
    
    async def run_analysis(self, data: Any, analysis_type: str) -> Dict[str, Any]:
        """
        Run predefined analysis on data
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Analysis results
        """
        analysis_code = self._get_analysis_code(analysis_type)
        
        if not analysis_code:
            return {
                "success": False,
                "error": f"Unknown analysis type: {analysis_type}"
            }
        
        # Inject data into context
        context = {"input_data": data}
        
        return await self.execute(analysis_code, context)
    
    def _get_analysis_code(self, analysis_type: str) -> Optional[str]:
        """
        Get predefined analysis code templates
        """
        templates = {
            "basic_stats": """
import json
import statistics

data = input_data
if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
    stats = {
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "mode": statistics.mode(data) if len(set(data)) < len(data) else None,
        "stdev": statistics.stdev(data) if len(data) > 1 else 0,
        "min": min(data),
        "max": max(data),
        "count": len(data)
    }
    print(json.dumps(stats, indent=2))
else:
    print("Invalid data format for statistics")
""",
            
            "price_optimization": """
import json

items = input_data
optimized = []

for item in items:
    cost = item.get('cost', 0)
    category = item.get('category', 'main')
    
    # Category-based markup
    markups = {
        'appetizer': 2.8,
        'main': 3.2,
        'dessert': 3.0,
        'beverage': 3.5
    }
    
    markup = markups.get(category, 3.0)
    suggested_price = cost * markup
    
    # Round to nearest 1000
    final_price = round(suggested_price / 1000) * 1000
    
    optimized.append({
        'name': item.get('name'),
        'cost': cost,
        'suggested_price': final_price,
        'margin_percentage': ((final_price - cost) / final_price * 100) if final_price > 0 else 0
    })

print(json.dumps(optimized, indent=2))
""",
            
            "demand_forecast": """
import json
import random  # Simplified for demonstration

# Simple demand forecasting
historical_data = input_data.get('historical', [])
item_name = input_data.get('item_name', 'Unknown')

# Generate simple forecast (would use actual ML in production)
if historical_data:
    avg_demand = sum(historical_data) / len(historical_data)
    trend = (historical_data[-1] - historical_data[0]) / len(historical_data) if len(historical_data) > 1 else 0
    
    forecast = []
    for i in range(30):  # 30 day forecast
        daily_forecast = avg_demand + (trend * i) + random.uniform(-5, 5)
        forecast.append(max(0, daily_forecast))
else:
    # Default forecast
    forecast = [random.uniform(10, 50) for _ in range(30)]

result = {
    'item': item_name,
    'forecast_days': 30,
    'daily_forecast': forecast,
    'total_expected': sum(forecast),
    'daily_average': sum(forecast) / len(forecast)
}

print(json.dumps(result, indent=2))
"""
        }
        
        return templates.get(analysis_type)