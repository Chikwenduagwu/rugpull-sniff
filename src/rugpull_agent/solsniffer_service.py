"""
SolSniffer API Service for fetching token analysis.
CREATE THIS FILE: src/rugpull_agent/solsniffer_service.py
"""

import aiohttp
import logging
from typing import Dict, Optional
from config.solsniffer_config import SolSnifferConfig

logger = logging.getLogger(__name__)


class SolSnifferService:
    """Service for fetching token analysis from SolSniffer API."""
    
    def __init__(self):
        self.config = SolSnifferConfig()
        logger.info(f"🔍 SolSniffer API initialized")
    
    async def analyze_token(self, contract_address: str) -> Optional[Dict]:
        """
        Analyze a Solana token using SolSniffer API.
        
        Args:
            contract_address: Solana contract address (CA)
            
        Returns:
            Dict containing token analysis or None if failed
        """
        # Construct the full URL with contract address
        url = f"{self.config.FULL_URL}/{contract_address}"
        
        logger.info(f"🔍 Analyzing token: {contract_address}")
        logger.info(f"📡 API URL: {url}")
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Add headers with API key
                headers = {
                    'User-Agent': 'RugPullChecker/1.0',
                    'Accept': 'application/json',
                    'X-API-KEY': self.config.API_KEY
                }
                
                logger.info(f"🔑 Using API Key: {self.config.API_KEY[:10]}...")
                
                async with session.get(url, headers=headers, ssl=False) as response:
                    response_text = await response.text()
                    logger.info(f"📥 Response Status: {response.status}")
                    logger.info(f"📥 Response (first 500 chars): {response_text[:500]}")
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            logger.info(f"✅ Analysis complete for: {contract_address}")
                            return data
                        except Exception as e:
                            logger.error(f"❌ JSON parse error: {str(e)}")
                            logger.error(f"Response text: {response_text}")
                            return {
                                "error": "Parse error",
                                "contract_address": contract_address,
                                "message": f"Failed to parse API response: {str(e)}"
                            }
                        
                    elif response.status == 404:
                        logger.warning(f"❌ Token not found: {contract_address}")
                        return {
                            "error": "Token not found",
                            "contract_address": contract_address,
                            "message": "This contract address was not found. Please verify the address is correct."
                        }
                        
                    elif response.status == 429:
                        logger.warning(f"⚠️ Rate limit exceeded")
                        return {
                            "error": "Rate limit",
                            "contract_address": contract_address,
                            "message": "API rate limit exceeded. Please try again later."
                        }
                        
                    else:
                        logger.error(f"❌ API error: {response.status}")
                        logger.error(f"Response: {response_text}")
                        return {
                            "error": "API error",
                            "contract_address": contract_address,
                            "message": f"The SolSniffer API returned an error (Status: {response.status})"
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
                "message": "The API request timed out. Please try again."
            }
            
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return {
                "error": "Unexpected error",
                "contract_address": contract_address,
                "message": f"An unexpected error occurred: {str(e)}"
            }
    
    def format_analysis(self, analysis_data: Dict) -> str:
        """
        Format analysis data into readable text.
        
        Args:
            analysis_data: Analysis data from API
            
        Returns:
            Formatted analysis text
        """
        if "error" in analysis_data:
            return f"❌ {analysis_data['message']}"
        
        # SolSniffer returns nested data, let's handle it properly
        # Check if data is nested under 'data' key
        if "data" in analysis_data:
            data = analysis_data["data"]
        else:
            data = analysis_data
        
        # Extract token info
        token_info = data.get("tokenInfo", {})
        token_metadata = data.get("tokenMetadata", {})
        security_info = data.get("securityInfo", {})
        
        # Get basic info
        ca = token_metadata.get("address", data.get("address", "Unknown"))
        token_name = token_metadata.get("name", data.get("name", "Unknown Token"))
        symbol = token_metadata.get("symbol", data.get("symbol", "???"))
        
        # Get risk info from security
        audit_risk = security_info.get("auditRisk", {})
        
        # Calculate simple risk score based on flags
        risk_score = 0
        risk_factors = []
        
        if not audit_risk.get("mintDisabled", False):
            risk_score += 20
            risk_factors.append("⚠️ Mint authority not disabled")
        
        if not audit_risk.get("freezeDisabled", False):
            risk_score += 20
            risk_factors.append("⚠️ Freeze authority not disabled")
        
        if not audit_risk.get("lpBurned", False):
            risk_score += 30
            risk_factors.append("⚠️ Liquidity pool not burned")
        
        if audit_risk.get("top10Holders", False):
            risk_score += 15
            risk_factors.append("⚠️ High concentration in top 10 holders")
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "🔴 HIGH RISK"
        elif risk_score >= 30:
            risk_level = "🟡 MODERATE RISK"
        else:
            risk_level = "🟢 LOW RISK"
        
        # Get price and market cap
        price = token_info.get("price", 0)
        mkt_cap = token_info.get("mktCap", 0)
        supply = token_info.get("supplyAmount", 0)
        
        # Format output
        output = f"""
**Token Analysis: {token_name} ({symbol})**
Contract Address: `{ca}`

**Risk Assessment:**
- Risk Level: {risk_level}
- Risk Score: {risk_score}/100

**Token Info:**
- Price: ${price:,.10f}
- Market Cap: ${mkt_cap:,.2f}
- Supply: {supply:,.0f}

**Security Audit:**
- Mint Authority: {"✅ Disabled" if audit_risk.get("mintDisabled") else "❌ Active"}
- Freeze Authority: {"✅ Disabled" if audit_risk.get("freezeDisabled") else "❌ Active"}
- LP Burned: {"✅ Yes" if audit_risk.get("lpBurned") else "❌ No"}
- Top 10 Concentration: {"⚠️ High" if audit_risk.get("top10Holders") else "✅ Normal"}

**Risk Factors:**
{chr(10).join(risk_factors) if risk_factors else "✅ No major risk factors detected"}
        """.strip()
        
        return output
    
    def _format_details(self, data: Dict) -> str:
        """Format detailed analysis information."""
        details = []
        
        # Add relevant details based on API response structure
        if "liquidity" in data:
            details.append(f"- Liquidity: ${data['liquidity']}")
        
        if "liquidityUsd" in data:
            details.append(f"- Liquidity: ${data['liquidityUsd']:,.2f}")
        
        if "holders" in data:
            details.append(f"- Holders: {data['holders']}")
        
        if "holderCount" in data:
            details.append(f"- Holders: {data['holderCount']}")
        
        if "isRenounced" in data:
            status = "✅ Renounced" if data["isRenounced"] else "⚠️ Not Renounced"
            details.append(f"- Ownership: {status}")
        
        if "ownershipRenounced" in data:
            status = "✅ Renounced" if data["ownershipRenounced"] else "⚠️ Not Renounced"
            details.append(f"- Ownership: {status}")
        
        if "isMintable" in data:
            status = "⚠️ Mintable" if data["isMintable"] else "✅ Not Mintable"
            details.append(f"- Mint Status: {status}")
        
        if "mintable" in data:
            status = "⚠️ Mintable" if data["mintable"] else "✅ Not Mintable"
            details.append(f"- Mint Status: {status}")
        
        if "isFreezable" in data:
            status = "⚠️ Freezable" if data["isFreezable"] else "✅ Not Freezable"
            details.append(f"- Freeze Authority: {status}")
        
        if "freezable" in data:
            status = "⚠️ Freezable" if data["freezable"] else "✅ Not Freezable"
            details.append(f"- Freeze Authority: {status}")
        
        if "topHolderPercent" in data:
            details.append(f"- Top Holder: {data['topHolderPercent']}%")
        
        if "top10HolderPercent" in data:
            details.append(f"- Top 10 Holders: {data['top10HolderPercent']}%")
        
        if "createdAt" in data:
            details.append(f"- Created: {data['createdAt']}")
        
        if "lpBurned" in data:
            status = "✅ LP Burned" if data["lpBurned"] else "⚠️ LP Not Burned"
            details.append(f"- Liquidity Pool: {status}")
        
        return "\n".join(details) if details else "No additional details available"