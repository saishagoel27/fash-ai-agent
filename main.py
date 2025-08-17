#!/usr/bin/env python3
"""
Main entry point for the Clothing Search Agent
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from agents.clothing_agent import ClothingAgent
from config.settings import Settings
from utils.helpers import setup_logging
from logger import logger


async def main():
    """Main function to run the clothing search agent"""
    parser = argparse.ArgumentParser(description="Clothing Search Agent")
    parser.add_argument(
        "--query", 
        type=str, 
        help="Search query for clothing items"
    )
    parser.add_argument(
        "--setup-preferences", 
        action="store_true",
        help="Set up user preferences"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    # Initialize settings and logging
    settings = Settings()
    setup_logging(settings.log_level, settings.log_file)
    logger.info("🚀 Application started")

    # Initialize the agent
    agent = ClothingAgent(config_path=args.config)
    
    try:
        if args.setup_preferences:
            # Interactive preference setup
            await agent.setup_user_preferences()
            logger.info("✅ User preferences have been set up successfully")
            return
        
        if args.query:
            logger.info(f"🔍 Searching for query: {args.query}")
            results = await agent.search(args.query)
            
            if results:
                logger.info(f"✅ Found {len(results)} items for query '{args.query}'")
                for i, item in enumerate(results[:10], 1):  # Show top 10
                    print(f"{i}. {item.title}")
                    print(f"   Price: ${item.price}")
                    print(f"   Site: {item.site}")
                    print(f"   URL: {item.url}")
                    print("-" * 50)
                
                if args.output:
                    await agent.save_results(results, args.output)
                    logger.info(f"💾 Results saved to {args.output}")
            else:
                logger.warning(f"No items found for query: {args.query}")
        else:
            # Interactive mode
            print("👋 Welcome to Clothing Search Agent!")
            print("Type 'help' for commands or 'quit' to exit")
            logger.info("Running in interactive mode")
            
            while True:
                try:
                    query = input("\n🔍 Enter search query: ").strip()
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        logger.info("User exited application")
                        break
                    elif query.lower() == 'help':
                        print_help()
                        continue
                    elif query:
                        results = await agent.search(query)
                        if results:
                            print(f"✅ Found {len(results)} items (showing top 5):")
                            for i, item in enumerate(results[:5], 1):
                                print(f"{i}. {item.title} - ${item.price} ({item.site})")
                            logger.debug(f"Displayed top {min(5, len(results))} results for query '{query}'")
                        else:
                            logger.warning(f"No results for query: {query}")
                
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt - shutting down gracefully")
                    break
                except Exception as e:
                    logger.error(f"Error in interactive loop: {e}", exc_info=True)
    
    except Exception as e:
        logger.critical(f"❌ Failed to run agent: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("👋 Application finished successfully")


def print_help():
    """Print help information"""
    help_text = """
Available commands:
- Type any clothing search query (e.g., "blue jeans size 32")
- 'help' - Show this help message
- 'quit' or 'exit' - Exit the application

Examples:
- "red summer dress size M under $50"
- "nike running shoes size 10"
- "leather jacket black medium"
"""
    print(help_text)


if __name__ == "__main__":
    asyncio.run(main())
