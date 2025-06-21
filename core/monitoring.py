"""Honeypot and blockchain monitoring with WebSocket support."""

import time
import asyncio
import random
from datetime import datetime
from typing import Optional, Dict, Any


class HoneypotMonitor:
    """Monitors honeypot wallets for unauthorized access."""

    def __init__(self):
        self.honeypots = []
        self.last_check = time.time()
        self.check_interval = 300

    def add_honeypot(self, wallet_address: str, balance: float) -> None:
        """Add a honeypot wallet to monitor."""
        self.honeypots.append(
            {
                "address": wallet_address,
                "initial_balance": balance,
                "current_balance": balance,
                "compromised": False,
            }
        )

    def check_balances(self) -> list[dict]:
        """Check all honeypot balances."""
        alerts = []
        for honeypot in self.honeypots:
            if honeypot["current_balance"] < honeypot["initial_balance"]:
                alerts.append(honeypot)
        return alerts


class ThreatMonitor:
    """Monitors and broadcasts threat levels via WebSocket."""
    
    def __init__(self):
        self.current_threat_level = 20.0
        self.is_monitoring = False
        self.threat_history = []
        self.base_threat = 20.0
        self.volatility = 5.0
        
    async def start_monitoring(self, connection_manager):
        """Start the threat monitoring loop."""
        self.is_monitoring = True
        
        while self.is_monitoring:
            # Simulate threat level fluctuation
            change = random.uniform(-self.volatility, self.volatility)
            self.current_threat_level = max(0, min(100, self.current_threat_level + change))
            
            # Add some randomness for demo purposes
            if random.random() < 0.05:  # 5% chance of spike
                self.current_threat_level = min(100, self.current_threat_level + random.uniform(10, 30))
            
            # Determine status and threshold
            status = self._get_threat_status()
            threshold = self._get_threshold()
            active_crypto = "post_quantum" if self.current_threat_level >= threshold else "classical"
            
            # Create status update
            status_update = {
                "threat_level": round(self.current_threat_level, 2),
                "status": status,
                "active_crypto": active_crypto,
                "threshold": threshold,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store in history
            self.threat_history.append(status_update)
            if len(self.threat_history) > 1000:  # Keep last 1000 entries
                self.threat_history.pop(0)
            
            # Broadcast update
            await connection_manager.broadcast_threat_update(
                self.current_threat_level,
                status_update
            )
            
            # Wait before next update
            await asyncio.sleep(2)  # Update every 2 seconds
    
    def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.is_monitoring = False
    
    def _get_threat_status(self) -> str:
        """Determine threat status based on level."""
        if self.current_threat_level < 30:
            return "low"
        elif self.current_threat_level < 50:
            return "medium"
        elif self.current_threat_level < 70:
            return "high"
        else:
            return "critical"
    
    def _get_threshold(self) -> float:
        """Get dynamic threshold (simplified for demo)."""
        # In production, this would consider transaction values
        return 50.0
    
    def simulate_attack(self, intensity: float):
        """Simulate a quantum attack."""
        self.current_threat_level = min(100, self.current_threat_level + intensity)
    
    def reduce_threat(self, amount: float):
        """Reduce threat level."""
        self.current_threat_level = max(0, self.current_threat_level - amount)