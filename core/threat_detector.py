"""Quantum threat detection logic."""

import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class ThreatDetector:
    """Detects quantum threats based on various indicators."""

    def __init__(self):
        self.threat_level = 20.0  # Start at baseline
        self.indicators = []
        self.threat_history = []
        self.last_update = datetime.utcnow()
        
    def get_current_threat_level(self) -> float:
        """Get the current threat level."""
        # Add slight random variation for realism
        variation = random.uniform(-2, 2)
        return max(0, min(100, self.threat_level + variation))
    
    def calculate_threat_level(self) -> float:
        """Calculate current quantum threat level (0-100)."""
        return self.get_current_threat_level()
    
    def simulate_attack(self, intensity: float) -> None:
        """Simulate a quantum attack with given intensity."""
        self.threat_level = min(100, self.threat_level + intensity)
        self.indicators.append({
            "type": "simulated_attack",
            "intensity": intensity,
            "timestamp": datetime.utcnow()
        })
        self._update_history()
    
    def reduce_threat(self, amount: float) -> None:
        """Reduce threat level by specified amount."""
        self.threat_level = max(0, self.threat_level - amount)
        self._update_history()
    
    def check_honeypots(self, honeypots: List[Dict]) -> bool:
        """Check if any honeypot wallets have been compromised."""
        for honeypot in honeypots:
            if honeypot.get("compromised", False):
                self.threat_level = min(100, self.threat_level + 20)
                self.indicators.append({
                    "type": "honeypot_breach",
                    "address": honeypot["address"],
                    "timestamp": datetime.utcnow()
                })
                return True
        return False
    
    def analyze_blockchain_patterns(self) -> Dict:
        """Analyze blockchain for suspicious patterns."""
        # Simulate pattern detection
        suspicious_count = random.randint(0, 5)
        dormant_count = random.randint(0, 3)
        
        if suspicious_count > 3:
            self.threat_level = min(100, self.threat_level + 10)
            self.indicators.append({
                "type": "suspicious_pattern",
                "count": suspicious_count,
                "timestamp": datetime.utcnow()
            })
        
        if dormant_count > 1:
            self.threat_level = min(100, self.threat_level + 15)
            self.indicators.append({
                "type": "dormant_activation",
                "count": dormant_count,
                "timestamp": datetime.utcnow()
            })
        
        return {
            "suspicious_transactions": suspicious_count,
            "dormant_activations": dormant_count
        }
    
    def get_historical_threat(self, hours_ago: int) -> float:
        """Get historical threat level from N hours ago."""
        # Simulate historical data
        base = max(10, self.threat_level - (hours_ago * 2))
        return base + random.uniform(-5, 5)
    
    def _update_history(self) -> None:
        """Update threat history."""
        self.threat_history.append({
            "threat_level": self.threat_level,
            "timestamp": datetime.utcnow(),
            "indicators": len(self.indicators)
        })
        
        # Keep only last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.threat_history = [
            h for h in self.threat_history 
            if h["timestamp"] > cutoff
        ]