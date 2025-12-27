import os
from dataclasses import dataclass
import toml


@dataclass
class Settings:
    nvd_api_key: str = None
    cache_ttl: int = 3600
    config_path: str = os.path.expanduser("~/.config/nvdi/config.toml")

    def __post_init__(self):
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
