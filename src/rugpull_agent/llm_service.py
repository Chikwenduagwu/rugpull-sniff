"""
LLM Service for AI-powered rug pull analysis.
REPLACE: src/rugpull_agent/llm_service.py WITH THIS FILE
"""

import aiohttp
import logging
import json
from typing import Dict
from config.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class LLMService:
    """Service for AI-powered token analysis."""
    
    def __init__(self):
        self.config = LLMConfig()
        
        if not self.config.validate():
            raise ValueError("Invalid LLM configuration")
        
        self.headers = {
            "Authorization": f"Bearer {self.config.API_KEY}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"🤖 LLM initialized: {self.config.MODEL}")
    
    async def analyze_token(
        self, 
        contract_address: str, 
        analysis_data: Dict,
        user_question: str = None
    ) -> str:
        """
        Get AI analysis for a token.
        
        Args:
            contract_address: The contract address
            analysis_data: Token analysis data from SolSniffer
            user_question: Optional specific question
            
        Returns:
            AI-generated analysis and verdict
        """
        
        # Build the prompt
        prompt = self._build_analysis_prompt(
            contract_address,
            analysis_data,
            user_question
        )
        
        # Get non-streaming response
        payload = {
            "model": self.config.MODEL,
            "messages": [
                {"role": "system", "content": self.config.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.MAX_TOKENS,
            "temperature": self.config.TEMPERATURE,
            "top_p": self.config.TOP_P,
            "stream": False
        }
        
        url = f"{self.config.BASE_URL}/chat/completions"
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    url, 
                    json=payload, 
                    headers=self.headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"❌ LLM API error: {response.status} - {error_text}")
                        return f"Error: Unable to generate AI analysis (Status: {response.status}). Please check your FIREWORKS_API_KEY."
                    
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
                    
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}", exc_info=True)
            return f"Error generating AI analysis: {str(e)}"
    
    def _build_analysis_prompt(
        self,
        contract_address: str,
        analysis_data: Dict,
        user_question: str = None
    ) -> str:
        """Build a detailed prompt for AI analysis."""
        
        # Extract key data (with fallbacks for different API response structures)
        token_name = analysis_data.get("tokenName") or analysis_data.get("name") or "Unknown Token"
        symbol = analysis_data.get("symbol") or "???"
        risk_level = analysis_data.get("riskLevel") or "Unknown"
        risk_score = analysis_data.get("riskScore") or 0
        
        # Build prompt
        if user_question:
            prompt = f"""User asks: "{user_question}"

Here is the token analysis data:

**Token:** {token_name} ({symbol})
**Contract Address:** {contract_address}
**Risk Level:** {risk_level}
**Risk Score:** {risk_score}/100

**Full Analysis Data:**
{json.dumps(analysis_data, indent=2)}

Please provide a comprehensive analysis that:
1. Explains what the risk indicators mean
2. Highlights any red flags
3. Gives a clear verdict (SAFE / MODERATE RISK / HIGH RISK)
4. Provides specific reasons
5. Advises the user what to do

Answer the user's specific question while covering these points."""
        else:
            prompt = f"""Analyze this Solana token:

**Token:** {token_name} ({symbol})
**Contract Address:** {contract_address}
**Risk Level:** {risk_level}
**Risk Score:** {risk_score}/100

**Full Analysis Data:**
{json.dumps(analysis_data, indent=2)}

Provide a comprehensive analysis covering:
1. Overall safety assessment
2. Red flags (if any)
3. Green flags (if any)
4. Clear verdict: SAFE / MODERATE RISK / HIGH RISK
5. Specific recommendations for investors

Be direct and honest. If it's a rug pull, say so clearly."""
        
        return prompt