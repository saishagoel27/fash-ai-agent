"""
Data model for clothing items
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


@dataclass
class ClothingItem:
    """Represents a clothing item found during search"""
    
    # Basic information
    title: str
    url: str
    site: str
    price: Optional[float] = None
    original_price: Optional[float] = None
    currency: str = "USD"
    
    # Product details
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    
    # Images
    image_url: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    
    # Availability and shipping
    in_stock: bool = True
    shipping_info: Optional[str] = None
    shipping_cost: Optional[float] = None
    
    # Ratings and reviews
    rating: Optional[float] = None
    review_count: Optional[int] = None
    
    # Additional metadata
    product_id: Optional[str] = None
    sku: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    # Search and filtering metadata
    search_query: Optional[str] = None
    relevance_score: Optional[float] = None
    preference_score: Optional[float] = None
    
    # Timestamps
    found_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Additional data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure price is numeric
        if self.price is not None:
            try:
                self.price = float(self.price)
            except (ValueError, TypeError):
                self.price = None
        
        if self.original_price is not None:
            try:
                self.original_price = float(self.original_price)
            except (ValueError, TypeError):
                self.original_price = None
        
        # Clean up title
        if self.title:
            self.title = self.title.strip()
        
        # Ensure image_urls includes image_url if present
        if self.image_url and self.image_url not in self.image_urls:
            self.image_urls.insert(0, self.image_url)
    
    @property
    def discount_percentage(self) -> Optional[float]:
        """Calculate discount percentage if original price is available"""
        if self.original_price and self.price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 1)
        return None
    
    @property
    def savings_amount(self) -> Optional[float]:
        """Calculate savings amount if original price is available"""
        if self.original_price and self.price and self.original_price > self.price:
            return round(self.original_price - self.price, 2)
        return None
    
    @property
    def is_on_sale(self) -> bool:
        """Check if item is on sale"""
        return self.discount_percentage is not None and self.discount_percentage > 0
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price string"""
        if self.price is None:
            return "Price unavailable"
        
        symbol = "$" if self.currency == "USD" else self.currency
        return f"{symbol}{self.price:.2f}"
    
    @property
    def short_description(self) -> str:
        """Get a short description of the item"""
        parts = []
        
        if self.brand:
            parts.append(self.brand)
        
        if self.color:
            parts.append(self.color)
        
        if self.size:
            parts.append(f"Size {self.size}")
        
        base = self.title
        if parts:
            base += f" ({', '.join(parts)})"
        
        return base
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the item"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if item has a specific tag"""
        return tag in self.tags
    
    def update_price(self, new_price: float) -> None:
        """Update the price and timestamp"""
        if self.price != new_price:
            self.price = new_price
            self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = {
            'title': self.title,
            'url': self.url,
            'site': self.site,
            'price': self.price,
            'original_price': self.original_price,
            'currency': self.currency,
            'brand': self.brand,
            'size': self.size,
            'color': self.color,
            'category': self.category,
            'description': self.description,
            'image_url': self.image_url,
            'image_urls': self.image_urls,
            'in_stock': self.in_stock,
            'shipping_info': self.shipping_info,
            'shipping_cost': self.shipping_cost,
            'rating': self.rating,
            'review_count': self.review_count,
            'product_id': self.product_id,
            'sku': self.sku,
            'tags': self.tags,
            'search_query': self.search_query,
            'relevance_score': self.relevance_score,
            'preference_score': self.preference_score,
            'found_at': self.found_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'raw_data': self.raw_data
        }
        
        # Add computed properties
        data['discount_percentage'] = self.discount_percentage
        data['savings_amount'] = self.savings_amount
        data['is_on_sale'] = self.is_on_sale
        data['formatted_price'] = self.formatted_price
        data['short_description'] = self.short_description
        
        return data
    
    def dict(self) -> Dict[str, Any]:
        """Alias for to_dict() for compatibility"""
        return self.to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClothingItem':
        """Create ClothingItem from dictionary"""
        # Handle datetime fields
        if 'found_at' in data and isinstance(data['found_at'], str):
            data['found_at'] = datetime.fromisoformat(data['found_at'])
        
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        # Remove computed properties if present
        computed_props = ['discount_percentage', 'savings_amount', 'is_on_sale', 
                         'formatted_price', 'short_description']
        for prop in computed_props:
            data.pop(prop, None)
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ClothingItem':
        """Create ClothingItem from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation"""
        return f"ClothingItem(title='{self.title}', price={self.formatted_price}, site='{self.site}')"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return (f"ClothingItem(title='{self.title}', url='{self.url}', "
                f"price={self.price}, site='{self.site}')")
    
    def __eq__(self, other) -> bool:
        """Check equality based on URL"""
        if not isinstance(other, ClothingItem):
            return False
        return self.url == other.url
    
    def __hash__(self) -> int:
        """Hash based on URL"""
        return hash(self.url)


# Type alias for lists of clothing items
ClothingItemList = List[ClothingItem]
