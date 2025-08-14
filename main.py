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
    
    # Initialize the agent
    agent = ClothingAgent(config_path=args.config)
    
    try:
        if args.setup_preferences:
            # Interactive preference setup
            await agent.setup_user_preferences()
            print("✅ User preferences have been set up successfully!")
            return
        
        if args.query:
            # Perform search
            print(f"🔍 Searching for: {args.query}")
            results = await agent.search(args.query)
            
            if results:
                print(f"✅ Found {len(results)} items:")
                for i, item in enumerate(results[:10], 1):  # Show top 10
                    print(f"{i}. {item.title}")
                    print(f"   Price: ${item.price}")
                    print(f"   Site: {item.site}")
                    print(f"   URL: {item.url}")
                    print("-" * 50)
                
                if args.output:
                    await agent.save_results(results, args.output)
                    print(f"💾 Results saved to {args.output}")
            else:
                print("❌ No items found matching your criteria")
        else:
            # Interactive mode
            print("👋 Welcome to Clothing Search Agent!")
            print("Type 'help' for commands or 'quit' to exit")
            
            while True:
                try:
                    query = input("\n🔍 Enter search query: ").strip()
                    
                    if query.lower() in ['quit', 'exit', 'q']:
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
                        else:
                            print("❌ No items found")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to run agent: {e}")
        sys.exit(1)
    
    print("👋 Thanks for using Clothing Search Agent!")


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
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Scroll to Top</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                height: 2000px;
                margin: 0;
                padding: 0;
                background: #f9f9f9;
            }
            #topBtn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 1000;
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 50px;
                cursor: pointer;
                font-size: 18px;
                display: none;
                transition: opacity 0.3s ease;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            #topBtn:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>

        <button id="topBtn" onclick="scrollToTop()">↑ Top</button>

        <script>
            const topBtn = document.getElementById("topBtn");

            window.addEventListener("scroll", () => {
                topBtn.style.display = (window.scrollY > 100) ? "block" : "none";
            });

            function scrollToTop() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        </script>

    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(debug=True)