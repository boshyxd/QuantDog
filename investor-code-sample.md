# QuantDog - Adaptive Cryptographic Routing Engine

**Core Algorithm: Intelligent Quantum Threat Response**

```python
def route_transaction(self, transaction: dict, threat_level: float) -> RoutingPath:
    """Determine optimal routing path for a transaction."""
    # Check if path is forced (for testing)
    if self.forced_path:
        return self.forced_path

    value = transaction.get("value", 0)

    # Dynamic thresholds based on transaction value
    if value > 100000:
        threshold = 30  # Higher security for large transactions
    elif value > 10000:
        threshold = 50
    else:
        threshold = 70

    if threat_level > threshold:
        path = RoutingPath.POST_QUANTUM
    else:
        path = RoutingPath.CLASSICAL

    # Track switches for analytics
    if path != self.current_path:
        self.switch_history.append({
            "from": self.current_path.value,
            "to": path.value,
            "threat_level": threat_level,
            "threshold": threshold,
        })
        self.current_path = path

    return path
```

**Key Features Demonstrated:**
- 🔒 **Adaptive Security**: Automatically switches between classical and post-quantum cryptography
- 📊 **Risk-Based Routing**: Higher value transactions get enhanced protection
- 📈 **Real-Time Response**: Instant threat level assessment and routing decisions
- 📋 **Enterprise Analytics**: Complete audit trail of all cryptographic switches
- ⚡ **Zero-Latency Protection**: Seamless integration with existing transaction flows

*Source: `core/router.py` - The heart of QuantDog's quantum threat detection platform*