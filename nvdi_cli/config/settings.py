import os
from dataclasses import dataclass
import toml
from dotenv import load_dotenv


@dataclass
class Settings:
    nvd_api_key: str = None
    cache_ttl: int = 3600
    config_path: str = os.path.expanduser("~/.config/nvdi/config.toml")

    def __post_init__(self):
        # Create config directory if it doesn't exist
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        # Create default config file if it doesn't exist
        if not os.path.exists(self.config_path):
            default_config = {
                "api": {
                    "nvd": {
                        "key": "",
                        "cache_ttl": 3600
                    }
                }
            }
            try:
                with open(self.config_path, 'w') as f:
                    toml.dump(default_config, f)
            except Exception:
                pass
        
        # Load .env file from current directory or ~/.config/nvdi/
        load_dotenv()  # Current directory
        load_dotenv(os.path.expanduser("~/.config/nvdi/.env"))  # Config directory
        
        # Load env first
        self.nvd_api_key = os.environ.get("NVD_API_KEY") or self.nvd_api_key
        self.cache_ttl = int(os.environ.get("NVD_CACHE_TTL") or self.cache_ttl)
        # Try toml config
        try:
            if os.path.exists(self.config_path):
                data = toml.load(self.config_path)
                nvd = data.get("api", {}).get("nvd", {})
                self.nvd_api_key = self.nvd_api_key or nvd.get("key")
                self.cache_ttl = int(nvd.get("cache_ttl") or self.cache_ttl)
        except Exception:
            pass
