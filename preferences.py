"""
User preferences model
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


@dataclass
class UserPreferences:
    """Represents user preferences for clothing searches"""
    
    # Size preferences
    preferred_size: Optional[str] = None
    acceptable_sizes: List[str] = field(default_factory=list)
    
    # Color preferences
    preferred_colors: List[str] = field(default_factory=list)
    disliked_colors: List[str] = field(default_factory=list)
    
    # Price preferences
    price_range: Optional[str] = None  # budget, moderate, premium, luxury
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    
    # Brand preferences
    preferred_brands: List[str] = field(default_factory=list)
    disliked_brands: List[str] = field(default_factory=list)
    
    # Category preferences
    preferred_categories: List[str] = field(default_factory=list)
    disliked_categories: List[str] = field(default_factory=list)
    
    # Style preferences
    preferred_styles: List[str] = field(default_factory=list)
    disliked_styles: List[str] = field(default_factory=list)
    
    # Material preferences
    preferred_materials: List[str] = field(default_factory=list)
    disliked_materials: List[str] = field(default_factory=list)
    
    # Shopping preferences
    preferred_sites: List[str] = field(default_factory=list)
    exclude_sites: List[str] = field(default_factory=list)
    
    # Quality preferences
    min_rating: Optional[float] = None
    min_review_count: Optional[int] = None
    
    # Notification preferences
    price_drop_alerts: bool = True
    new_items_alerts: bool = True
    restock_alerts: bool = True
    
    # Search behavior
    include_sale_items: bool = True
    include_out_of_stock: bool = False
    sort_preference: str = "relevance"  # relevance, price_low, price_high, rating, newest
    
    # Seasonal preferences
    seasonal_preferences: Dict[str, List[str]] = field(default_factory=dict)
    
    # Custom keywords
    must_include_keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Normalize string lists to lowercase
        self.preferred_colors = [color.lower() for color in self.preferred_colors]
        self.disliked_colors = [color.lower() for color in self.disliked_colors]
        self.preferred_brands = [brand.lower() for brand in self.preferred_brands]
        self.disliked_brands = [brand.lower() for brand in self.disliked_brands]
        self.preferred_categories = [cat.lower() for cat in self.preferred_categories]
        self.disliked_categories = [cat.lower() for cat in self.disliked_categories]
        
        # Normalize size
        if self.preferred_size:
            self.preferred_size = self.preferred_size.upper()
        
        self.acceptable_sizes = [size.upper() for size in self.acceptable_sizes]
        
        # Add preferred size to acceptable sizes if not present
        if self.preferred_size and self.preferred_size not in self.acceptable_sizes:
            self.acceptable_sizes.insert(0, self.preferred_size)
    
    def add_preferred_color(self, color: str) -> None:
        """Add a preferred color"""
        color = color.lower()
        if color not in self.preferred_colors:
            self.preferred_colors.append(color)
            self.updated_at = datetime.now()
        
        # Remove from disliked if present
        if color in self.disliked_colors:
            self.disliked_colors.remove(color)
    
    def add_disliked_color(self, color: str) -> None:
        """Add a disliked color"""
        color = color.lower()
        if color not in self.disliked_colors:
            self.disliked_colors.append(color)
            self.updated_at = datetime.now()
        
        # Remove from preferred if present
        if color in self.preferred_colors:
            self.preferred_colors.remove(color)
    
    def add_preferred_brand(self, brand: str) -> None:
        """Add a preferred brand"""
        brand = brand.lower()
        if brand not in self.preferred_brands:
            self.preferred_brands.append(brand)
            self.updated_at = datetime.now()
        
        # Remove from disliked if present
        if brand in self.disliked_brands:
            self.disliked_brands.remove(brand)
    
    def add_disliked_brand(self, brand: str) -> None:
        """Add a disliked brand"""
        brand = brand.lower()
        if brand not in self.disliked_brands:
            self.disliked_brands.append(brand)
            self.updated_at = datetime.now()
        
        # Remove from preferred if present
        if brand in self.preferred_brands:
            self.preferred_brands.remove(brand)
    
    def set_price_range(self, min_price: Optional[float] = None, max_price: Optional[float] = None) -> None:
        """Set custom price range"""
        if min_price is not None:
            self.min_price = min_price
        if max_price is not None:
            self.max_price = max_price
        self.updated_at = datetime.now()
    
    def get_price_range(self, price_ranges: Dict[str, List[int]]) -> tuple[Optional[float], Optional[float]]:
        """Get effective price range"""
        # Custom range takes precedence
        if self.min_price is not None or self.max_price is not None:
            return (self.min_price, self.max_price)
        
        # Use predefined range
        if self.price_range and self.price_range in price_ranges:
            min_p, max_p = price_ranges[self.price_range]
            return (float(min_p), float(max_p))
        
        return (None, None)
    
    def matches_color(self, color: str) -> bool:
        """Check if a color matches preferences"""
        if not color:
            return True
        
        color = color.lower()
        
        # Check disliked colors first
        if any(disliked in color for disliked in self.disliked_colors):
            return False
        
        # Check preferred colors
        if self.preferred_colors:
            return any(preferred in color for preferred in self.preferred_colors)
        
        return True
    
    def matches_brand(self, brand: str) -> bool:
        """Check if a brand matches preferences"""
        if not brand:
            return True
        
        brand = brand.lower()
        
        # Check disliked brands first
        if any(disliked in brand for disliked in self.disliked_brands):
            return False
        
        # Check preferred brands
        if self.preferred_brands:
            return any(preferred in brand for preferred in self.preferred_brands)
        
        return True
    
    def matches_category(self, category: str) -> bool:
        """Check if a category matches preferences"""
        if not category:
            return True
        
        category = category.lower()
        
        # Check disliked categories first
        if any(disliked in category for disliked in self.disliked_categories):
            return False
        
        # Check preferred categories
        if self.preferred_categories:
            return any(preferred in category for preferred in self.preferred_categories)
        
        return True
    
    def matches_size(self, size: str) -> bool:
        """Check if a size matches preferences"""
        if not size:
            return True
        
        size = size.upper()
        
        # Check preferred size first
        if self.preferred_size and size == self.preferred_size:
            return True
        
        # Check acceptable sizes
        if self.acceptable_sizes:
            return size in self.acceptable_sizes
        
        # If no size preferences set, accept all
        return not self.preferred_size
    
    def get_seasonal_preferences(self, season: str) -> List[str]:
        """Get preferences for a specific season"""
        return self.seasonal_preferences.get(season.lower(), [])
    
    def set_seasonal_preferences(self, season: str, preferences: List[str]) -> None:
        """Set preferences for a specific season"""
        self.seasonal_preferences[season.lower()] = preferences
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'preferred_size': self.preferred_size,
            'acceptable_sizes': self.acceptable_sizes,
            'preferred_colors': self.preferred_colors,
            'disliked_colors': self.disliked_colors,
            'price_range': self.price_range,
            'max_price': self.max_price,
            'min_price': self.min_price,
            'preferred_brands': self.preferred_brands,
            'disliked_brands': self.disliked_brands,
            'preferred_categories': self.preferred_categories,
            'disliked_categories': self.disliked_categories,
            'preferred_styles': self.preferred_styles,
            'disliked_styles': self.disliked_styles,
            'preferred_materials': self.preferred_materials,
            'disliked_materials': self.disliked_materials,
            'preferred_sites': self.preferred_sites,
            'exclude_sites': self.exclude_sites,
            'min_rating': self.min_rating,
            'min_review_count': self.min_review_count,
            'price_drop_alerts': self.price_drop_alerts,
            'new_items_alerts': self.new_items_alerts,
            'restock_alerts': self.restock_alerts,
            'include_sale_items': self.include_sale_items,
            'include_out_of_stock': self.include_out_of_stock,
            'sort_preference': self.sort_preference,
            'seasonal_preferences': self.seasonal_preferences,
            'must_include_keywords': self.must_include_keywords,
            'exclude_keywords': self.exclude_keywords,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create UserPreferences from dictionary"""
        # Handle datetime fields
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UserPreferences':
        """Create UserPreferences from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def merge_with(self, other: 'UserPreferences') -> 'UserPreferences':
        """Merge with another preferences object"""
        # Create a new preferences object with combined data
        merged_data = self.to_dict()
        other_data = other.to_dict()
        
        # Merge lists
        list_fields = [
            'acceptable_sizes', 'preferred_colors', 'disliked_colors',
            'preferred_brands', 'disliked_brands', 'preferred_categories',
            'disliked_categories', 'preferred_styles', 'disliked_styles',
            'preferred_materials', 'disliked_materials', 'preferred_sites',
            'exclude_sites', 'must_include_keywords', 'exclude_keywords'
        ]
        
        for field in list_fields:
            merged_data[field] = list(set(merged_data[field] + other_data[field]))
        
        # Override single values with other's values if they exist
        single_fields = [
            'preferred_size', 'price_range', 'max_price', 'min_price',
            'min_rating', 'min_review_count', 'sort_preference'
        ]
        
        for field in single_fields:
            if other_data[field] is not None:
                merged_data[field] = other_data[field]
        
        # Override boolean values
        bool_fields = [
            'price_drop_alerts', 'new_items_alerts', 'restock_alerts',
            'include_sale_items', 'include_out_of_stock'
        ]
        
        for field in bool_fields:
            merged_data[field] = other_data[field]
        
        # Merge seasonal preferences
        for season, prefs in other_data['seasonal_preferences'].items():
            if season in merged_data['seasonal_preferences']:
                merged_data['seasonal_preferences'][season] = list(
                    set(merged_data['seasonal_preferences'][season] + prefs)
                )
            else:
                merged_data['seasonal_preferences'][season] = prefs
        
        merged_data['updated_at'] = datetime.now().isoformat()
        
        return cls.from_dict(merged_data)
    
    def __str__(self) -> str:
        """String representation"""
        parts = []
        if self.preferred_size:
            parts.append(f"Size: {self.preferred_size}")
        if self.preferred_colors:
            parts.append(f"Colors: {', '.join(self.preferred_colors[:3])}")
        if self.price_range:
            parts.append(f"Price: {self.price_range}")
        
        return f"UserPreferences({', '.join(parts)})"
