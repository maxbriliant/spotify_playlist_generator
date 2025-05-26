"""
Configuration Management - Centralized config handling
====================================================
Version: 2.0.0
Author: MaxBriliant

Provides centralized configuration management with environment variable
support, validation, and sensible defaults.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

@dataclass
class SpotifyConfig:
    """Spotify API configuration."""
    client_id: str
    client_secret: str
    redirect_uri: str = "http://127.0.0.1:8888/callback"
    cache_path: str = ".spotify_cache"
    
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return bool(self.client_id and self.client_secret and self.redirect_uri)

@dataclass
class UIConfig:
    """User interface configuration."""
    theme: str = "dark"  # "dark" or "light"
    window_width: int = 900
    window_height: int = 700
    auto_open_playlist: bool = True
    remember_last_file: bool = True
    show_console: bool = True

@dataclass
class AppConfig:
    """General application configuration."""
    batch_size: int = 100
    max_search_results: int = 5
    search_timeout: int = 30
    log_level: str = "INFO"
    log_file: str = "spotify_playlist.log"
    auto_backup: bool = True

class ConfigManager:
    """
    Centralized configuration management.
    
    Handles loading from:
    1. Environment variables
    2. .env file
    3. config.json file
    4. Default values
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing config files (defaults to current dir)
        """
        self.config_dir = Path(config_dir) if config_dir else Path.cwd()
        self.env_file = self.config_dir / ".env"
        self.config_file = self.config_dir / "config.json"
        
        # Load configurations
        self._load_environment()
        self._cached_configs = {}
    
    def _load_environment(self):
        """Load environment variables from .env file if it exists."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.debug(f"Loaded environment from {self.env_file}")
    
    def get_spotify_config(self) -> SpotifyConfig:
        """Get Spotify API configuration."""
        if 'spotify' not in self._cached_configs:
            config = SpotifyConfig(
                client_id=os.getenv("SPOTIPY_CLIENT_ID", ""),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET", ""),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
                cache_path=os.getenv("SPOTIFY_CACHE_PATH", ".spotify_cache")
            )
            self._cached_configs['spotify'] = config
        
        return self._cached_configs['spotify']
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration."""
        if 'ui' not in self._cached_configs:
            # Load from config file first, then env vars
            file_config = self._load_config_file().get('ui', {})
            
            config = UIConfig(
                theme=os.getenv("UI_THEME", file_config.get('theme', 'dark')),
                window_width=int(os.getenv("UI_WIDTH", file_config.get('window_width', 900))),
                window_height=int(os.getenv("UI_HEIGHT", file_config.get('window_height', 700))),
                auto_open_playlist=self._get_bool_env("AUTO_OPEN_PLAYLIST", 
                                                    file_config.get('auto_open_playlist', True)),
                remember_last_file=self._get_bool_env("REMEMBER_LAST_FILE", 
                                                     file_config.get('remember_last_file', True)),
                show_console=self._get_bool_env("SHOW_CONSOLE", 
                                              file_config.get('show_console', True))
            )
            self._cached_configs['ui'] = config
        
        return self._cached_configs['ui']
    
    def get_app_config(self) -> AppConfig:
        """Get application configuration."""
        if 'app' not in self._cached_configs:
            file_config = self._load_config_file().get('app', {})
            
            config = AppConfig(
                batch_size=int(os.getenv("BATCH_SIZE", file_config.get('batch_size', 100))),
                max_search_results=int(os.getenv("MAX_SEARCH_RESULTS", 
                                                file_config.get('max_search_results', 5))),
                search_timeout=int(os.getenv("SEARCH_TIMEOUT", 
                                           file_config.get('search_timeout', 30))),
                log_level=os.getenv("LOG_LEVEL", file_config.get('log_level', 'INFO')),
                log_file=os.getenv("LOG_FILE", file_config.get('log_file', 'spotify_playlist.log')),
                auto_backup=self._get_bool_env("AUTO_BACKUP", 
                                             file_config.get('auto_backup', True))
            )
            self._cached_configs['app'] = config
        
        return self._cached_configs['app']
    
    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")
            return {}
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def save_ui_config(self, ui_config: UIConfig):
        """Save UI configuration to file."""
        try:
            config_data = self._load_config_file()
            config_data['ui'] = asdict(ui_config)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Update cache
            self._cached_configs['ui'] = ui_config
            logger.debug("UI configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save UI config: {e}")
    
    def save_app_config(self, app_config: AppConfig):
        """Save application configuration to file."""
        try:
            config_data = self._load_config_file()
            config_data['app'] = asdict(app_config)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Update cache
            self._cached_configs['app'] = app_config
            logger.debug("App configuration saved")
            
        except Exception as e:
            logger.error(f"Failed to save app config: {e}")
    
    def create_env_template(self) -> bool:
        """Create .env template file with examples."""
        template = """# Spotify API Credentials
