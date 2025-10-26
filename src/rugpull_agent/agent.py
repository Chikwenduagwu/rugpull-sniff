"""
Rug Pull Checker Agent - Main Agent Implementation
REPLACE: src/rugpull_agent/agent.py WITH THIS FILE
"""

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
        
        # Initialize services
        self.solsniffer_service = SolSnifferService()
        self.llm_service = LLMService()
        self.ca_parser = CAParser()
        
        # Initialize cache if enabled
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
        print(f"🎯 Response Mode: Full JSON")
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
            logger.info(f"📨 Query: {user_prompt[:100]}...")
            
            # Try to extract contract address FIRST (before checking greetings)
            contract_address = self.ca_parser.extract_contract_address(user_prompt)
            logger.info(f"🔍 CA Parser result: {contract_address}")
            
            # If we found a CA, process it (even if there are greeting words)
            if contract_address:
                logger.info(f"🔍 Found CA: {contract_address}")
                await self._process_token_analysis(
                    contract_address, 
                    user_prompt, 
                    response_handler
                )
                return
            
            # Check for greeting
            if self._is_greeting(user_prompt):
                await self._handle_greeting(response_handler)
                return
            
            # No CA found - have a normal chat conversation
            await self._handle_normal_chat(user_prompt, response_handler)
            
        except Exception as e:
            logger.error(f"❌ Error processing query: {str(e)}", exc_info=True)
            await response_handler.emit_json(
                "ERROR",
                {
                    "status": "error",
                    "message": f"An error occurred: {str(e)}",
                    "error_type": type(e).__name__
                }
            )
            await response_handler.complete()
    
    async def _process_token_analysis(
        self,
        contract_address: str,
        user_prompt: str,
        response_handler: ResponseHandler
    ):
        """Process token analysis for a given contract address."""
        
        # Check cache first
        cache_key = contract_address
        if self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.info(f"💾 Cache hit for: {contract_address}")
                
                # Send formatted text response instead of JSON
                await response_handler.emit_text_block(
                    "ANALYSIS",
                    f"✨ **Found cached analysis**\n\n{cached_result.get('formatted_analysis', '')}"
                )
                
                await response_handler.emit_text_block(
                    "AI_VERDICT",
                    f"\n## 🤖 AI Analysis\n\n{cached_result.get('ai_verdict', '')}"
                )
                
                await response_handler.complete()
                return
        
        # Fetch token analysis from SolSniffer
        await response_handler.emit_text_block(
            "STATUS",
            f"🔍 Analyzing token: {contract_address[:8]}...{contract_address[-8:]}"
        )
        
        analysis_data = await self.solsniffer_service.analyze_token(contract_address)
        
        if not analysis_data or "error" in analysis_data:
            error_msg = analysis_data.get("message", "Failed to analyze token") if analysis_data else "Failed to analyze token"
            await response_handler.emit_text_block(
                "ERROR",
                f"❌ **Error**\n\n{error_msg}\n\nPlease check the contract address and try again."
            )
            await response_handler.complete()
            return
        
        # Format analysis
        formatted_analysis = self.solsniffer_service.format_analysis(analysis_data)
        
        # Display formatted analysis
        await response_handler.emit_text_block(
            "ANALYSIS",
            formatted_analysis
        )
        
        # Get AI verdict
        await response_handler.emit_text_block(
            "STATUS",
            "🤖 Generating AI analysis..."
        )
        
        ai_verdict = await self.llm_service.analyze_token(
            contract_address=contract_address,
            analysis_data=analysis_data,
            user_question=user_prompt
        )
        
        # Display AI verdict
        await response_handler.emit_text_block(
            "AI_VERDICT",
            f"\n## 🤖 AI Analysis\n\n{ai_verdict}"
        )
        
        # Cache the result
        if self.cache_manager:
            cache_data = {
                "analysis_data": analysis_data,
                "formatted_analysis": formatted_analysis,
                "ai_verdict": ai_verdict
            }
            await self.cache_manager.set(cache_key, cache_data)
            logger.info(f"💾 Cached result for: {contract_address}")
        
        await response_handler.complete()
        logger.info("✅ Query processed successfully")
    
    def _is_greeting(self, prompt: str) -> bool:
        """Check if the prompt is a greeting."""
        prompt_lower = prompt.lower()
        return any(
            pattern in prompt_lower 
            for pattern in self.GREETING_PATTERNS
        )
    
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
• `I need to know whether this is a rug pull: [paste CA here]`

**Ready to analyze!** Just paste a contract address. 🚀
        """.strip()
        
        await response_handler.emit_text_block(
            "GREETING",
            greeting_text
        )
        await response_handler.complete()
    
    async def _handle_normal_chat(self, user_prompt: str, response_handler: ResponseHandler):
        """Handle normal conversation without CA."""
        
        # Use LLM for general conversation
        try:
            prompt = f"""The user says: "{user_prompt}"

You are a Solana token rug pull checker assistant. The user is asking a general question that doesn't include a contract address.

Please respond helpfully about:
- What makes a token a rug pull
- How to identify scam tokens
- General crypto safety tips
- How to use this tool (just paste a Solana contract address)

Keep your response concise and helpful."""

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
                        # Fallback response if API fails
                        await response_handler.emit_text_block(
                            "CHAT_RESPONSE",
                            "I'm here to help analyze Solana tokens for rug pull risks! 🔍\n\n"
                            "To get started, simply paste a Solana contract address and I'll analyze it for you.\n\n"
                            "**Example:** `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`\n\n"
                            "I can help you identify:\n"
                            "• Mint/freeze authorities\n"
                            "• Liquidity issues\n"
                            "• Holder concentration\n"
                            "• Overall rug pull risk"
                        )
        except Exception as e:
            logger.error(f"Error in normal chat: {str(e)}")
            await response_handler.emit_text_block(
                "CHAT_RESPONSE",
                "I'm a rug pull checker for Solana tokens! 🔍\n\n"
                "Just paste a contract address and I'll analyze it for you.\n\n"
                "**Example:** `Check this CA: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263`"
            )
        
        await response_handler.complete()