"""
User feedback system for personalized recommendations
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

from ..models.clothing_item import ClothingItem


@dataclass
class UserFeedback:
    """Represents user feedback on a clothing item"""
    
    # Item identification
    item_id: str
    item_url: str
    item_title: str
    
    # Feedback data
    feedback_type: str  # 'like', 'dislike', 'save', 'view'
    feedback_value: float = 1.0  # 1.0 for positive, -1.0 for negative, 0.5 for neutral
    
    # User context
    search_query: Optional[str] = None
    user_session_id: Optional[str] = None
    
    # Metadata
    timestamp: datetime = None
    source_site: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class FeedbackManager:
    """Manages user feedback and preference learning"""
    
    def __init__(self, db_path: str = "user_feedback.db"):
        """Initialize the feedback manager"""
        self.db_path = db_path
        self.db_path_obj = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the feedback database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create feedback table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_id TEXT NOT NULL,
                        item_url TEXT NOT NULL,
                        item_title TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        feedback_value REAL NOT NULL,
                        search_query TEXT,
                        user_session_id TEXT,
                        timestamp DATETIME NOT NULL,
                        source_site TEXT,
                        category TEXT,
                        brand TEXT,
                        price REAL,
                        UNIQUE(item_id, feedback_type, user_session_id)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_id ON user_feedback(item_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback(feedback_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON user_feedback(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_session ON user_feedback(user_session_id)')
                
                # Create user preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_session_id TEXT NOT NULL,
                        preference_type TEXT NOT NULL,
                        preference_value TEXT NOT NULL,
                        weight REAL DEFAULT 1.0,
                        timestamp DATETIME NOT NULL,
                        UNIQUE(user_session_id, preference_type, preference_value)
                    )
                ''')
                
                # Create indexes for preferences
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_pref_user ON user_preferences(user_session_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_pref_type ON user_preferences(preference_type)')
                
                conn.commit()
                
        except Exception as e:
            print(f"Error initializing feedback database: {e}")
    
    def add_feedback(self, feedback: UserFeedback) -> bool:
        """
        Add user feedback to the database
        
        Args:
            feedback: UserFeedback object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_feedback 
                    (item_id, item_url, item_title, feedback_type, feedback_value, 
                     search_query, user_session_id, timestamp, source_site, 
                     category, brand, price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    feedback.item_id,
                    feedback.item_url,
                    feedback.item_title,
                    feedback.feedback_type,
                    feedback.feedback_value,
                    feedback.search_query,
                    feedback.user_session_id,
                    feedback.timestamp.isoformat(),
                    feedback.source_site,
                    feedback.category,
                    feedback.brand,
                    feedback.price
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error adding feedback: {e}")
            return False
    
    def get_feedback_for_item(self, item_id: str, user_session_id: Optional[str] = None) -> List[UserFeedback]:
        """
        Get feedback for a specific item
        
        Args:
            item_id: Item identifier
            user_session_id: Optional user session ID to filter by
            
        Returns:
            List of feedback entries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if user_session_id:
                    cursor.execute('''
                        SELECT * FROM user_feedback 
                        WHERE item_id = ? AND user_session_id = ?
                        ORDER BY timestamp DESC
                    ''', (item_id, user_session_id))
                else:
                    cursor.execute('''
                        SELECT * FROM user_feedback 
                        WHERE item_id = ?
                        ORDER BY timestamp DESC
                    ''', (item_id,))
                
                rows = cursor.fetchall()
                return [self._row_to_feedback(row) for row in rows]
                
        except Exception as e:
            print(f"Error getting feedback for item: {e}")
            return []
    
    def get_user_preferences(self, user_session_id: str, days_back: int = 30) -> Dict[str, Dict[str, float]]:
        """
        Get user preferences based on feedback history
        
        Args:
            user_session_id: User session ID
            days_back: Number of days to look back for feedback
            
        Returns:
            Dictionary of preference categories and their weights
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get feedback within the time period
                cursor.execute('''
                    SELECT source_site, category, brand, feedback_type, feedback_value
                    FROM user_feedback 
                    WHERE user_session_id = ? AND timestamp >= ?
                ''', (user_session_id, cutoff_date.isoformat()))
                
                rows = cursor.fetchall()
                
                preferences = {
                    'sites': {},
                    'categories': {},
                    'brands': {},
                    'feedback_patterns': {}
                }
                
                for row in rows:
                    site, category, brand, feedback_type, feedback_value = row
                    
                    # Aggregate site preferences
                    if site:
                        if site not in preferences['sites']:
                            preferences['sites'][site] = 0
                        preferences['sites'][site] += feedback_value
                    
                    # Aggregate category preferences
                    if category:
                        if category not in preferences['categories']:
                            preferences['categories'][category] = 0
                        preferences['categories'][category] += feedback_value
                    
                    # Aggregate brand preferences
                    if brand:
                        if brand not in preferences['brands']:
                            preferences['brands'][brand] = 0
                        preferences['brands'][brand] += feedback_value
                    
                    # Aggregate feedback patterns
                    if feedback_type not in preferences['feedback_patterns']:
                        preferences['feedback_patterns'][feedback_type] = 0
                    preferences['feedback_patterns'][feedback_type] += 1
                
                return preferences
                
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            return {}
    
    def calculate_item_score(self, item: ClothingItem, user_session_id: Optional[str] = None) -> float:
        """
        Calculate a personalized score for an item based on user preferences
        
        Args:
            item: ClothingItem to score
            user_session_id: Optional user session ID
            
        Returns:
            Personalized score (higher is better)
        """
        if not user_session_id:
            return item.relevance_score or 0.5
        
        try:
            preferences = self.get_user_preferences(user_session_id)
            score = item.relevance_score or 0.5
            
            # Boost score based on site preference
            if item.site and item.site in preferences['sites']:
                site_score = preferences['sites'][item.site]
                if site_score > 0:
                    score += min(site_score * 0.1, 0.3)  # Max 0.3 boost
            
            # Boost score based on category preference
            if item.category and item.category in preferences['categories']:
                cat_score = preferences['categories'][item.category]
                if cat_score > 0:
                    score += min(cat_score * 0.1, 0.3)  # Max 0.3 boost
            
            # Boost score based on brand preference
            if item.brand and item.brand in preferences['brands']:
                brand_score = preferences['brands'][item.brand]
                if brand_score > 0:
                    score += min(brand_score * 0.1, 0.2)  # Max 0.2 boost
            
            # Penalize based on negative preferences
            if item.site and item.site in preferences['sites']:
                site_score = preferences['sites'][item.site]
                if site_score < 0:
                    score -= min(abs(site_score) * 0.1, 0.2)  # Max 0.2 penalty
            
            if item.category and item.category in preferences['categories']:
                cat_score = preferences['categories'][item.category]
                if cat_score < 0:
                    score -= min(abs(cat_score) * 0.1, 0.2)  # Max 0.2 penalty
            
            return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            
        except Exception as e:
            print(f"Error calculating item score: {e}")
            return item.relevance_score or 0.5
    
    def rank_items_by_preference(self, items: List[ClothingItem], user_session_id: Optional[str] = None) -> List[ClothingItem]:
        """
        Rank items by user preference score
        
        Args:
            items: List of clothing items
            user_session_id: Optional user session ID
            
        Returns:
            Ranked list of items
        """
        if not user_session_id:
            return sorted(items, key=lambda x: x.relevance_score or 0, reverse=True)
        
        # Calculate personalized scores
        for item in items:
            item.preference_score = self.calculate_item_score(item, user_session_id)
        
        # Sort by preference score
        return sorted(items, key=lambda x: x.preference_score or 0, reverse=True)
    
    def get_trending_items(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Get trending items based on recent feedback
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of trending items with their popularity scores
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT item_id, item_title, item_url, source_site, 
                           COUNT(*) as feedback_count,
                           AVG(feedback_value) as avg_feedback
                    FROM user_feedback 
                    WHERE timestamp >= ? AND feedback_type IN ('like', 'save')
                    GROUP BY item_id
                    ORDER BY feedback_count DESC, avg_feedback DESC
                    LIMIT 20
                ''', (cutoff_date.isoformat(),))
                
                rows = cursor.fetchall()
                
                trending_items = []
                for row in rows:
                    item_id, title, url, site, count, avg_feedback = row
                    trending_items.append({
                        'item_id': item_id,
                        'title': title,
                        'url': url,
                        'site': site,
                        'feedback_count': count,
                        'avg_feedback': avg_feedback,
                        'trending_score': count * avg_feedback
                    })
                
                return trending_items
                
        except Exception as e:
            print(f"Error getting trending items: {e}")
            return []
    
    def _row_to_feedback(self, row: Tuple) -> UserFeedback:
        """Convert database row to UserFeedback object"""
        return UserFeedback(
            item_id=row[1],
            item_url=row[2],
            item_title=row[3],
            feedback_type=row[4],
            feedback_value=row[5],
            search_query=row[6],
            user_session_id=row[7],
            timestamp=datetime.fromisoformat(row[8]),
            source_site=row[9],
            category=row[10],
            brand=row[11],
            price=row[12]
        )
    
    def generate_item_id(self, item: ClothingItem) -> str:
        """Generate a unique ID for an item"""
        # Use URL hash as base ID
        url_hash = hashlib.md5(item.url.encode()).hexdigest()[:8]
        return f"{item.site}_{url_hash}"
    
    def record_view(self, item: ClothingItem, user_session_id: Optional[str] = None, search_query: Optional[str] = None):
        """Record that a user viewed an item"""
        feedback = UserFeedback(
            item_id=self.generate_item_id(item),
            item_url=item.url,
            item_title=item.title,
            feedback_type='view',
            feedback_value=0.1,  # Low weight for views
            search_query=search_query,
            user_session_id=user_session_id,
            source_site=item.site,
            category=item.category,
            brand=item.brand,
            price=item.price
        )
        self.add_feedback(feedback)
    
    def record_like(self, item: ClothingItem, user_session_id: Optional[str] = None, search_query: Optional[str] = None):
        """Record that a user liked an item"""
        feedback = UserFeedback(
            item_id=self.generate_item_id(item),
            item_url=item.url,
            item_title=item.title,
            feedback_type='like',
            feedback_value=1.0,
            search_query=search_query,
            user_session_id=user_session_id,
            source_site=item.site,
            category=item.category,
            brand=item.brand,
            price=item.price
        )
        self.add_feedback(feedback)
    
    def record_dislike(self, item: ClothingItem, user_session_id: Optional[str] = None, search_query: Optional[str] = None):
        """Record that a user disliked an item"""
        feedback = UserFeedback(
            item_id=self.generate_item_id(item),
            item_url=item.url,
            item_title=item.title,
            feedback_type='dislike',
            feedback_value=-1.0,
            search_query=search_query,
            user_session_id=user_session_id,
            source_site=item.site,
            category=item.category,
            brand=item.brand,
            price=item.price
        )
        self.add_feedback(feedback)
    
    def record_save(self, item: ClothingItem, user_session_id: Optional[str] = None, search_query: Optional[str] = None):
        """Record that a user saved an item"""
        feedback = UserFeedback(
            item_id=self.generate_item_id(item),
            item_url=item.url,
            item_title=item.title,
            feedback_type='save',
            feedback_value=1.5,  # Higher weight for saves
            search_query=search_query,
            user_session_id=user_session_id,
            source_site=item.site,
            category=item.category,
            brand=item.brand,
            price=item.price
        )
        self.add_feedback(feedback)
