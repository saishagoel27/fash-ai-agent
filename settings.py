"""
Settings and configuration management
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class AISettings(BaseModel):
    """AI configuration settings"""
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    fallback_model: str = "gpt-3.5-turbo-instruct"


class SiteConfig(BaseModel):
    """Configuration for individual e-commerce sites"""
    base_url: str
    search_endpoint: str
    rate_limit: float = 1.0


class SearchSettings(BaseModel):
    """Search configuration settings"""
    max_results_per_site: int = 50
    max_total_results: int = 200
    search_timeout: int = 30
    concurrent_searches: int = 5


class ScrapingSettings(BaseModel):
    """Web scraping configuration"""
    request_delay: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    respect_robots_txt: bool = True


class NotificationSettings(BaseModel):
    """Notification configuration"""
    price_drop_threshold: float = 0.2
    new_items_alert: bool = True
    daily_summary: bool = True
    email_enabled: bool = True


class StorageSettings(BaseModel):
    """Storage configuration"""
    cache_expiry_hours: int = 24
    max_cache_size_mb: int = 100
    backup_frequency_days: int = 7
    cleanup_old_data_days: int = 30


class LoggingSettings(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_rotation: str = "daily"
    max_file_size_mb: int = 10
    backup_count: int = 7


class Settings(BaseSettings):
    """Main settings class that loads from environment and config files"""
    
    # Environment variables
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    serp_api_key: str = Field(default="", env="SERP_API_KEY")
    database_url: str = Field(default="sqlite:///data/clothing_agent.db", env="DATABASE_URL")
    
    # Email settings
    smtp_server: str = Field(default="smtp.gmail.com", env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    email_address: str = Field(default="", env="EMAIL_ADDRESS")
    email_password: str = Field(default="", env="EMAIL_PASSWORD")
    
    # Basic settings
    request_delay: float = Field(default=1.0, env="REQUEST_DELAY")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    timeout: int = Field(default=30, env="TIMEOUT")
    max_results_per_site: int = Field(default=50, env="MAX_RESULTS_PER_SITE")
    price_alert_threshold: float = Field(default=0.2, env="PRICE_ALERT_THRESHOLD")
    cache_expiry_hours: int = Field(default=24, env="CACHE_EXPIRY_HOURS")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    
    # Configuration from JSON files
    _config_data: Optional[Dict[str, Any]] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, config_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self._config_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    @property
    def ai(self) -> AISettings:
        """Get AI settings"""
        if self._config_data and "ai" in self._config_data:
            return AISettings(**self._config_data["ai"])
        return AISettings()
    
    @property
    def search(self) -> SearchSettings:
        """Get search settings"""
        if self._config_data and "search" in self._config_data:
            return SearchSettings(**self._config_data["search"])
        return SearchSettings()
    
    @property
    def scraping(self) -> ScrapingSettings:
        """Get scraping settings"""
        if self._config_data and "scraping" in self._config_data:
            return ScrapingSettings(**self._config_data["scraping"])
        return ScrapingSettings()
    
    @property
    def notifications(self) -> NotificationSettings:
        """Get notification settings"""
        if self._config_data and "notifications" in self._config_data:
            return NotificationSettings(**self._config_data["notifications"])
        return NotificationSettings()
    
    @property
    def storage(self) -> StorageSettings:
        """Get storage settings"""
        if self._config_data and "storage" in self._config_data:
            return StorageSettings(**self._config_data["storage"])
        return StorageSettings()
    
    @property
    def logging(self) -> LoggingSettings:
        """Get logging settings"""
        if self._config_data and "logging" in self._config_data:
            return LoggingSettings(**self._config_data["logging"])
        return LoggingSettings()
    
    @property
    def sites(self) -> Dict[str, SiteConfig]:
        """Get site configurations"""
        if self._config_data and "sites" in self._config_data:
            sites_data = self._config_data["sites"]
            enabled_sites = sites_data.get("enabled", [])
            configs = {}
            
            for site in enabled_sites:
                if site in sites_data and isinstance(sites_data[site], dict):
                    configs[site] = SiteConfig(**sites_data[site])
            
            return configs
        return {}
    
    @property
    def enabled_sites(self) -> List[str]:
        """Get list of enabled sites"""
        if self._config_data and "sites" in self._config_data:
            return self._config_data["sites"].get("enabled", [])
        return ["amazon", "ebay", "etsy", "asos"]
    
    @property
    def price_ranges(self) -> Dict[str, List[int]]:
        """Get price range definitions"""
        if self._config_data and "filters" in self._config_data:
            return self._config_data["filters"].get("price_ranges", {})
        return {
            "budget": [0, 50],
            "moderate": [50, 150],
            "premium": [150, 500],
            "luxury": [500, 999999]
        }
    
    @property
    def available_sizes(self) -> List[str]:
        """Get available clothing sizes"""
        if self._config_data and "filters" in self._config_data:
            return self._config_data["filters"].get("sizes", [])
        return ["XS", "S", "M", "L", "XL", "XXL"]
    
    @property
    def available_colors(self) -> List[str]:
        """Get available colors"""
        if self._config_data and "filters" in self._config_data:
            return self._config_data["filters"].get("colors", [])
        return ["black", "white", "blue", "red", "green", "yellow", "pink", "purple", "brown", "gray"]
    
    @property
    def categories(self) -> List[str]:
        """Get clothing categories"""
        if self._config_data and "filters" in self._config_data:
            return self._config_data["filters"].get("categories", [])
        return ["tops", "bottoms", "dresses", "outerwear", "shoes", "accessories"]


def get_settings(config_path: Optional[str] = None) -> Settings:
    """Get settings instance"""
    return Settings(config_path=config_path)
