import logging
import aiohttp
from sentient_agent_framework import (
    AbstractAgent,
    Session,
    Query,
    ResponseHandler
)
from .solsniffer_service import SolSnifferService
from .llm_service import LLMService
from utils.ca_parser import CAParser
from utils.cache import CacheManager
from config.solsniffer_config import SolSnifferConfig
from config.llm_config import LLMConfig

logger = logging.getLogger(__name__)


class RugPullAgent(AbstractAgent):
    """
    Rug Pull Checker Agent - Analyzes Solana tokens for rug pull risks.
    AI handles ALL formatting and analysis.
    """
    
    GREETING_PATTERNS = [
        "who are you",
        "what can you do",
        "what are you",
        "hello",
        "hi there",
        "hey there",
        "help me",
        "about you"
    ]
    
    def __init__(self, name: str = "Rug Pull Checker"):
        super().__init__(name)
        
        logger.info(f"🔍 Initializing {name}...")
        
       
        self.solsniffer_service = SolSnifferService()
        self.llm_service = LLMService()
        self.ca_parser = CAParser()
        
        
        if SolSnifferConfig.ENABLE_CACHE:
            self.cache_manager = CacheManager(
                cache_dir=".cache",
                ttl_hours=SolSnifferConfig.CACHE_TTL_HOURS
            )
        else:
            self.cache_manager = None
        
        logger.info(f"✅ {name} initialized successfully")
        self._print_startup_info()
    
    def _print_startup_info(self):
        """Print startup information."""
        print("\n" + "=" * 60)
        print(f"🔍 {self.name} Started")
        print("=" * 60)
        print(f"🔗 SolSniffer API: {SolSnifferConfig.BASE_URL}")
        print(f"🤖 LLM Model: {LLMConfig.MODEL}")
        print(f"💾 Cache: {'Enabled' if SolSnifferConfig.ENABLE_CACHE else 'Disabled'}")
        if SolSnifferConfig.ENABLE_CACHE:
            print(f"   - TTL: {SolSnifferConfig.CACHE_TTL_HOURS} hours")
        print(f"🎯 Mode: AI-First (All responses via AI)")
        print(f"🎯 Status: Ready to analyze tokens")
        print("=" * 60 + "\n")
    
    async def assist(
        self,
        session: Session,
        query: Query,
        response_handler: ResponseHandler
    ):
        """Process user query and analyze token."""
        
        try:
            user_prompt = query.prompt.strip()
            logger.info(f"📨 Received query: {user_prompt[:100]}...")
            
            
            contract_address = self.ca_parser.extract_contract_address(user_prompt)
            logger.info(f"🔍 CA Parser result: {contract_address}")
            
            
            if contract_address:
                logger.info(f"✅ Valid CA detected: {contract_address}")
                await self._process_token_analysis(
                    contract_address, 
                    user_prompt, 
                    response_handler
                )
                return
            
           
            if self._is_greeting(user_prompt):
                logger.info("👋 Greeting detected")
                await self._handle_greeting(response_handler)
                return
            
            
            logger.info("💬 Normal chat conversation")
            await self._handle_normal_chat(user_prompt, response_handler)
            
        except Exception as e:
            logger.error(f"❌ Error in assist(): {str(e)}", exc_info=True)
            await response_handler.emit_text_block(
                "ERROR",
                f"❌ **Error**\n\nAn unexpected error occurred: {str(e)}\n\nPlease try again."
            )
            await response_handler.complete()
    
    async def _process_token_analysis(
        self,
        contract_address: str,
        user_prompt: str,
        response_handler: ResponseHandler
    ):
        """Process token analysis - AI handles everything."""
        
        try:
            
            cache_key = f"token_analysis_{contract_address}"
            if self.cache_manager:
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info(f"💾 Cache hit for: {contract_address}")
                    
                    
                    await response_handler.emit_text_block(
                        "AI_ANALYSIS",
                        f"✨ **[Cached Analysis]**\n\n{cached_result.get('ai_response', '')}"
                    )
                    
                    await response_handler.complete()
                    return
            
            
            logger.info(f"🔍 Fetching analysis from SolSniffer API...")
            await response_handler.emit_text_block(
                "STATUS",
                f"🔍 **Analyzing Token**\n\n`{contract_address[:8]}...{contract_address[-8:]}`\n\nFetching data..."
            )
            
            
            analysis_data = await self.solsniffer_service.analyze_token(contract_address)
            
            
            if not analysis_data or "error" in analysis_data:
                error_msg = analysis_data.get("message", "Failed to analyze token") if analysis_data else "Failed to analyze token"
                logger.error(f"❌ API Error: {error_msg}")
                await response_handler.emit_text_block(
                    "ERROR",
                    f"❌ **Error**\n\n{error_msg}\n\n**Possible reasons:**\n- Invalid contract address\n- Token not found\n- API connectivity issue\n\nPlease verify and try again."
                )
                await response_handler.complete()
                return
            
            logger.info(f"✅ Successfully fetched analysis data")
            logger.info(f"📊 Data keys: {list(analysis_data.keys())}")
            
            
            await response_handler.emit_text_block(
                "STATUS",
                "🤖 **AI Processing**\n\nAnalyzing token data with AI..."
            )
            
            
            ai_response = await self.llm_service.analyze_token(
                contract_address=contract_address,
                analysis_data=analysis_data,
                user_question=user_prompt
            )
            
            
            await response_handler.emit_text_block(
                "AI_ANALYSIS",
                ai_response
            )
            
            
            if self.cache_manager:
                cache_data = {
                    "analysis_data": analysis_data,
                    "ai_response": ai_response,
                    "contract_address": contract_address
                }
                await self.cache_manager.set(cache_key, cache_data)
                logger.info(f"💾 Cached result for: {contract_address}")
            
            await response_handler.complete()
            logger.info("✅ Analysis completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in _process_token_analysis(): {str(e)}", exc_info=True)
            await response_handler.emit_text_block(
                "ERROR",
                f"❌ **Error Processing Analysis**\n\n{str(e)}\n\nPlease try again."
            )
            await response_handler.complete()
    
    def _is_greeting(self, prompt: str) -> bool:
        """Check if the prompt is a greeting."""
        prompt_lower = prompt.lower()
        
        has_long_word = any(len(word) >= 32 for word in prompt.split())
        if has_long_word:
            return False
        return any(pattern in prompt_lower for pattern in self.GREETING_PATTERNS)
    
    async def _handle_greeting(self, response_handler: ResponseHandler):
        """Handle greeting queries."""
        greeting_text = f"""
👋 **Hello! I'm {self.name}**

I analyze Solana tokens to detect potential rug pulls and scams using SolSniffer API and AI.

**What I Can Do:**
• Analyze token contract addresses for rug pull risks
• Check liquidity, holders, and ownership status
• Detect mint/freeze authorities
• Provide AI-powered risk assessment
• Give clear verdicts: SAFE, MODERATE RISK, or HIGH RISK

**How to Use:**
Simply paste a Solana contract address (CA) and I'll analyze it!

**Examples:**
• `Is this token safe? 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`
• `Check this CA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`
• `[paste any Solana CA here]`

**Ready to analyze!** Just paste a contract address. 🚀
        """.strip()
        
        await response_handler.emit_text_block(
            "GREETING",
            greeting_text
        )
        await response_handler.complete()
    
    async def _handle_normal_chat(self, user_prompt: str, response_handler: ResponseHandler):
        """Handle normal conversation without CA."""
        
        try:
            prompt = f"""The user says: "{user_prompt}"

You are a Solana token rug pull checker assistant. The user is asking a general question that doesn't include a contract address.

Please respond helpfully about:
- What makes a token a rug pull
- How to identify scam tokens
- General crypto safety tips
- How to use this tool (just paste a Solana contract address)

Keep your response concise, helpful, and friendly."""

            payload = {
                "model": LLMConfig.MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful crypto safety assistant specializing in Solana tokens."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 512,
                "temperature": 0.7,
                "stream": False
            }
            
            url = f"{LLMConfig.BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {LLMConfig.API_KEY}",
                "Content-Type": "application/json"
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        await response_handler.emit_text_block(
                            "CHAT_RESPONSE",
                            content
                        )
                    else:
                        
                        await response_handler.emit_text_block(
                            "CHAT_RESPONSE",
                            "I'm here to help analyze Solana tokens for rug pull risks! 🔍\n\n"
                            "To get started, simply paste a Solana contract address.\n\n"
                            "**Example:** `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`"
                        )
        except Exception as e:
            logger.error(f"Error in normal chat: {str(e)}")
            await response_handler.emit_text_block(
                "CHAT_RESPONSE",
                "I'm a rug pull checker for Solana tokens! 🔍\n\n"
                "Just paste a contract address and I'll analyze it.\n\n"
                "**Example:** `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`"
            )
        
        await response_handler.complete()