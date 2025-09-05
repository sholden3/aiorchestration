"""
Configuration Loader for MCP Governance Server

Loads and validates configuration from YAML with environment variable substitution.

Author: Dr. Sarah Chen
Phase: MCP-001 PHOENIX_RISE_FOUNDATION
"""

import os
import re
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Configuration loader with environment variable substitution.
    
    Handles loading YAML configuration files and replacing
    ${VAR:default} patterns with environment variables.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to configuration file (default: mcp_config.yaml)
        """
        self.config_path = config_path or Path(__file__).parent / "mcp_config.yaml"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        
        Returns:
            Dictionary containing configuration
        """
        if not self.config_path.exists():
            logger.warning(f"Config file not found at {self.config_path}, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                content = f.read()
                # Substitute environment variables
                content = self._substitute_env_vars(content)
                config = yaml.safe_load(content)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}, using defaults")
            return self._get_default_config()
    
    def _substitute_env_vars(self, content: str) -> str:
        """
        Substitute environment variables in configuration.
        
        Replaces ${VAR:default} with environment variable VAR
        or default value if VAR is not set.
        
        Args:
            content: Configuration file content
            
        Returns:
            Content with substituted variables
        """
        pattern = re.compile(r'\$\{([^}]+):([^}]*)\}')
        
        def replacer(match):
            var_name = match.group(1)
            default_value = match.group(2)
            return os.environ.get(var_name, default_value)
        
        return pattern.sub(replacer, content)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "server": {
                "name": "mcp-governance",
                "version": "1.0.0",
                "environment": "development",
                "port": {
                    "preferred": 8001,
                    "range_start": 8001,
                    "range_end": 8100,
                    "fallback": 8001
                },
                "host": "127.0.0.1",
                "reload": True,
                "log_level": "INFO"
            },
            "database": {
                "type": "sqlite",
                "sqlite": {
                    "path": "./data/mcp_governance.db",
                    "check_same_thread": False,
                    "timeout": 30
                }
            },
            "cache": {
                "type": "memory",
                "memory": {
                    "max_size": 1000,
                    "ttl_seconds": 300,
                    "cleanup_interval": 60
                }
            },
            "governance": {
                "personas_config": "./libs/governance/personas.yaml",
                "rules_config": "./libs/governance/documentation_standards.yaml",
                "consultation": {
                    "timeout_seconds": 30,
                    "max_retries": 3,
                    "cache_enabled": True,
                    "cache_ttl": 600
                },
                "thresholds": {
                    "approval_confidence": 0.7,
                    "warning_confidence": 0.5,
                    "unanimous_required": False
                }
            },
            "monitoring": {
                "metrics": {
                    "enabled": True,
                    "interval_seconds": 60,
                    "retention_days": 30
                },
                "audit": {
                    "enabled": True,
                    "log_file": "./logs/mcp_audit.log",
                    "rotation": "daily",
                    "retention_days": 90
                }
            },
            "security": {
                "api_key": "",
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "burst_size": 10
                },
                "cors": {
                    "enabled": True,
                    "origins": ["http://localhost:4200", "http://localhost:3000"],
                    "methods": ["GET", "POST", "PUT", "DELETE"],
                    "headers": ["Content-Type", "Authorization"]
                }
            },
            "paths": {
                "port_file": "~/.ai_assistant/mcp_governance_port.txt",
                "session_state": "./data/mcp_sessions.json",
                "decision_log": "./logs/mcp_decisions.jsonl"
            },
            "performance": {
                "connection_pool": {
                    "min_size": 5,
                    "max_size": 20,
                    "timeout": 30
                },
                "request": {
                    "timeout": 60,
                    "max_payload_size": 10485760
                },
                "background": {
                    "workers": 4,
                    "queue_size": 100
                }
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to config value (e.g., "server.port.preferred")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration section."""
        return self.config.get("server", {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration section."""
        return self.config.get("database", {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache configuration section."""
        return self.config.get("cache", {})
    
    def get_governance_config(self) -> Dict[str, Any]:
        """Get governance configuration section."""
        return self.config.get("governance", {})
    
    def get_port_config(self) -> Dict[str, Any]:
        """Get port configuration for discovery."""
        port_config = self.get("server.port", {})
        return {
            "preferred_port": port_config.get("preferred", 8001),
            "port_range": (
                port_config.get("range_start", 8001),
                port_config.get("range_end", 8100)
            ),
            "fallback": port_config.get("fallback", 8001),
            "service_name": self.get("server.name", "mcp-governance")
        }
    
    def get_database_url(self) -> str:
        """
        Get database connection URL.
        
        Returns:
            Database connection string
        """
        db_config = self.get_database_config()
        db_type = db_config.get("type", "sqlite")
        
        if db_type == "postgresql":
            pg_config = db_config.get("postgresql", {})
            host = pg_config.get("host", "localhost")
            port = pg_config.get("port", 5432)
            database = pg_config.get("database", "mcp_governance")
            username = pg_config.get("username", "mcp_user")
            password = pg_config.get("password", "")
            
            if password:
                return f"postgresql://{username}:{password}@{host}:{port}/{database}"
            else:
                return f"postgresql://{username}@{host}:{port}/{database}"
        
        else:  # sqlite
            sqlite_config = db_config.get("sqlite", {})
            path = sqlite_config.get("path", "./data/mcp_governance.db")
            return f"sqlite:///{path}"
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        required_keys = [
            "server.name",
            "server.port.preferred",
            "database.type",
            "governance.personas_config"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                logger.error(f"Missing required configuration key: {key}")
                return False
        
        return True


# Global instance for convenience
_config_loader = None


def get_config() -> ConfigLoader:
    """Get or create global ConfigLoader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_mcp_config() -> Dict[str, Any]:
    """
    Convenience function to get MCP configuration.
    
    Returns:
        Complete MCP configuration dictionary
    """
    return get_config().config