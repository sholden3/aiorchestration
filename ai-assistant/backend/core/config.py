"""
@fileoverview Configuration management system for backend
@author Dr. Sarah Chen - Backend/Systems Architect
@architecture Backend - Core Configuration
@business_logic Centralized configuration with environment overrides
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache
import logging
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = "sqlite:///./ai_assistant.db"
    pool_size: int = 10
    echo: bool = False

class CacheConfig(BaseModel):
    """Cache configuration"""
    enabled: bool = True
    ttl: int = 3600
    max_size: int = 1000

class WebSocketConfig(BaseModel):
    """WebSocket configuration"""
    enabled: bool = True
    ping_interval: int = 30
    ping_timeout: int = 10

class CorsConfig(BaseModel):
    """CORS configuration"""
    enabled: bool = True
    origins: list[str] = ["http://localhost:4200", "http://localhost:8000", "file://"]

class BackendConfig(BaseModel):
    """Backend configuration"""
    host: str = "127.0.0.1"
    port: int = 8000
    protocol: str = "http"
    api_prefix: str = "/api"
    health_check_path: str = "/health"
    cors: CorsConfig = CorsConfig()
    database: DatabaseConfig = DatabaseConfig()
    cache: CacheConfig = CacheConfig()
    websocket: WebSocketConfig = WebSocketConfig()

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    format: str = "json"
    
class SecurityConfig(BaseModel):
    """Security configuration"""
    auth_enabled: bool = False
    jwt_secret: str = "CHANGE_THIS_IN_PRODUCTION"
    token_expiry: int = 3600
    rate_limiting_enabled: bool = True
    requests_per_minute: int = 60

class AIConfig(BaseModel):
    """AI integration configuration"""
    enabled: bool = False
    provider: str = "mock"
    model: str = "gpt-4"
    max_tokens: int = 2000
    api_key: Optional[str] = None

class GovernanceConfig(BaseModel):
    """Governance configuration"""
    enabled: bool = True
    audit_all_operations: bool = True
    enforce_rules: bool = True

class FeaturesConfig(BaseModel):
    """Features configuration"""
    ai_integration: AIConfig = AIConfig()
    governance: GovernanceConfig = GovernanceConfig()
    templates_enabled: bool = True
    practices_enabled: bool = True

class AppConfig(BaseSettings):
    """Main application configuration"""
    name: str = "AI Development Assistant"
    version: str = "2.0.0"
    environment: str = "development"
    
    backend: BackendConfig = BackendConfig()
    logging: LoggingConfig = LoggingConfig()
    security: SecurityConfig = SecurityConfig()
    features: FeaturesConfig = FeaturesConfig()
    
    class Config:
        env_prefix = "APP_"
        env_nested_delimiter = "__"
        case_sensitive = False

class ConfigLoader:
    """Configuration loader with environment-specific overrides"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parents[3] / "config"
        self.environment = os.getenv("APP_ENV", "development")
        self._config: Optional[AppConfig] = None
        
    def load_json_config(self, filename: str) -> Dict[str, Any]:
        """Load JSON configuration file"""
        filepath = self.config_dir / filename
        if not filepath.exists():
            logger.warning(f"Config file not found: {filepath}")
            return {}
            
        with open(filepath, 'r') as f:
            config = json.load(f)
            
        # Handle extends directive
        if "extends" in config:
            base_config = self.load_json_config(config["extends"].replace("./", ""))
            # Merge configs (env-specific overrides base)
            config = self._deep_merge(base_config, config)
            
        return config
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _substitute_env_vars(self, config: Dict) -> Dict:
        """Substitute environment variables in config"""
        def substitute(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                return os.getenv(env_var, value)
            elif isinstance(value, dict):
                return {k: substitute(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute(v) for v in value]
            return value
            
        return substitute(config)
    
    @lru_cache()
    def get_config(self) -> AppConfig:
        """Get application configuration"""
        if self._config is None:
            # Load base config
            json_config = self.load_json_config("app.config.json")
            
            # Load environment-specific config
            env_config_file = f"app.config.{self.environment}.json"
            if (self.config_dir / env_config_file).exists():
                env_config = self.load_json_config(env_config_file)
                json_config = self._deep_merge(json_config, env_config)
            
            # Substitute environment variables
            json_config = self._substitute_env_vars(json_config)
            
            # Extract relevant sections for AppConfig
            config_data = {
                "name": json_config.get("app", {}).get("name", "AI Development Assistant"),
                "version": json_config.get("app", {}).get("version", "2.0.0"),
                "environment": json_config.get("app", {}).get("environment", self.environment),
                "backend": json_config.get("backend", {}),
                "logging": json_config.get("logging", {}),
                "security": {
                    "auth_enabled": json_config.get("security", {}).get("auth", {}).get("enabled", False),
                    "jwt_secret": json_config.get("security", {}).get("auth", {}).get("jwt_secret"),
                    "token_expiry": json_config.get("security", {}).get("auth", {}).get("token_expiry", 3600),
                    "rate_limiting_enabled": json_config.get("security", {}).get("rate_limiting", {}).get("enabled", True),
                    "requests_per_minute": json_config.get("security", {}).get("rate_limiting", {}).get("requests_per_minute", 60)
                },
                "features": json_config.get("features", {})
            }
            
            # Create AppConfig from merged configuration
            self._config = AppConfig(**config_data)
            
            logger.info(f"Configuration loaded for environment: {self.environment}")
            
        return self._config
    
    def reload(self):
        """Reload configuration"""
        self._config = None
        self.get_config.cache_clear()
        logger.info("Configuration reloaded")

# Global configuration instance
config_loader = ConfigLoader()

@lru_cache()
def get_config() -> AppConfig:
    """Get application configuration"""
    return config_loader.get_config()

def get_backend_url() -> str:
    """Get backend URL"""
    config = get_config()
    return f"{config.backend.protocol}://{config.backend.host}:{config.backend.port}"

def get_database_url() -> str:
    """Get database URL"""
    config = get_config()
    return config.backend.database.url

def is_development() -> bool:
    """Check if running in development mode"""
    return get_config().environment == "development"

def is_production() -> bool:
    """Check if running in production mode"""
    return get_config().environment == "production"