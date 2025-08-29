# core/state_manager.py

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages global application state and persistence
    """
    
    def __init__(self, state_file: str = "state.json"):
        self.state_file = Path(state_file)
        self.state: Dict[str, Any] = {}
        self.load_state()
        logger.info("State manager initialized")
    
    def load_state(self) -> None:
        """Load state from file if exists"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logger.info(f"State loaded from {self.state_file}")
            except Exception as e:
                logger.error(f"Failed to load state: {str(e)}")
                self.state = {}
        else:
            self.state = {}
            logger.info("Starting with empty state")
    
    def save_state(self) -> None:
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            logger.debug("State saved successfully")
        except Exception as e:
            logger.error(f"Failed to save state: {str(e)}")
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value"""
        self.state[key] = {
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }
        self.save_state()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value"""
        if key in self.state:
            return self.state[key].get("value", default)
        return default
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update multiple state values"""
        for key, value in updates.items():
            self.set_state(key, value)
    
    def get_all_state(self) -> Dict[str, Any]:
        """Get all state values"""
        return {
            key: data.get("value") 
            for key, data in self.state.items()
        }
    
    def clear_state(self) -> None:
        """Clear all state"""
        self.state = {}
        self.save_state()
        logger.info("State cleared")