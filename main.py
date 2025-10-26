import logging
import sys
from src.rugpull_agent.agent import RugPullAgent
from src.rugpull_agent.server import RugPullServerWithCORS


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the Rug Pull Checker Agent."""
    
    try:
        logger.info("=" * 60)
        logger.info("🔍 Rug Pull Checker Agent Starting...")
        logger.info("=" * 60)
        
        
        agent = RugPullAgent(name="Rug Pull Checker")
        
        
        server = RugPullServerWithCORS(
            agent,
            allow_origins=["*"]  
        )
        
        
        logger.info("🌐 CORS: Allowing all origins (*)")
        logger.info("⚠️  Remember to restrict origins in production!")
        logger.info("🚀 Server starting on http://0.0.0.0:8000")
        logger.info("💡 Test with: http://localhost:8000/health")
        logger.info("=" * 60 + "\n")
        
        server.run(host="0.0.0.0", port=8000)
        
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("👋 Shutting down gracefully...")
        logger.info("=" * 60)
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()