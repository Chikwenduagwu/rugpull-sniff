import aiohttp
import logging
import json
from typing import Dict
from config.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class LLMService:
    """Service for AI-powered token analysis."""
    
    
    SYSTEM_PROMPT = """You are an expert Solana token analyst specializing in detecting rug pulls and scams.

Your job is to:
1. Extract and present ALL relevant token information clearly
2. Explain what each metric means in simple terms
3. Identify red flags and green flags
4. Provide a clear risk assessment (LOW RISK / MODERATE RISK / HIGH RISK)
5. Give specific, actionable recommendations

Be thorough, accurate, and direct. If it's a scam, say so clearly.
Format your response with markdown for readability."""
    
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
        Get comprehensive AI analysis for a token.
        AI extracts and formats ALL data from the API response.
        """
        
        
        prompt = self._build_comprehensive_prompt(
            contract_address,
            analysis_data,
            user_question
        )
        
        
        payload = {
            "model": self.config.MODEL,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 2048,  
            "temperature": 0.7,
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
                        return f"❌ **Error**\n\nUnable to generate AI analysis (Status: {response.status}).\n\nPlease check your FIREWORKS_API_KEY in .env file."
                    
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return content
                    
        except Exception as e:
            logger.error(f"❌ LLM Error: {str(e)}", exc_info=True)
            return f"❌ **Error**\n\nFailed to generate AI analysis: {str(e)}"
    
    def _build_comprehensive_prompt(
        self,
        contract_address: str,
        analysis_data: Dict,
        user_question: str = None
    ) -> str:
        """Build a comprehensive prompt that includes ALL token data."""
        
        
        json_data = json.dumps(analysis_data, indent=2)
        
        
        data_size = len(json_data)
        logger.info(f"📊 Sending {data_size} bytes of data to AI")
        
        
        base_prompt = f"""Analyze this Solana token completely and thoroughly.

**CONTRACT ADDRESS:** {contract_address}

**COMPLETE API DATA:**
```json
{json_data}
```

**YOUR TASK:**
1. **Extract Token Information:**
   - Token name and symbol
   - Contract address
   - Price (format small numbers properly)
   - Market cap
   - Liquidity
   - Supply/circulation
   - Holder count
   - Any other relevant metrics you find

2. **Security Analysis:**
   - Check if mint authority is renounced/disabled
   - Check if freeze authority is renounced/disabled
   - Check if liquidity pool is burned/locked
   - Analyze holder distribution (top holders percentage)
   - Check for any other security flags in the data

3. **Risk Assessment:**
   - Calculate an overall risk score (0-100)
   - Assign a risk level: 🟢 LOW RISK / 🟡 MODERATE RISK / 🔴 HIGH RISK
   - List specific red flags (if any)
   - List specific green flags (if any)

4. **Clear Verdict:**
   - Is this token SAFE, MODERATE RISK, or HIGH RISK?
   - Should investors buy, be cautious, or avoid?
   - Specific reasons for your verdict

5. **Format Requirements:**
   - Use markdown formatting (headers, bold, lists, tables)
   - Make it visually clear and easy to scan
   - Include emojis for visual appeal
   - Put the most important info first

**IMPORTANT:** Extract ALL relevant information from the JSON data above. Don't skip any important fields. If data is nested (like inside "data", "tokenInfo", "securityInfo", etc.), make sure to look inside those objects."""

        
        if user_question:
            base_prompt = f"""User's question: "{user_question}"

{base_prompt}

Also answer the user's specific question in your response."""
        
        return base_prompt