"""Configuration management for QuantDog."""

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    QUANTUM_THREAT_LOW = int(os.getenv("QUANTUM_THREAT_LOW", "30"))
    QUANTUM_THREAT_MEDIUM = int(os.getenv("QUANTUM_THREAT_MEDIUM", "50"))
    QUANTUM_THREAT_HIGH = int(os.getenv("QUANTUM_THREAT_HIGH", "70"))
    HONEYPOT_CHECK_INTERVAL = int(os.getenv("HONEYPOT_CHECK_INTERVAL", "300"))

    ETH_RPC_URL = os.getenv(
        "ETH_TESTNET_RPC_URL", "https://eth-sepolia.g.alchemy.com/v2/demo"
    )
    BTC_RPC_URL = os.getenv(
        "BTC_TESTNET_RPC_URL", "https://api.blockcypher.com/v1/btc/test3"
    )

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(cls, key, default)


def get_settings() -> Config:
    """Get application settings instance."""
    return Config()