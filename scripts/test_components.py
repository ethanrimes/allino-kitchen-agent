# scripts/test_components.py

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import MainOrchestrator
from config.logging_config import setup_logging
from config.settings import settings

async def test_research_only():
    """Test only the research agent"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Testing Research Agent...")
    
    orchestrator = MainOrchestrator()
    research_agent = orchestrator.agents["research"]
    
    # Test with a simple query
    result = await research_agent.execute({
        "task": "research",
        "query": "Popular food delivery trends in Bogotá Colombia 2024",
        "depth": "standard"
    })
    
    logger.info(f"Research completed: {len(result.get('sources', []))} sources found")
    logger.info(f"Key insights: {result.get('key_insights', [])[:2]}")
    
    await orchestrator.shutdown()
    return result

async def test_menu_creation_only():
    """Test menu creation with mock data"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Testing Menu Creation Agent...")
    
    orchestrator = MainOrchestrator()
    menu_agent = orchestrator.agents["menu_creation"]
    
    # Mock research data
    mock_research = {
        "Colombian food trends": {
            "answer": "Fusion cuisine and healthy options are trending",
            "sources": ["mock_source"]
        }
    }
    
    result = await menu_agent.execute({
        "task": "create_menu",
        "research_data": mock_research,
        "constraints": {
            "max_items": 10,
            "price_range_cop": {"min": 15000, "max": 60000}
        }
    })
    
    logger.info(f"Menu created: {result.get('total_items', 0)} items")
    if result.get('items'):
        for item in result['items'][:3]:
            logger.info(f"  • {item.get('name', 'Unknown')}: ${item.get('price_cop', 0):,.0f} COP")
    
    await orchestrator.shutdown()
    return result

async def test_social_media_only():
    """Test social media posting with mock content"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Testing Social Media Agent...")
    
    orchestrator = MainOrchestrator()
    social_agent = orchestrator.agents["social_media"]
    
    # Mock content
    mock_content = {
        "instagram": {
            "text": "¡Nuevo menú disponible! 🍽️",
            "image_url": "https://placeholder.com/menu.jpg"
        },
        "facebook": {
            "text": "Descubre nuestras delicias",
            "link": "https://wa.me/573001234567"
        },
        "whatsapp": {
            "message": "Menú del día disponible"
        }
    }
    
    result = await social_agent.execute({
        "task": "post_content",
        "content": mock_content,
        "menu_data": {},
        "schedule": "immediate",
        "boost_budget_cop": 0  # No boost for testing
    })
    
    logger.info(f"Social media posting: {result.get('status')}")
    for platform, post_result in result.get('posts', {}).items():
        logger.info(f"  • {platform}: {post_result.get('status', 'unknown')}")
    
    await orchestrator.shutdown()
    return result

async def test_specific_component():
    """Interactive component tester"""
    print("\n🧪 Component Testing Menu")
    print("=" * 50)
    print("1. Test Research Agent (uses Perplexity API)")
    print("2. Test Menu Creation (uses OpenAI)")
    print("3. Test Social Media Posting (uses Social APIs)")
    print("4. Test All Components Sequentially")
    print("5. Exit")
    
    choice = input("\nSelect component to test (1-5): ")
    
    if choice == "1":
        await test_research_only()
    elif choice == "2":
        await test_menu_creation_only()
    elif choice == "3":
        await test_social_media_only()
    elif choice == "4":
        print("\n📋 Testing all components...")
        await test_research_only()
        await test_menu_creation_only()
        await test_social_media_only()
    else:
        print("Exiting...")

if __name__ == "__main__":
    asyncio.run(test_specific_component())