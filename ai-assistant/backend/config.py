"""
Unified Configuration System
Business Context: Centralized configuration management for all system components
Architecture Pattern: Singleton configuration with environment variable override
Performance Requirements: Fast access, type-safe, validated at startup
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

class AIIntegrationConfig(BaseSettings):
    """Dr. Sarah Chen's Domain: Claude and AI Configuration"""
    
    # Claude Integration
    claude_model: str = Field("claude-3-sonnet", description="Default Claude model")
    claude_max_tokens: int = Field(4000, description="Maximum tokens per request")
    claude_timeout_seconds: int = Field(30, description="Claude API timeout")
    token_estimation_divisor: int = Field(4, description="Characters per token estimate")
    token_cost_per_unit: float = Field(0.00002, description="Cost per token in USD")
    
    # API Key Configuration (cascading priority: env > config > CLI fallback)
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY", description="Anthropic API key (optional)")
    
    # Claude Executable Paths (Windows)
    claude_paths: list = Field(
        default=[
            "claude",
            "claude-code",
            r"C:\Program Files\Claude\claude.exe",
            r"C:\Users\%USERNAME%\AppData\Local\Claude\claude.exe"
        ],
        description="Potential Claude executable locations"
    )
    
    # Persona Configurations
    persona_confidence_threshold: float = Field(0.7, description="Min confidence for persona selection")
    persona_voting_weight: dict = Field(
        default={
            "ai_integration": 1.0,
            "systems_performance": 1.0,
            "ux_frontend": 1.0
        },
        description="Voting weights for each persona"
    )
    
    class Config:
        env_prefix = "AI_"

class SystemsPerformanceConfig(BaseSettings):
    """Marcus Rodriguez's Domain: Performance and Infrastructure"""
    
    # Database Configuration
    db_host: str = Field("localhost", description="PostgreSQL host")
    db_port: int = Field(5432, description="PostgreSQL port")
    db_name: str = Field("ai_assistant", description="Database name")
    db_user: str = Field("postgres", description="Database user")
    db_password: str = Field("postgres", description="Database password")
    
    # Connection Pool Settings
    db_pool_min_size: int = Field(2, description="Minimum connection pool size")
    db_pool_max_size: int = Field(10, description="Maximum connection pool size")
    db_max_queries: int = Field(50000, description="Max queries per connection")
    db_max_inactive_lifetime: int = Field(300, description="Max inactive connection lifetime (seconds)")
    db_command_timeout: int = Field(10, description="Command timeout (seconds)")
    
    # Cache Configuration
    cache_hot_size_mb: int = Field(512, description="Hot cache size in MB")
    cache_warm_size_mb: int = Field(2048, description="Warm cache size in MB")
    cache_default_ttl_seconds: int = Field(3600, description="Default cache TTL")
    cache_max_ttl_seconds: int = Field(86400, description="Maximum cache TTL")
    
    # Performance Targets
    target_cache_hit_rate: float = Field(0.90, description="Target 90% cache hit rate")
    target_token_reduction: float = Field(0.65, description="Target 65% token reduction")
    target_response_time_ms: int = Field(500, description="Target response time")
    target_p95_response_time_ms: int = Field(1000, description="Target P95 response time")
    
    # Metrics Configuration
    metrics_window_size: int = Field(1000, description="Rolling window for metrics")
    metrics_collection_interval: int = Field(60, description="Metrics snapshot interval (seconds)")
    metrics_retention_hours: int = Field(24, description="Metrics retention period")
    
    # Backend Service
    backend_port: int = Field(8000, description="FastAPI backend port")
    backend_workers: int = Field(4, description="Number of worker processes")
    
    class Config:
        env_prefix = "SYSTEMS_"

class UXFrontendConfig(BaseSettings):
    """Emily Watson's Domain: UX and Frontend Configuration"""
    
    # Terminal Configuration
    terminal_default_cols: int = Field(120, description="Default terminal columns")
    terminal_default_rows: int = Field(30, description="Default terminal rows")
    terminal_scrollback_lines: int = Field(10000, description="Terminal scrollback buffer")
    terminal_font_family: str = Field("Consolas, 'Courier New', monospace", description="Terminal font")
    terminal_font_size: int = Field(14, description="Terminal font size in pixels")
    
    # UI Configuration
    ui_theme: str = Field("dark", description="Default UI theme (dark/light)")
    ui_animation_duration_ms: int = Field(200, description="UI animation duration")
    ui_debounce_delay_ms: int = Field(300, description="Input debounce delay")
    ui_auto_save_interval_seconds: int = Field(30, description="Auto-save interval")
    
    # Dashboard Settings
    dashboard_refresh_interval_ms: int = Field(5000, description="Dashboard update interval")
    dashboard_chart_points: int = Field(50, description="Number of points in charts")
    dashboard_alert_threshold_cpu: float = Field(80.0, description="CPU alert threshold %")
    dashboard_alert_threshold_memory: float = Field(85.0, description="Memory alert threshold %")
    
    # Accessibility
    accessibility_high_contrast: bool = Field(False, description="High contrast mode")
    accessibility_screen_reader: bool = Field(True, description="Screen reader support")
    accessibility_keyboard_nav: bool = Field(True, description="Full keyboard navigation")
    
    class Config:
        env_prefix = "UX_"

