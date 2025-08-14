#!/usr/bin/env python3
"""
Demo script for Social Media Fashion Trends Integration
Showcases the new features from Issue #10
"""

import asyncio
import uuid
from datetime import datetime

from clothing_agent import ClothingAgent


async def demo_social_media_integration():
    """Demonstrate social media integration features"""
    print("🌟 Fash AI Agent - Social Media Integration Demo")
    print("=" * 60)
    
    # Initialize agent
    agent = ClothingAgent()
    user_session_id = str(uuid.uuid4())
    
    print(f"👤 User Session ID: {user_session_id}")
    print()
    
    try:
        # Demo 1: Enhanced search with social media
        print("🔍 Demo 1: Enhanced Search with Social Media")
        print("-" * 40)
        query = "summer dress"
        print(f"Searching for: '{query}' with social media integration...")
        
        results = await agent.search_with_social_media(
            query, 
            user_session_id=user_session_id,
            include_trends=True,
            max_results=20
        )
        
        print(f"✅ Found {len(results)} items (e-commerce + social media)")
        
        # Show sample results
        for i, item in enumerate(results[:5], 1):
            source = "📌 Pinterest" if item.site == "pinterest" else "📷 Instagram" if item.site == "instagram" else "🛒 E-commerce"
            score = f" (Score: {item.preference_score:.2f})" if item.preference_score else ""
            print(f"  {i}. {item.title[:50]}... {source}{score}")
        
        print()
        
        # Demo 2: Trending fashion
        print("🔥 Demo 2: Trending Fashion Content")
        print("-" * 40)
        print("Getting trending fashion from social media...")
        
        trending_results = await agent.get_trending_fashion(
            user_session_id=user_session_id,
            max_results=15
        )
        
        print(f"✅ Found {len(trending_results)} trending items")
        
        # Show sample trending items
        for i, item in enumerate(trending_results[:5], 1):
            source = "📌 Pinterest" if item.site == "pinterest" else "📷 Instagram"
            score = f" (Score: {item.preference_score:.2f})" if item.preference_score else ""
            print(f"  {i}. {item.title[:50]}... {source}{score}")
        
        print()
        
        # Demo 3: Fashion inspiration
        print("💡 Demo 3: Fashion Inspiration")
        print("-" * 40)
        style_keywords = ["vintage", "bohemian"]
        print(f"Getting inspiration for: {', '.join(style_keywords)}")
        
        inspiration_results = await agent.get_fashion_inspiration(
            style_keywords,
            user_session_id=user_session_id,
            max_results=15
        )
        
        print(f"✅ Found {len(inspiration_results)} inspirational items")
        
        # Show sample inspiration items
        for i, item in enumerate(inspiration_results[:5], 1):
            source = "📌 Pinterest" if item.site == "pinterest" else "📷 Instagram"
            score = f" (Score: {item.preference_score:.2f})" if item.preference_score else ""
            print(f"  {i}. {item.title[:50]}... {source}{score}")
        
        print()
        
        # Demo 4: Seasonal trends
        print("🍂 Demo 4: Seasonal Fashion Trends")
        print("-" * 40)
        season = "summer"
        print(f"Getting {season} fashion trends...")
        
        seasonal_results = await agent.get_seasonal_trends(
            season,
            user_session_id=user_session_id,
            max_results=15
        )
        
        print(f"✅ Found {len(seasonal_results)} {season} trend items")
        
        # Show sample seasonal items
        for i, item in enumerate(seasonal_results[:5], 1):
            source = "📌 Pinterest" if item.site == "pinterest" else "📷 Instagram"
            score = f" (Score: {item.preference_score:.2f})" if item.preference_score else ""
            print(f"  {i}. {item.title[:50]}... {source}{score}")
        
        print()
        
        # Demo 5: User feedback simulation
        print("👍 Demo 5: User Feedback System")
        print("-" * 40)
        print("Simulating user feedback on items...")
        
        # Record some feedback
        if results:
            # Like first item
            agent.record_user_feedback(
                results[0], 'like', user_session_id, query
            )
            print(f"  ✅ Liked: {results[0].title[:40]}...")
            
            # Save second item
            if len(results) > 1:
                agent.record_user_feedback(
                    results[1], 'save', user_session_id, query
                )
                print(f"  ✅ Saved: {results[1].title[:40]}...")
            
            # Dislike third item
            if len(results) > 2:
                agent.record_user_feedback(
                    results[2], 'dislike', user_session_id, query
                )
                print(f"  ✅ Disliked: {results[2].title[:40]}...")
        
        print()
        
        # Demo 6: User preferences summary
        print("📊 Demo 6: User Preferences Summary")
        print("-" * 40)
        
        preferences = agent.get_user_preferences_summary(user_session_id)
        
        if preferences:
            print("User Preferences:")
            if preferences.get('preferences', {}).get('sites'):
                print("  📍 Preferred sites:", list(preferences['preferences']['sites'].keys())[:3])
            
            if preferences.get('preferences', {}).get('categories'):
                print("  🏷️  Preferred categories:", list(preferences['preferences']['categories'].keys())[:3])
            
            if preferences.get('preferences', {}).get('brands'):
                print("  🏪 Preferred brands:", list(preferences['preferences']['brands'].keys())[:3])
            
            print(f"  📈 Total feedback count: {preferences.get('total_feedback_count', 0)}")
        
        print()
        
        # Demo 7: Personalized recommendations
        print("🎯 Demo 7: Personalized Recommendations")
        print("-" * 40)
        print("Getting personalized recommendations based on feedback...")
        
        recommendations = agent.get_recommendations(user_session_id, max_results=10)
        
        print(f"✅ Found {len(recommendations)} personalized recommendations")
        
        # Show sample recommendations
        for i, item in enumerate(recommendations[:5], 1):
            score = f" (Score: {item.preference_score:.2f})" if item.preference_score else ""
            print(f"  {i}. {item.title[:50]}... {score}")
        
        print()
        
        # Demo 8: Brand trends
        print("🏪 Demo 8: Brand Trends")
        print("-" * 40)
        brand = "nike"
        print(f"Getting trending content for {brand}...")
        
        brand_results = await agent.social_media_manager.get_brand_trends(brand, max_results=10)
        
        print(f"✅ Found {len(brand_results)} {brand} trend items")
        
        # Show sample brand items
        for i, item in enumerate(brand_results[:5], 1):
            source = "📌 Pinterest" if item.site == "pinterest" else "📷 Instagram"
            print(f"  {i}. {item.title[:50]}... {source}")
        
        print()
        
        print("🎉 Demo completed successfully!")
        print("=" * 60)
        print("Key Features Demonstrated:")
        print("✅ Social media integration (Pinterest & Instagram)")
        print("✅ Enhanced search with trend integration")
        print("✅ User feedback system (like/dislike/save)")
        print("✅ Personalized recommendations")
        print("✅ Trending fashion content")
        print("✅ Fashion inspiration search")
        print("✅ Seasonal trend analysis")
        print("✅ Brand trend discovery")
        print("✅ Preference learning and scoring")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    finally:
        # Cleanup
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(demo_social_media_integration())