# Get these from: https://developer.spotify.com/dashboard
# 1. Create a Spotify app
# 2. Copy Client ID and Client Secret
# 3. Set Redirect URI to: http://127.0.0.1:8888/callback

SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

# Optional: Custom cache path
# SPOTIFY_CACHE_PATH=.spotify_cache

# UI Configuration (Optional)
# UI_THEME=dark
# UI_WIDTH=900
# UI_HEIGHT=700
# AUTO_OPEN_PLAYLIST=true
# REMEMBER_LAST_FILE=true
# SHOW_CONSOLE=true

# App Configuration (Optional)
# BATCH_SIZE=100
# MAX_SEARCH_RESULTS=5
# SEARCH_TIMEOUT=30
# LOG_LEVEL=INFO
# LOG_FILE=spotify_playlist.log
# AUTO_BACKUP=true
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(template)
            logger.info(f"Created .env template: {self.env_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create .env template: {e}")
            return False
    
    def create_config_template(self) -> bool:
        """Create config.json template file."""
        template = {
            "ui": {
                "theme": "dark",
                "window_width": 900,
                "window_height": 700,
                "auto_open_playlist": True,
                "remember_last_file": True,
                "show_console": True
            },
            "app": {
                "batch_size": 100,
                "max_search_results": 5,
                "search_timeout": 30,
                "log_level": "INFO",
                "log_file": "spotify_playlist.log",
                "auto_backup": True
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"Created config template: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to create config template: {e}")
            return False
    
    def validate_spotify_config(self) -> tuple[bool, list[str]]:
        """
        Validate Spotify configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        config = self.get_spotify_config()
        errors = []
        
        if not config.client_id:
            errors.append("SPOTIPY_CLIENT_ID is not set")
        elif config.client_id == "your_client_id_here":
            errors.append("SPOTIPY_CLIENT_ID still contains placeholder value")
        
        if not config.client_secret:
            errors.append("SPOTIPY_CLIENT_SECRET is not set")
        elif config.client_secret == "your_client_secret_here":
            errors.append("SPOTIPY_CLIENT_SECRET still contains placeholder value")
        
        if not config.redirect_uri:
            errors.append("SPOTIPY_REDIRECT_URI is not set")
        
        return len(errors) == 0, errors
    
    def get_last_used_file(self) -> Optional[str]:
        """Get the last used playlist file path."""
        try:
            config_data = self._load_config_file()
            return config_data.get('last_used_file')
        except Exception:
            return None
    
    def save_last_used_file(self, file_path: str):
        """Save the last used playlist file path."""
        try:
            config_data = self._load_config_file()
            config_data['last_used_file'] = file_path
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Failed to save last used file: {e}")
    
    def get_recent_files(self, limit: int = 5) -> list[str]:
        """Get list of recently used files."""
        try:
            config_data = self._load_config_file()
            recent = config_data.get('recent_files', [])
            return [f for f in recent[:limit] if Path(f).exists()]
        except Exception:
            return []
    
    def add_recent_file(self, file_path: str, limit: int = 5):
        """Add a file to recent files list."""
        try:
            config_data = self._load_config_file()
            recent = config_data.get('recent_files', [])
            
            # Remove if already exists
            if file_path in recent:
                recent.remove(file_path)
            
            # Add to beginning
            recent.insert(0, file_path)
            
            # Limit size
            recent = recent[:limit]
            
            config_data['recent_files'] = recent
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Failed to add recent file: {e}")
    
    def clear_cache(self):
        """Clear cached configurations."""
        self._cached_configs.clear()
        logger.debug("Configuration cache cleared")
    
    def __repr__(self) -> str:
        """String representation of ConfigManager."""
        return f"ConfigManager(config_dir={self.config_dir})"