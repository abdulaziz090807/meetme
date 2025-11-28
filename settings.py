"""
Secure configuration module.
All sensitive data loaded from environment variables.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Secure configuration class."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from environment."""
        self._bot_token = os.getenv("BOT_TOKEN")
        if not self._bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self._admin_ids = [
            int(id.strip()) 
            for id in admin_ids_str.split(",") 
            if id.strip().isdigit()
        ]
        
        self._database_path = os.getenv("DATABASE_PATH", "meet_me.db")
        self._pending_timeout = int(os.getenv("PENDING_PAIR_TIMEOUT", "48"))
        self._rejection_timeout = int(os.getenv("REJECTION_TIMEOUT", "72"))
    
    @property
    def bot_token(self) -> str:
        return self._bot_token
    
    @property
    def admin_ids(self) -> List[int]:
        return self._admin_ids.copy()
    
    @property
    def database_path(self) -> str:
        return self._database_path
    
    @property
    def pending_timeout(self) -> int:
        return self._pending_timeout
    
    @property
    def rejection_timeout(self) -> int:
        return self._rejection_timeout
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self._admin_ids


# Singleton instance
config = Config()


# Available courses
COURSES = [
    "Computer Science",
    "Engineering", 
    "Business",
    "Medicine",
    "Law",
    "Arts",
    "Sciences",
    "Other"
]

MIN_AGE = 16
MAX_AGE = 100
DEFAULT_AGE_DIFF = 1  # Default age difference filter