"""
Centralized configuration manager for PythonParagon.

This module handles loading and accessing configuration settings from config.yaml.
"""
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class ConfigManager:
    """Centralized configuration manager using YAML."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. Defaults to config.yaml in the root directory.
        """
        if config_path is None:
            # Look for config.yaml in the project root
            current = Path(__file__).parent.parent.parent
            config_path = current / "config.yaml"
        
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = self._get_default_config()
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config file is not available."""
        return {
            "app": {
                "name": "PythonParagon",
                "version": "2.0.0",
                "author": "PythonParagon Team"
            },
            "api": {
                "currency_api": "https://api.exchangerate-api.com/v4/latest/",
                "ip_api": "https://api.ipify.org?format=json"
            },
            "network": {
                "timeout": 10,
                "max_retries": 3
            },
            "file_operations": {
                "max_file_size_mb": 100,
                "supported_extensions": [".txt", ".json", ".yaml", ".yml", ".csv", ".md", ".log", ".xml"]
            },
            "security": {
                "password_length": 16,
                "include_special_chars": True
            },
            "docker": {
                "timeout": 30
            },
            "git": {
                "default_branch": "main"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path (e.g., 'app.name').
        
        Args:
            key: Dot-separated key path
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get the entire configuration dictionary."""
        return self._config.copy()


# Global configuration instance
config = ConfigManager()
