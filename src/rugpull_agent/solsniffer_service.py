import aiohttp
import logging
from typing import Dict, Optional
from config.solsniffer_config import SolSnifferConfig

logger = logging.getLogger(__name__)


class SolSnifferService:
    """Service for fetching token analysis from SolSniffer API."""
    
    def __init__(self):
        self.config = SolSnifferConfig()
        logger.info(f"🔍 SolSniffer API initialized: {self.config.BASE_URL}")
    
    async def analyze_token(self, contract_address: str) -> Optional[Dict]:
        """
        Fetch raw token analysis from SolSniffer API.
        Returns the complete JSON response for AI to process.
        
        Args:
            contract_address: Solana contract address (CA)
            
        Returns:
            Dict containing complete API response or error dict
        """
        url = f"{self.config.FULL_URL}/{contract_address}"
        
        logger.info(f"🔍 Fetching analysis for: {contract_address}")
        logger.info(f"📡 API URL: {url}")
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    'User-Agent': 'RugPullChecker/1.0',
                    'Accept': 'application/json',
                    'X-API-KEY': self.config.API_KEY
                }
                
                logger.info(f"🔑 Using API Key: {self.config.API_KEY[:10]}...")
                
                async with session.get(url, headers=headers, ssl=False) as response:
                    response_text = await response.text()
                    
                    logger.info(f"📥 HTTP Status: {response.status}")
                    logger.info(f"📥 Response Length: {len(response_text)} bytes")
                    logger.info(f"📥 Response Preview (first 500 chars):")
                    logger.info(response_text[:500])
                    
                    if response.status == 200:
                        try:
                            
                            data = await response.json()
                            
                            
                            logger.info(f"✅ Successfully parsed JSON")
                            logger.info(f"📊 Top-level keys: {list(data.keys())}")
                            
                            
                            if "data" in data and isinstance(data["data"], dict):
                                logger.info(f"📊 Nested 'data' keys: {list(data['data'].keys())}")
                            
                            
                            return data
                            
                        except Exception as e:
                            logger.error(f"❌ JSON parse error: {str(e)}")
                            logger.error(f"Response text: {response_text[:1000]}")
                            return {
                                "error": "Parse error",
                                "contract_address": contract_address,
                                "message": f"Failed to parse API response: {str(e)}",
                                "raw_response": response_text[:500]
                            }
                    
                    elif response.status == 404:
                        logger.warning(f"❌ Token not found: {contract_address}")
                        return {
                            "error": "Token not found",
                            "contract_address": contract_address,
                            "message": "This contract address was not found on SolSniffer. Please verify the address is correct."
                        }
                    
                    elif response.status == 429:
                        logger.warning(f"⚠️ Rate limit exceeded")
                        return {
                            "error": "Rate limit",
                            "contract_address": contract_address,
                            "message": "API rate limit exceeded. Please try again in a few moments."
                        }
                    
                    elif response.status == 401 or response.status == 403:
                        logger.error(f"❌ Authentication error: {response.status}")
                        return {
                            "error": "Authentication error",
                            "contract_address": contract_address,
                            "message": f"API authentication failed (Status: {response.status}). Check your SOLSNIFFER_API_KEY."
                        }
                    
                    else:
                        logger.error(f"❌ API error: {response.status}")
                        logger.error(f"Response: {response_text[:500]}")
                        return {
                            "error": "API error",
                            "contract_address": contract_address,
                            "message": f"SolSniffer API returned error (Status: {response.status})",
                            "raw_response": response_text[:500]
                        }
                        
        except aiohttp.ClientConnectionError as e:
            logger.error(f"❌ Connection error: {str(e)}")
            return {
                "error": "Connection error",
                "contract_address": contract_address,
                "message": "Could not connect to SolSniffer API. Please check your internet connection."
            }
        
        except aiohttp.ClientTimeout as e:
            logger.error(f"❌ Timeout error: {str(e)}")
            return {
                "error": "Timeout",
                "contract_address": contract_address,
                "message": "The API request timed out. The SolSniffer API may be slow. Please try again."
            }
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return {
                "error": "Unexpected error",
                "contract_address": contract_address,
                "message": f"An unexpected error occurred: {str(e)}"
            }