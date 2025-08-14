"""
Social Media Trends Manager for integrating Pinterest and Instagram fashion content
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import random

from .pinterest_scraper import PinterestScraper
from .instagram_scraper import InstagramScraper
from ..models.clothing_item import ClothingItem
from ..services.feedback_manager import FeedbackManager


class SocialMediaManager:
    """Manages social media trend integration and content aggregation"""
    
    def __init__(self, settings, feedback_manager: Optional[FeedbackManager] = None):
        """Initialize the social media manager"""
        self.settings = settings
        self.feedback_manager = feedback_manager or FeedbackManager()
        
        # Initialize scrapers
        self.pinterest_scraper = PinterestScraper(settings)
        self.instagram_scraper = InstagramScraper(settings)
        
        # Cache for trending content
        self.trending_cache = {}
        self.cache_duration = 1800  # 30 minutes
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds
    
    async def get_trending_fashion(self, max_results: int = 30) -> List[ClothingItem]:
        """
        Get trending fashion content from all social media sources
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of trending clothing items
        """
        cache_key = f"trending_{max_results}"
        
        # Check cache first
        if cache_key in self.trending_cache:
            cached_data = self.trending_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['items']
        
        try:
            all_items = []
            
            # Get Pinterest trending content
            try:
                pinterest_items = await self.pinterest_scraper.get_trending_fashion(max_results // 2)
                all_items.extend(pinterest_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error getting Pinterest trending content: {e}")
            
            # Get Instagram trending content
            try:
                instagram_items = await self.instagram_scraper.get_trending_fashion(max_results // 2)
                all_items.extend(instagram_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error getting Instagram trending content: {e}")
            
            # Remove duplicates and limit results
            unique_items = self._remove_duplicates(all_items)
            final_items = unique_items[:max_results]
            
            # Cache results
            self.trending_cache[cache_key] = {
                'items': final_items,
                'timestamp': time.time()
            }
            
            return final_items
            
        except Exception as e:
            print(f"Error getting trending fashion: {e}")
            return []
    
    async def search_social_media(self, query: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Search for fashion content across social media platforms
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of clothing items from social media
        """
        try:
            all_items = []
            
            # Search Pinterest
            try:
                pinterest_items = await self.pinterest_scraper.search_trends(query, max_results // 2)
                all_items.extend(pinterest_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error searching Pinterest: {e}")
            
            # Search Instagram hashtags
            try:
                # Extract hashtags from query
                hashtags = self._extract_hashtags(query)
                if hashtags:
                    for hashtag in hashtags[:2]:  # Limit to 2 hashtags
                        instagram_items = await self.instagram_scraper.search_hashtags(
                            hashtag, max_results // 4
                        )
                        all_items.extend(instagram_items)
                        await self._rate_limit()
                else:
                    # Fallback to general fashion hashtags
                    instagram_items = await self.instagram_scraper.search_hashtags(
                        "fashion", max_results // 2
                    )
                    all_items.extend(instagram_items)
                    await self._rate_limit()
            except Exception as e:
                print(f"Error searching Instagram: {e}")
            
            # Remove duplicates and limit results
            unique_items = self._remove_duplicates(all_items)
            return unique_items[:max_results]
            
        except Exception as e:
            print(f"Error searching social media: {e}")
            return []
    
    async def get_personalized_trends(self, user_session_id: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Get personalized trending content based on user preferences
        
        Args:
            user_session_id: User session ID
            max_results: Maximum number of results
            
        Returns:
            List of personalized trending items
        """
        try:
            # Get user preferences
            user_preferences = self.feedback_manager.get_user_preferences(user_session_id)
            
            # Get trending content
            trending_items = await self.get_trending_fashion(max_results * 2)
            
            if not trending_items:
                return []
            
            # Calculate personalized scores
            for item in trending_items:
                item.preference_score = self.feedback_manager.calculate_item_score(
                    item, user_session_id
                )
            
            # Sort by personalized score
            personalized_items = sorted(
                trending_items, 
                key=lambda x: x.preference_score or 0, 
                reverse=True
            )
            
            return personalized_items[:max_results]
            
        except Exception as e:
            print(f"Error getting personalized trends: {e}")
            return []
    
    async def get_fashion_inspiration(self, style_keywords: List[str], max_results: int = 15) -> List[ClothingItem]:
        """
        Get fashion inspiration based on style keywords
        
        Args:
            style_keywords: List of style-related keywords
            max_results: Maximum number of results
            
        Returns:
            List of inspirational clothing items
        """
        try:
            all_items = []
            
            for keyword in style_keywords[:3]:  # Limit to 3 keywords
                # Search Pinterest for inspiration
                try:
                    pinterest_items = await self.pinterest_scraper.search_trends(
                        f"fashion inspiration {keyword}", max_results // 3
                    )
                    all_items.extend(pinterest_items)
                    await self._rate_limit()
                except Exception as e:
                    print(f"Error getting Pinterest inspiration for {keyword}: {e}")
                
                # Search Instagram for inspiration
                try:
                    instagram_items = await self.instagram_scraper.search_hashtags(
                        keyword, max_results // 3
                    )
                    all_items.extend(instagram_items)
                    await self._rate_limit()
                except Exception as e:
                    print(f"Error getting Instagram inspiration for {keyword}: {e}")
            
            # Remove duplicates and limit results
            unique_items = self._remove_duplicates(all_items)
            return unique_items[:max_results]
            
        except Exception as e:
            print(f"Error getting fashion inspiration: {e}")
            return []
    
    async def get_seasonal_trends(self, season: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Get seasonal fashion trends
        
        Args:
            season: Season (spring, summer, fall, winter)
            max_results: Maximum number of results
            
        Returns:
            List of seasonal trending items
        """
        try:
            all_items = []
            
            # Search Pinterest for seasonal trends
            try:
                pinterest_items = await self.pinterest_scraper.search_trends(
                    f"{season} fashion trends 2024", max_results // 2
                )
                all_items.extend(pinterest_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error getting Pinterest seasonal trends: {e}")
            
            # Search Instagram for seasonal trends
            try:
                instagram_items = await self.instagram_scraper.search_hashtags(
                    f"{season}fashion", max_results // 2
                )
                all_items.extend(instagram_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error getting Instagram seasonal trends: {e}")
            
            # Remove duplicates and limit results
            unique_items = self._remove_duplicates(all_items)
            return unique_items[:max_results]
            
        except Exception as e:
            print(f"Error getting seasonal trends: {e}")
            return []
    
    async def get_brand_trends(self, brand: str, max_results: int = 15) -> List[ClothingItem]:
        """
        Get trending content for a specific brand
        
        Args:
            brand: Brand name
            max_results: Maximum number of results
            
        Returns:
            List of brand-related items
        """
        try:
            all_items = []
            
            # Search Pinterest for brand content
            try:
                pinterest_items = await self.pinterest_scraper.search_trends(
                    f"{brand} fashion", max_results // 2
                )
                all_items.extend(pinterest_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error getting Pinterest brand trends for {brand}: {e}")
            
            # Search Instagram for brand content
            try:
                instagram_items = await self.instagram_scraper.search_hashtags(
                    brand.lower(), max_results // 2
                )
                all_items.extend(instagram_items)
                await self._rate_limit()
            except Exception as e:
                print(f"Error getting Instagram brand trends for {brand}: {e}")
            
            # Remove duplicates and limit results
            unique_items = self._remove_duplicates(all_items)
            return unique_items[:max_results]
            
        except Exception as e:
            print(f"Error getting brand trends: {e}")
            return []
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def _remove_duplicates(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Remove duplicate items based on URL"""
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url and item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items
    
    async def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    async def close(self):
        """Close scrapers and clean up resources"""
        try:
            if hasattr(self.pinterest_scraper, 'session') and self.pinterest_scraper.session:
                await self.pinterest_scraper.session.close()
            
            if hasattr(self.instagram_scraper, 'session') and self.instagram_scraper.session:
                await self.instagram_scraper.session.close()
        except Exception as e:
            print(f"Error closing social media manager: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
