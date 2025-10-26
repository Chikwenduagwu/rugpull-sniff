"""
SolSniffer API Configuration
CREATE: config/solsniffer_config.py
"""

import os
from dotenv import load_dotenv

load_dotenv()


class SolSnifferConfig:
    """Configuration for SolSniffer API."""
    
    # SolSniffer API settings
    API_KEY = os.getenv("SOLSNIFFER_API_KEY", "to5p72yao22ajhlxiw6bvj8hogt896")
    BASE_URL = "https://solsniffer.com"
    API_PATH = "/api/v2/token"
    
    # Full API endpoint
    FULL_URL = f"{BASE_URL}{API_PATH}"
    
    # Timeout for API requests (seconds)
    TIMEOUT = int(os.getenv("SOLSNIFFER_TIMEOUT", "30"))
    
    # Maximum retries for failed requests
    MAX_RETRIES = int(os.getenv("SOLSNIFFER_MAX_RETRIES", "3"))
    
    # Cache settings
    ENABLE_CACHE = os.getenv("SOLSNIFFER_ENABLE_CACHE", "True").lower() == "true"
    CACHE_TTL_HOURS = int(os.getenv("SOLSNIFFER_CACHE_TTL_HOURS", "24"))  # 24 hours
    
    @classmethod
    def get_token_url(cls, contract_address: str) -> str:
        """
        Generate SolSniffer API URL for a contract address.
        
        Args:
            contract_address: Solana contract address
            
        Returns:
            Full API URL with contract address
        """
        return f"{cls.FULL_URL}/{contract_address}"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate SolSniffer configuration."""
        if not cls.API_KEY:
            print("⚠️ SOLSNIFFER_API_KEY is not set (using default)")
        return True