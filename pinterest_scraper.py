"""
Pinterest scraper for fashion trends and style inspiration
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


class PinterestScraper(BaseScraper):
    """Scraper for Pinterest fashion content"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.base_url = "https://www.pinterest.com"
        self.search_url = "https://www.pinterest.com/search/pins/"
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
    
    async def search_trends(self, query: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Search for trending fashion content on Pinterest
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of clothing items from Pinterest
        """
        cache_key = f"pinterest_{query}_{max_results}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                return cached_data['items']
        
        try:
            # Construct search URL
            search_params = {
                'q': query,
                'rs': 'typed',
                'term_meta[]': query
            }
            
            url = f"{self.search_url}?{'&'.join([f'{k}={v}' for k, v in search_params.items()])}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    items = await self._parse_search_results(html, query, max_results)
                    
                    # Cache results
                    self.cache[cache_key] = {
                        'items': items,
                        'timestamp': time.time()
                    }
                    
                    return items
                else:
                    self.log_error(f"Pinterest search failed with status {response.status}")
                    return []
                    
        except Exception as e:
            self.log_error(f"Error searching Pinterest: {e}")
            return []
    
    async def get_trending_fashion(self, max_results: int = 20) -> List[ClothingItem]:
        """
        Get trending fashion content from Pinterest
        
        Args:
            max_results: Maximum number of results to return
            
        Returns:
            List of trending clothing items
        """
        trending_queries = [
            "fashion trends 2024",
            "street style",
            "outfit inspiration",
            "fashion week",
            "style trends",
            "fashion blogger",
            "outfit of the day",
            "fashion inspiration"
        ]
        
        all_items = []
        
        for query in trending_queries[:3]:  # Limit to top 3 queries
            try:
                items = await self.search_trends(query, max_results // 3)
                all_items.extend(items)
                
                # Rate limiting
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                self.log_error(f"Error getting trending fashion for {query}: {e}")
        
        # Remove duplicates and limit results
        unique_items = self._remove_duplicates(all_items)
        return unique_items[:max_results]
    
    async def _parse_search_results(self, html: str, query: str, max_results: int) -> List[ClothingItem]:
        """
        Parse Pinterest search results HTML
        
        Args:
            html: HTML content
            query: Original search query
            max_results: Maximum number of results
            
        Returns:
            List of clothing items
        """
        items = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for Pinterest pin data
            script_tags = soup.find_all('script', {'type': 'application/json'})
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    pins = self._extract_pins_from_data(data)
                    
                    for pin in pins[:max_results]:
                        item = self._create_clothing_item_from_pin(pin, query)
                        if item:
                            items.append(item)
                            
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Fallback: try to extract from HTML structure
            if not items:
                items = await self._extract_from_html_structure(soup, query, max_results)
            
        except Exception as e:
            self.log_error(f"Error parsing Pinterest results: {e}")
        
        return items
    
    def _extract_pins_from_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract pin data from Pinterest JSON response"""
        pins = []
        
        def extract_pins_recursive(obj):
            if isinstance(obj, dict):
                if 'type' in obj and obj.get('type') == 'pin':
                    pins.append(obj)
                elif 'pins' in obj:
                    pins.extend(obj['pins'])
                else:
                    for value in obj.values():
                        extract_pins_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_pins_recursive(item)
        
        extract_pins_recursive(data)
        return pins
    
    def _create_clothing_item_from_pin(self, pin: Dict[str, Any], query: str) -> Optional[ClothingItem]:
        """Create a clothing item from Pinterest pin data"""
        try:
            # Extract basic information
            title = pin.get('title', '') or pin.get('description', '')[:100]
            description = pin.get('description', '')
            image_url = pin.get('images', {}).get('orig', {}).get('url')
            
            # Extract price if available
            price = None
            price_match = re.search(r'\$(\d+(?:\.\d{2})?)', description)
            if price_match:
                price = float(price_match.group(1))
            
            # Extract brand if available
            brand = None
            brand_match = re.search(r'#(\w+)', description)
            if brand_match:
                brand = brand_match.group(1)
            
            # Create clothing item
            item = ClothingItem(
                title=title,
                url=pin.get('link', ''),
                site='pinterest',
                price=price,
                description=description,
                image_url=image_url,
                brand=brand,
                tags=pin.get('hashtags', []),
                search_query=query,
                relevance_score=0.8,  # Pinterest items are generally relevant
                raw_data=pin
            )
            
            return item
            
        except Exception as e:
            self.log_error(f"Error creating clothing item from pin: {e}")
            return None
    
    async def _extract_from_html_structure(self, soup: BeautifulSoup, query: str, max_results: int) -> List[ClothingItem]:
        """Extract items from HTML structure as fallback"""
        items = []
        
        try:
            # Look for pin containers
            pin_containers = soup.find_all('div', {'data-test-id': 'pin'})
            
            for container in pin_containers[:max_results]:
                try:
                    # Extract title/description
                    title_elem = container.find('div', {'data-test-id': 'pinTitle'})
                    title = title_elem.get_text().strip() if title_elem else ''
                    
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
                        title=title,
                        url=url,
                        site='pinterest',
                        image_url=image_url,
                        search_query=query,
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
    
    async def get_user_feed(self, username: str, max_results: int = 20) -> List[ClothingItem]:
        """
        Get fashion content from a specific Pinterest user
        
        Args:
            username: Pinterest username
            max_results: Maximum number of results
            
        Returns:
            List of clothing items from user's feed
        """
        try:
            url = f"{self.base_url}/{username}/"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return await self._parse_search_results(html, f"user:{username}", max_results)
                else:
                    self.log_error(f"Failed to get user feed for {username}")
                    return []
                    
        except Exception as e:
            self.log_error(f"Error getting user feed for {username}: {e}")
            return []
