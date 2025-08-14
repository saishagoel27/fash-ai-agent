from typing import List, Dict, Any
from app.models import ClothingItem, UserPreferences, FilterSettings
from app.utils.logger import logger

class FilterAgent:
    def __init__(self, settings: FilterSettings):
        self.settings = settings

    def filter_items(self, items: List[ClothingItem], preferences: UserPreferences) -> List[ClothingItem]:
        """
        Filters clothing items based on user preferences and active filters.
        """
        logger.info("Starting filtering process for %d items", len(items))
        
        filtered_items = [
            item for item in items
            if self._matches_all_criteria(item, preferences)
        ]
        
        logger.info("Filtering complete. %d items match preferences.", len(filtered_items))
        return filtered_items

    def rank_items(self, items: List[ClothingItem], preferences: UserPreferences) -> List[Dict[str, Any]]:
        """
        Ranks items based on how well they match user preferences.
        """
        logger.info("Starting ranking process for %d items", len(items))
        
        ranked_items = [
            {"item": item, "score": round(self._calculate_relevance_score(item, preferences), 2)}
            for item in items
        ]
        
        ranked_items.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info("Ranking complete. Top item score: %.2f", ranked_items[0]["score"] if ranked_items else 0)
        return ranked_items

    # -------------------------
    # Internal helper functions
    # -------------------------
    def _matches_all_criteria(self, item: ClothingItem, preferences: UserPreferences) -> bool:
        """
        Checks if item matches user preferences and filter settings.
        """
        return self._matches_preferences(item, preferences) and self._matches_filters(item)

    def _matches_preferences(self, item: ClothingItem, preferences: UserPreferences) -> bool:
        """
        Matches the clothing item against the user's saved preferences.
        """
        normalized_size = (item.size or "").upper()
        preferred_size = (preferences.preferred_size or "").upper()
        if preferred_size and normalized_size != preferred_size:
            return False

        if preferences.preferred_colors:
            item_color = (item.color or "").lower()
            if not any(color.lower() in item_color for color in preferences.preferred_colors):
                return False

        if preferences.preferred_brands:
            if (item.brand or "").lower() not in (brand.lower() for brand in preferences.preferred_brands):
                return False

        if preferences.min_price and item.price < preferences.min_price:
            return False

        if preferences.max_price and item.price > preferences.max_price:
            return False

        return True

    def _matches_filters(self, item: ClothingItem) -> bool:
        """
        Matches the clothing item against active filter settings.
        """
        # Size filter
        if self.settings.sizes:
            if (item.size or "").upper() not in [s.upper() for s in self.settings.sizes]:
                return False

        # Color filter
        if self.settings.colors:
            item_color = (item.color or "").lower()
            if not any(color.lower() in item_color for color in self.settings.colors):
                return False

        # Brand filter
        if self.settings.brands:
            if (item.brand or "").lower() not in [b.lower() for b in self.settings.brands]:
                return False

        # Price range filter
        price_ranges = getattr(self.settings, "price_ranges", {})
        if price_ranges:
            if "min" in price_ranges and item.price < price_ranges["min"]:
                return False
            if "max" in price_ranges and item.price > price_ranges["max"]:
                return False

        return True

    def _calculate_relevance_score(self, item: ClothingItem, preferences: UserPreferences) -> float:
        """
        Calculates a relevance score based on preference matches.
        """
        score = 0

        # Brand match
        if preferences.preferred_brands and (item.brand or "").lower() in [b.lower() for b in preferences.preferred_brands]:
            score += 5

        # Color match
        if preferences.preferred_colors:
            item_color = (item.color or "").lower()
            for color in preferences.preferred_colors:
                if color.lower() in item_color:
                    score += 2
                    break  # early exit

        # Size match
        if preferences.preferred_size and (item.size or "").upper() == (preferences.preferred_size or "").upper():
            score += 3

        # Price closeness
        if preferences.min_price or preferences.max_price:
            ideal_price = (preferences.min_price + preferences.max_price) / 2 if (preferences.min_price and preferences.max_price) else preferences.min_price or preferences.max_price
            price_difference = abs(item.price - ideal_price)
            score += max(0, 2 - price_difference / 50)

        # Text relevance from description/title
        preference_keywords = set(
            word.lower() for word in (
                (preferences.description_keywords or []) +
                (preferences.title_keywords or [])
            )
        )

        item_text_tokens = set(((item.title or "") + " " + (item.description or "")).lower().split())
        score += len(preference_keywords & item_text_tokens) * 1.5

        return score
