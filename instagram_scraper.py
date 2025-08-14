"""
Instagram scraper for fashion trends and style inspiration
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import time
import random

from .base_scraper import BaseScraper
from ..models.clothing_item import ClothingItem


class InstagramScraper(BaseScraper):
    """Scraper for Instagram fashion content"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.base_url = "https://www.instagram.com"
        self.search_url = "https://www.instagram.com/explore/tags/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = None
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def search_hashtags(self, hashtag: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Search for fashion content by hashtag on Instagram
        
        Args:
            hashtag: Hashtag to search for (without #)
            max_results: Maximum number of results to return
            
        Returns:
            List of clothing items from Instagram
        """
        cache_key = f"instagram_{hashtag}_{max_results}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['items']
        
        try:
            # Clean hashtag
            hashtag = hashtag.replace('#', '').strip()
            url = f"{self.search_url}{hashtag}/"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    items = await self._parse_hashtag_page(html, hashtag, max_results)
                    
                    # Cache results
                    self.cache[cache_key] = {
                        'items': items,
                        'timestamp': time.time()
                    }
                    
                    return items
                else:
                    self.log_error(f"Instagram hashtag search failed with status {response.status}")
                    return []
                    
        except Exception as e:
            self.log_error(f"Error searching Instagram hashtag {hashtag}: {e}")
            return []
    
    async def get_trending_fashion(self, max_results: int = 20) -> List[ClothingItem]:
        """
        Get trending fashion content from Instagram
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of trending clothing items
        """
        trending_hashtags = [
            "fashion",
            "style",
            "outfit",
            "fashionblogger",
            "streetstyle",
            "fashionweek",
            "ootd",
            "fashioninspiration",
            "fashiontrends",
            "styleinspiration"
        ]
        
        all_items = []
        
        for hashtag in trending_hashtags[:4]:  # Limit to top 4 hashtags
            try:
                items = await self.search_hashtags(hashtag, max_results // 4)
                all_items.extend(items)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                self.log_error(f"Error getting trending fashion for #{hashtag}: {e}")
        
        # Remove duplicates and limit results
        unique_items = self._remove_duplicates(all_items)
        return unique_items[:max_results]
    
    async def _parse_hashtag_page(self, html: str, hashtag: str, max_results: int) -> List[ClothingItem]:
        """
        Parse Instagram hashtag page HTML
        
        Args:
            html: HTML content
            hashtag: Original hashtag
            max_results: Maximum number of results
            
        Returns:
            List of clothing items
        """
        items = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for Instagram post data in script tags
            script_tags = soup.find_all('script', {'type': 'application/ld+json'})
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    posts = self._extract_posts_from_data(data)
                    
                    for post in posts[:max_results]:
                        item = self._create_clothing_item_from_post(post, hashtag)
                        if item:
                            items.append(item)
                            
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Fallback: try to extract from HTML structure
            if not items:
                items = await self._extract_from_html_structure(soup, hashtag, max_results)
            
        except Exception as e:
            self.log_error(f"Error parsing Instagram hashtag page: {e}")
        
        return items
    
    def _extract_posts_from_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract post data from Instagram JSON response"""
        posts = []
        
        def extract_posts_recursive(obj):
            if isinstance(obj, dict):
                if 'type' in obj and obj.get('type') == 'ImageObject':
                    posts.append(obj)
                elif 'graph' in obj and 'shortcode_media' in obj['graph']:
                    posts.extend(obj['graph']['shortcode_media'])
                else:
                    for value in obj.values():
                        extract_posts_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_posts_recursive(item)
        
        extract_posts_recursive(data)
        return posts
    
    def _create_clothing_item_from_post(self, post: Dict[str, Any], hashtag: str) -> Optional[ClothingItem]:
        """Create a clothing item from Instagram post data"""
        try:
            # Extract basic information
            caption = post.get('caption', '') or post.get('text', '')
            title = caption[:100] if caption else f"Instagram post #{hashtag}"
            
            # Extract image URL
            image_url = None
            if 'image' in post:
                image_url = post['image'].get('url') if isinstance(post['image'], dict) else post['image']
            elif 'display_url' in post:
                image_url = post['display_url']
            
            # Extract price if available
            price = None
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', caption)
            if price_match:
                price = float(price_match.group(1))
            
            # Extract brand if available
            brand = None
            brand_match = re.search(r'@(\w+)', caption)
            if brand_match:
                brand = brand_match.group(1)
            
            # Extract hashtags
            hashtags = re.findall(r'#(\w+)', caption)
            
            # Create clothing item
            item = ClothingItem(
                title=title,
                url=post.get('url', ''),
                site='instagram',
                price=price,
                description=caption,
                image_url=image_url,
                brand=brand,
                tags=hashtags,
                search_query=f"#{hashtag}",
                relevance_score=0.8,  # Instagram items are generally relevant
                raw_data=post
            )
            
            return item
            
        except Exception as e:
            self.log_error(f"Error creating clothing item from Instagram post: {e}")
            return None
    
    async def _extract_from_html_structure(self, soup: BeautifulSoup, hashtag: str, max_results: int) -> List[ClothingItem]:
        """Extract items from HTML structure as fallback"""
        items = []
        
        try:
            # Look for post containers
            post_containers = soup.find_all('article')
            
            for container in post_containers[:max_results]:
                try:
                    # Extract caption
                    caption_elem = container.find('div', {'class': 'caption'})
                    caption = caption_elem.get_text().strip() if caption_elem else ''
                    
                    # Extract image
                    img_elem = container.find('img')
                    image_url = img_elem.get('src') if img_elem else None
                    
                    # Extract link
                    link_elem = container.find('a')
                    url = link_elem.get('href') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = f"{self.base_url}{url}"
                    
                    # Create item
                    item = ClothingItem(
                        title=caption[:100] if caption else f"Instagram post #{hashtag}",
                        url=url,
                        site='instagram',
                        image_url=image_url,
                        description=caption,
                        search_query=f"#{hashtag}",
                        relevance_score=0.7,
                        raw_data={'extracted_from_html': True}
                    )
                    
                    items.append(item)
                    
                except Exception as e:
                    self.log_error(f"Error extracting from HTML structure: {e}")
                    continue
                    
        except Exception as e:
            self.log_error(f"Error in HTML structure extraction: {e}")
        
        return items
    
    def _remove_duplicates(self, items: List[ClothingItem]) -> List[ClothingItem]:
        """Remove duplicate items based on URL"""
        seen_urls = set()
        unique_items = []
        
        for item in items:
            if item.url and item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items
    
    async def get_user_posts(self, username: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Get fashion posts from a specific Instagram user
        
        Args:
            username: Instagram username
            max_results: Maximum number of results
            
        Returns:
            List of clothing items from user's posts
        """
        try:
            url = f"{self.base_url}/{username}/"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return await self._parse_hashtag_page(html, f"user:{username}", max_results)
                else:
                    self.log_error(f"Failed to get user posts for {username}")
                    return []
                    
        except Exception as e:
            self.log_error(f"Error getting user posts for {username}: {e}")
            return []
    
    async def search_fashion_influencers(self, max_results: int = 20) -> List[ClothingItem]:
        """
        Search for fashion influencer content
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of clothing items from fashion influencers
        """
        fashion_influencers = [
            "fashionnova",
            "zara",
            "h&m",
            "nike",
            "adidas",
            "fashionblogger",
            "styleblogger",
            "fashionista"
        ]
        
        all_items = []
        
        for influencer in fashion_influencers[:3]:  # Limit to top 3 influencers
            try:
                items = await self.get_user_posts(influencer, max_results // 3)
                all_items.extend(items)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                self.log_error(f"Error getting influencer posts for {influencer}: {e}")
        
        # Remove duplicates and limit results
        unique_items = self._remove_duplicates(all_items)
        return unique_items[:max_results]
