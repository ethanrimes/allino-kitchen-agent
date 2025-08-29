# scripts/start_platform.py

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import MainOrchestrator
from config.logging_config import setup_logging

async def run_planning_cycle():
    """
    Run a single planning cycle immediately
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("Starting Ghost Kitchen AI Platform")
    logger.info("=" * 50)
    
    try:
        # Initialize orchestrator
        logger.info("Initializing Main Orchestrator...")
        orchestrator = MainOrchestrator()
        
        # Execute planning cycle
        logger.info("\n🚀 Starting Planning Cycle...")
        logger.info("This will:")
        logger.info("1. Research Colombian food market")
        logger.info("2. Create optimized menu")
        logger.info("3. Forecast demand")
        logger.info("4. Create social content")
        logger.info("5. Post to social channels\n")
        
        results = await orchestrator.execute_planning_cycle()
        
        # Display results
        logger.info("\n" + "=" * 50)
        logger.info("📊 PLANNING CYCLE RESULTS")
        logger.info("=" * 50)
        
        if results.get("status") == "completed":
            logger.info("✅ Planning cycle completed successfully!")
            
            # Show research insights
            if "research" in results.get("phases", {}):
                logger.info("\n📚 Research Insights:")
                research = results["phases"]["research"]
                for topic, data in list(research.items())[:3]:
                    logger.info(f"  • {topic}: Completed")
            
            # Show menu creation results
            if "menu_creation" in results.get("phases", {}):
                menu = results["phases"]["menu_creation"]
                logger.info(f"\n🍽️ Menu Created:")
                logger.info(f"  • Total items: {menu.get('total_items', 0)}")
                logger.info(f"  • Average price: ${menu.get('average_price_cop', 0):,.0f} COP")
                
                # Show sample items
                if menu.get("items"):
                    logger.info("  • Sample items:")
                    for item in menu["items"][:3]:
                        logger.info(f"    - {item.get('name', 'Unknown')}: ${item.get('price_cop', 0):,.0f} COP")
            
            # Show social media results
            if "social_posting" in results.get("phases", {}):
                social = results["phases"]["social_posting"]
                logger.info(f"\n📱 Social Media Posts:")
                logger.info(f"  • Total reach: {social.get('total_reach', 0):,} people")
                logger.info(f"  • Budget spent: ${social.get('budget_spent_cop', 0):,.0f} COP")
                
                for platform, result in social.get("posts", {}).items():
                    status = "✅" if result.get("status") in ["posted", "sent"] else "❌"
                    logger.info(f"  • {platform}: {status}")
        
        else:
            logger.error(f"❌ Planning cycle failed: {results.get('error', 'Unknown error')}")
        
        # Shutdown
        await orchestrator.shutdown()
        logger.info("\n✨ Platform shutdown complete")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise

async def run_continuous():
    """
    Run the orchestrator continuously
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Ghost Kitchen AI Platform in continuous mode")
    
    try:
        orchestrator = MainOrchestrator()
        
        # Run continuously (will execute planning cycle daily)
        await orchestrator.run()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        await orchestrator.shutdown()

def main():
    """
    Main entry point with menu
    """
    print("\n🍽️ Ghost Kitchen AI Platform 🤖")
    print("=" * 50)
    print("\nSelect operation mode:")
    print("1. Run single planning cycle (recommended for testing)")
    print("2. Run continuous mode (daily cycles)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == "1":
        print("\n▶️ Running single planning cycle...")
        asyncio.run(run_planning_cycle())
    elif choice == "2":
        print("\n▶️ Starting continuous mode (Ctrl+C to stop)...")
        asyncio.run(run_continuous())
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()