class ApplicationConfig(BaseSettings):
    """Root Application Configuration"""
    
    # Application Metadata
    app_name: str = Field("AI Development Assistant", description="Application name")
    app_version: str = Field("1.0.0", description="Application version")
    app_environment: str = Field("development", description="Environment (development/production)")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field("json", description="Log format (json/text)")
    log_file: Optional[str] = Field(None, description="Log file path")
    
    # Security
    enable_cors: bool = Field(True, description="Enable CORS for API")
    cors_origins: list = Field(["http://localhost:4200"], description="Allowed CORS origins")
    api_key_required: bool = Field(False, description="Require API key for requests")
    
    # Paths
    data_dir: Path = Field(Path("./data"), description="Data directory")
    cache_dir: Path = Field(Path("./cache"), description="Cache directory")
    logs_dir: Path = Field(Path("./logs"), description="Logs directory")
    
    @field_validator("data_dir", "cache_dir", "logs_dir", mode='before')
    def create_directories(cls, v):
        """Ensure directories exist"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    class Config:
        env_prefix = "APP_"

class Config:
    """
    Unified Configuration Manager
    Orchestrated by all three personas for comprehensive coverage
    """
    
    def __init__(self):
        """Initialize all configuration domains"""
        self.ai = AIIntegrationConfig()
        self.systems = SystemsPerformanceConfig()
        self.ux = UXFrontendConfig()
        self.app = ApplicationConfig()
        
        # Computed properties
        self._db_connection_string = None
        
    @property
    def database_url(self) -> str:
        """Generate database connection string"""
        if not self._db_connection_string:
            self._db_connection_string = (
                f"postgresql://{self.systems.db_user}:{self.systems.db_password}"
                f"@{self.systems.db_host}:{self.systems.db_port}/{self.systems.db_name}"
            )
        return self._db_connection_string
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app.app_environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.app.app_environment == "development"
    
    def validate(self) -> bool:
        """
        Validate configuration across all domains
        Returns True if valid, raises exception otherwise
        """
        # AI Domain Validation (Dr. Sarah Chen)
        assert self.ai.claude_max_tokens > 0, "Invalid max tokens"
        assert self.ai.claude_timeout_seconds > 0, "Invalid timeout"
        assert 0 <= self.ai.persona_confidence_threshold <= 1, "Invalid confidence threshold"
        
        # Systems Domain Validation (Marcus Rodriguez)
        assert self.systems.db_pool_max_size >= self.systems.db_pool_min_size, "Invalid pool sizes"
        assert self.systems.cache_hot_size_mb < self.systems.cache_warm_size_mb, "Hot cache should be smaller"
        assert 0 < self.systems.target_cache_hit_rate <= 1, "Invalid cache hit rate target"
        assert 0 < self.systems.target_token_reduction <= 1, "Invalid token reduction target"
        
        # UX Domain Validation (Emily Watson)
        assert self.ux.terminal_default_cols > 0, "Invalid terminal columns"
        assert self.ux.terminal_default_rows > 0, "Invalid terminal rows"
        assert self.ux.ui_theme in ["dark", "light"], "Invalid theme"
        
        return True
    
    def to_dict(self) -> dict:
        """Export all configuration as dictionary"""
        return {
            "ai": self.ai.dict(),
            "systems": self.systems.dict(),
            "ux": self.ux.dict(),
            "app": self.app.dict()
        }
    
    @classmethod
    def from_env_file(cls, env_file: str = ".env"):
        """Load configuration from .env file"""
        from dotenv import load_dotenv
        load_dotenv(env_file)
        return cls()

# Global configuration instance
config = Config()

# Validate on import
try:
    config.validate()
except AssertionError as e:
    import logging
    logging.error(f"Configuration validation failed: {e}")
    raise