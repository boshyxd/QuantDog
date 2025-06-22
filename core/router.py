"""Cryptographic routing engine."""

from enum import Enum


class RoutingPath(Enum):
    """Available routing paths."""

    CLASSICAL = "classical"
    POST_QUANTUM = "post_quantum"


class CryptoRouter:
    """Routes transactions based on threat level and transaction parameters."""

    def __init__(self):
        self.default_path = RoutingPath.CLASSICAL
        self.threat_threshold = 50
        self.forced_path: RoutingPath | None = None
        self.current_path = RoutingPath.CLASSICAL
        self.switch_history = []

    def route_transaction(self, transaction: dict, threat_level: float) -> RoutingPath:
        """Determine optimal routing path for a transaction."""
        # Check if path is forced (for testing)
        if self.forced_path:
            return self.forced_path

        value = transaction.get("value", 0)

        # Dynamic thresholds based on transaction value
        if value > 100000:
            threshold = 30
        elif value > 10000:
            threshold = 50
        else:
            threshold = 70

        if threat_level > threshold:
            path = RoutingPath.POST_QUANTUM
        else:
            path = RoutingPath.CLASSICAL

        # Track switches
        if path != self.current_path:
            self.switch_history.append(
                {
                    "from": self.current_path.value,
                    "to": path.value,
                    "threat_level": threat_level,
                    "threshold": threshold,
                }
            )
            self.current_path = path

        return path

    def get_active_crypto_method(self, threat_level: float) -> str:
        """Get the active cryptographic method based on threat level."""
        # Simplified - uses default transaction value
        transaction = {"value": 50000}  # Medium value transaction
        path = self.route_transaction(transaction, threat_level)
        return path.value

    def get_current_threshold(self) -> float:
        """Get the current threshold (simplified)."""
        return self.threat_threshold

    def force_post_quantum(self) -> None:
        """Force post-quantum cryptography (for testing)."""
        self.forced_path = RoutingPath.POST_QUANTUM
        self.current_path = RoutingPath.POST_QUANTUM

    def force_classical(self) -> None:
        """Force classical cryptography (for testing)."""
        self.forced_path = RoutingPath.CLASSICAL
        self.current_path = RoutingPath.CLASSICAL

    def clear_forced_path(self) -> None:
        """Clear forced routing path."""
        self.forced_path = None

