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
6. **ALWAYS show top holders with their individual addresses and percentages**

Be thorough, accurate, and direct. If it's a scam, say so clearly.
Format your response with markdown for readability.

CRITICAL: When showing top holders, you MUST list each holder's address individually with their percentage, not just aggregate statistics."""
    
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

**YOUR TASK - FOLLOW THIS EXACT FORMAT:**

## 🎯 RISK VERDICT (Show this first)
- **Risk Level:** 🟢 LOW RISK / 🟡 MODERATE RISK / 🔴 HIGH RISK
- **Risk Score:** X/100
- **Recommendation:** Buy / Be Cautious / Avoid

---

## 📊 TOKEN INFORMATION
- **Name:** [Token Name]
- **Symbol:** [Token Symbol]
- **Contract:** `{contract_address}`
- **Price:** $X.XX (format properly, use scientific notation if needed)
- **Market Cap:** $X,XXX,XXX
- **Total Supply:** X,XXX,XXX
- **Circulating Supply:** X,XXX,XXX
- **Holder Count:** XXX
- **Liquidity:** $X,XXX,XXX
- **Token Age:** X days/months

---

## 👥 TOP HOLDERS (!)

**⚠️ lists ⚠️**

Search the JSON data for fields like:
- `holders`, `topHolders`, `top_holders`
- `holderInfo`, `holder_info`
- Any array containing holder/wallet data

Then create a table like this:

| Rank | Address | Holdings | % of Supply |
|------|---------|----------|-------------|
| 1 | `abc123...xyz789` | 1,234,567 | 12.34% |
| 2 | `def456...uvw012` | 987,654 | 9.87% |
| 3 | `ghi789...rst345` | 765,432 | 7.65% |
| ... | ... | ... | ... |

**Concentration Analysis:**
- Top 5 holders own: XX.XX%
- Top 10 holders own: XX.XX%
- Top 20 holders own: XX.XX%
- **Risk Assessment:** [Is concentration too high? Is it distributed?]

**IF YOU CANNOT FIND HOLDER DATA IN THE JSON:**
State clearly: "⚠️ Holder address data not available in API response. Only showing aggregate statistics."

---

## 🔒 SECURITY ANALYSIS

### Mint Authority
- **Status:** ✅ Renounced / ❌ Active
- **Address:** [if available]
- **Risk:** [Explain the risk]

### Freeze Authority
- **Status:** ✅ Renounced / ❌ Active
- **Address:** [if available]
- **Risk:** [Explain the risk]

### Liquidity Pool
- **Status:** ✅ Burned / 🔒 Locked / ❌ Unlocked
- **LP Tokens Burned:** XX%
- **LP Tokens Locked:** XX%
- **Risk:** [Explain the risk]

### Other Security Flags
- List any other security-related findings from the data

---

## 🚩 RED FLAGS & 🟢 GREEN FLAGS

### 🚩 Red Flags:
- [List specific concerns]
- [Be specific about what makes this risky]

### 🟢 Green Flags:
- [List positive indicators]
- [Be specific about what makes this safe]

---

## 💡 FINAL VERDICT

**Overall Assessment:** [Detailed explanation]

**Should you invest?**
- [Clear yes/no/maybe with reasoning]

**Specific Recommendations:**
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

---

**CRITICAL REQUIREMENTS:**
1. ⚠️ **YOU MUST SHOW THE TOP HOLDERS TABLE** - Do not just say "Top 10 hold X%"
2. Extract holder addresses from fields like: `holders`, `topHolders`, `holderInfo`, `top_holders`, or any array with wallet/address data
3. If the data contains holder addresses, DISPLAY THEM in a table
4. Abbreviate long addresses: `abc123...xyz789`
5. Look inside ALL nested objects in the JSON (data.holders, data.tokenInfo.holders, etc.)
6. If you truly cannot find individual holder addresses, say so explicitly

**REMEMBER:** The goal is to show DETAILED holder breakdown, not just aggregate percentages!"""

        
        if user_question:
            base_prompt = f"""User's question: "{user_question}"

{base_prompt}

Make sure to address the user's specific question. If they asked about "top holders", prioritize showing the detailed holder breakdown table."""
        
        return base_prompt
