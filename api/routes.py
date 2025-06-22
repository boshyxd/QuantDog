import asyncio
from datetime import datetime

from fastapi import APIRouter, HTTPException

from api.models import (
    CryptoMethod,
    DeployHoneypotRequest,
    HoneypotConfig,
    HoneypotData,
    HoneypotInteraction,
    RecordInteractionRequest,
    ReduceThreatRequest,
    SimulateAttackRequest,
    SystemMetrics,
    SystemSettings,
    ThreatLevel,
    ThreatStatus,
    Transaction,
)
from core.router import CryptoRouter
from core.threat_detector import ThreatDetector
from services.blockchain import BlockchainService
from utils.config import get_settings

router = APIRouter()
settings = get_settings()

# Initialize services
threat_detector = ThreatDetector()
crypto_router = CryptoRouter()
blockchain_service = BlockchainService()

# In-memory storage for honeypot configurations
honeypot_configs = {
    "honeypot_0": {
        "name": "Quantum Honeypot 1",
        "monitoring_sensitivity": "medium",
        "protection_type": "ecdsa",
        "auto_response": True,
        "routing_method": "classical",
        "blockchain": "ethereum",
        "description": "Primary Ethereum honeypot",
        "interaction_count": 0,
        "last_interaction": None,
        "threat_indicators": []
    },
    "honeypot_1": {
        "name": "Quantum Honeypot 2",
        "monitoring_sensitivity": "medium",
        "protection_type": "rsa",
        "auto_response": True,
        "routing_method": "classical",
        "blockchain": "bitcoin",
        "description": "Bitcoin monitoring honeypot",
        "interaction_count": 0,
        "last_interaction": None,
        "threat_indicators": []
    },
    "honeypot_2": {
        "name": "Quantum Honeypot 3",
        "monitoring_sensitivity": "high",
        "protection_type": "ecdsa",
        "auto_response": True,
        "routing_method": "classical",
        "blockchain": "quantum",
        "description": "High-sensitivity quantum testnet honeypot",
        "interaction_count": 0,
        "last_interaction": None,
        "threat_indicators": []
    }
}

# Track disabled honeypots
disabled_honeypots = set()

# In-memory storage for honeypot interactions
honeypot_interactions = []


@router.get("/status", response_model=ThreatStatus)
async def get_status():
    """Get current system status including threat level and active cryptography."""
    current_threat = threat_detector.get_current_threat_level()
    active_crypto = crypto_router.get_active_crypto_method(current_threat)

    # Determine status level
    if current_threat < 30:
        status = ThreatLevel.LOW
    elif current_threat < 50:
        status = ThreatLevel.MEDIUM
    elif current_threat < 70:
        status = ThreatLevel.HIGH
    else:
        status = ThreatLevel.CRITICAL

    return ThreatStatus(
        threat_level=current_threat,
        status=status,
        active_crypto=CryptoMethod.POST_QUANTUM if active_crypto == "post_quantum" else CryptoMethod.CLASSICAL,
        threshold=crypto_router.get_current_threshold(),
        timestamp=datetime.utcnow(),
        message=f"System operating with {active_crypto} cryptography"
    )


@router.post("/simulate/attack", response_model=ThreatStatus)
async def simulate_attack(request: SimulateAttackRequest):
    """Simulate a quantum attack to increase threat level."""
    threat_detector.simulate_attack(request.intensity)

    if request.duration:
        # Schedule threat reduction after duration
        async def reduce_after_delay():
            await asyncio.sleep(request.duration)
            threat_detector.reduce_threat(request.intensity)

        asyncio.create_task(reduce_after_delay())

    return await get_status()


@router.post("/simulate/reduce-threat", response_model=ThreatStatus)
async def reduce_threat(request: ReduceThreatRequest):
    """Reduce the current threat level."""
    threat_detector.reduce_threat(request.amount)
    return await get_status()


@router.get("/transactions", response_model=list[Transaction])
async def get_transactions(limit: int = 10):
    """Get recent transactions with their cryptographic methods."""
    # This would normally fetch from a database
    # For now, return mock data
    transactions = []
    for i in range(limit):
        threat_at_time = threat_detector.get_historical_threat(i)
        crypto_method = crypto_router.get_active_crypto_method(threat_at_time)

        transactions.append(Transaction(
            id=f"tx_{i}",
            amount=1000.0 * (i + 1),
            from_address=f"0x{'a' * 40}",
            to_address=f"0x{'b' * 40}",
            timestamp=datetime.utcnow(),
            crypto_method=CryptoMethod.POST_QUANTUM if crypto_method == "post_quantum" else CryptoMethod.CLASSICAL,
            threat_level_at_time=threat_at_time
        ))

    return transactions


@router.get("/debug/honeypot-configs")
async def get_honeypot_configs_debug():
    """Debug endpoint to see all honeypot configs."""
    return {
        "total_configs": len(honeypot_configs),
        "configs": honeypot_configs,
        "disabled_honeypots": list(disabled_honeypots)
    }


@router.get("/honeypots", response_model=list[HoneypotData])
async def get_honeypots():
    """Get status of all honeypot systems."""
    # Load honeypot data from configuration storage
    honeypots = []

    for honeypot_id, config in honeypot_configs.items():
        # Extract index from honeypot_id for backwards compatibility with mock data
        try:
            index = int(honeypot_id.split('_')[1])
        except (IndexError, ValueError):
            index = len(honeypots)

        # Determine status based on whether honeypot is disabled
        if honeypot_id in disabled_honeypots:
            status = "disabled"
        elif index < 2:
            status = "active"
        else:
            status = "triggered"

        honeypots.append(HoneypotData(
            id=honeypot_id,
            name=config.get("name", f"Quantum Honeypot {index+1}"),
            status=status,
            last_interaction=config.get("last_interaction"),
            interaction_count=config.get("interaction_count", 0),
            threat_indicators=config.get("threat_indicators", []),
            protection_type=config.get("protection_type", "ecdsa"),
            monitoring_sensitivity=config.get("monitoring_sensitivity", "medium"),
            blockchain=config.get("blockchain", "ethereum"),
            description=config.get("description", "")
        ))

    # Sort by honeypot ID to maintain consistent order
    honeypots.sort(key=lambda x: x.id)

    return honeypots


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """Get current system performance metrics."""
    import time

    import psutil

    return SystemMetrics(
        cpu_usage=psutil.cpu_percent(),
        memory_usage=psutil.virtual_memory().percent,
        active_connections=len(asyncio.all_tasks()),
        processed_transactions=1234,  # Mock value
        threats_detected=42,  # Mock value
        uptime_seconds=time.time()  # Mock value
    )


@router.post("/crypto/switch/{method}")
async def switch_crypto_method(method: CryptoMethod):
    """Manually switch cryptographic method (for testing)."""
    if method == CryptoMethod.POST_QUANTUM:
        crypto_router.force_post_quantum()
    else:
        crypto_router.force_classical()

    return {"message": f"Switched to {method} cryptography"}


@router.get("/threat/history")
async def get_threat_history(hours: int = 24):
    """Get threat level history for the specified time period."""
    # This would normally query a time-series database
    # For now, return mock data
    history = []
    for i in range(hours):
        history.append({
            "timestamp": datetime.utcnow(),
            "threat_level": threat_detector.get_historical_threat(i),
            "hour": i
        })

    return {"history": history}


@router.put("/honeypots/{honeypot_id}/config")
async def update_honeypot_config(honeypot_id: str, config: HoneypotConfig):
    """Update honeypot configuration."""
    # Update the in-memory configuration storage
    honeypot_configs[honeypot_id] = {
        "monitoring_sensitivity": config.monitoring_sensitivity,
        "protection_type": config.protection_type,
        "auto_response": config.auto_response,
        "routing_method": config.routing_method
    }

    # Update crypto router if needed
    if config.protection_type == "rsa":
        crypto_router.force_classical()
    elif config.protection_type == "ecdsa":
        crypto_router.force_classical()  # Both RSA and ECDSA are classical

    if config.routing_method == "post_quantum":
        crypto_router.force_post_quantum()

    return {"message": f"Honeypot {honeypot_id} configuration updated successfully"}


@router.post("/honeypots/{honeypot_id}/disable")
async def disable_honeypot(honeypot_id: str):
    """Disable a specific honeypot."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")

    # Add to disabled set
    disabled_honeypots.add(honeypot_id)

    return {"message": f"Honeypot {honeypot_id} has been disabled"}


@router.post("/honeypots/{honeypot_id}/enable")
async def enable_honeypot(honeypot_id: str):
    """Enable a specific honeypot."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")

    # Remove from disabled set
    disabled_honeypots.discard(honeypot_id)

    return {"message": f"Honeypot {honeypot_id} has been enabled"}


@router.delete("/honeypots/{honeypot_id}")
async def delete_honeypot(honeypot_id: str):
    """Delete a specific honeypot permanently."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")

    # Remove from configurations
    del honeypot_configs[honeypot_id]
    
    # Remove from disabled set if it was disabled
    disabled_honeypots.discard(honeypot_id)

    # In a real implementation, this would:
    # 1. Stop all monitoring processes for this honeypot
    # 2. Clean up deployed infrastructure
    # 3. Remove smart contracts if applicable
    # 4. Archive historical data
    # 5. Clean up network routing rules

    return {"message": f"Honeypot {honeypot_id} has been permanently deleted"}


@router.get("/honeypots/{honeypot_id}/config", response_model=HoneypotConfig)
async def get_honeypot_config(honeypot_id: str):
    """Get honeypot configuration."""
    # Return mock configuration for now
    return HoneypotConfig(
        monitoring_sensitivity="medium",
        protection_type="ecdsa",
        auto_response=True,
        routing_method="classical"
    )


@router.put("/settings")
async def update_system_settings(settings: SystemSettings):
    """Update system settings."""
    # In a real implementation, this would update the database/config
    # For now, just acknowledge the update
    return {"message": "System settings updated successfully"}


@router.get("/settings", response_model=SystemSettings)
async def get_system_settings():
    """Get current system settings."""
    # Return mock settings for now
    return SystemSettings(
        email_alerts=True,
        push_notifications=False,
        threat_threshold="medium",
        auto_response=True,
        monitoring_interval=5,
        retention_period=30
    )


@router.post("/honeypots/deploy")
async def deploy_honeypot(request: DeployHoneypotRequest):
    """Deploy a new honeypot with the specified configuration."""
    # Generate new honeypot ID - find the next available number
    existing_ids = list(honeypot_configs.keys())
    existing_nums = []
    for honeypot_id in existing_ids:
        try:
            num = int(honeypot_id.split('_')[1])
            existing_nums.append(num)
        except (IndexError, ValueError):
            continue
    
    # Find the next available number
    new_id_num = 0
    while new_id_num in existing_nums:
        new_id_num += 1
    
    new_honeypot_id = f"honeypot_{new_id_num}"

    # Store the configuration
    honeypot_configs[new_honeypot_id] = {
        "name": request.name,
        "monitoring_sensitivity": request.monitoring_sensitivity,
        "protection_type": request.protection_type,
        "auto_response": request.auto_response,
        "routing_method": "classical",
        "blockchain": request.blockchain,
        "description": request.description or "",
        "interaction_count": 0,
        "last_interaction": None,
        "threat_indicators": []
    }

    # In a real implementation, this would:
    # 1. Provision infrastructure on the specified blockchain
    # 2. Deploy smart contracts or monitoring services
    # 3. Configure network routing and security policies
    # 4. Initialize threat detection algorithms
    # 5. Set up logging and alerting systems

    # For now, we'll just acknowledge the deployment
    return {
        "message": f"Honeypot '{request.name}' deployed successfully",
        "honeypot_id": new_honeypot_id,
        "blockchain": request.blockchain,
        "protection_type": request.protection_type,
        "status": "active"
    }


@router.post("/honeypots/{honeypot_id}/interactions")
async def record_interaction(honeypot_id: str, interaction: RecordInteractionRequest):
    """Record a new interaction with a honeypot."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    
    # Generate interaction ID
    interaction_id = f"int_{len(honeypot_interactions)}_{honeypot_id}"
    
    # Determine if auto-response should be triggered
    honeypot_config = honeypot_configs[honeypot_id]
    auto_responded = False
    
    if honeypot_config.get("auto_response", False):
        # Trigger auto-response for high/critical threats
        if interaction.threat_level in ["high", "critical"]:
            auto_responded = True
            # In real implementation, this would trigger defensive actions
    
    # Create interaction record
    new_interaction = HoneypotInteraction(
        id=interaction_id,
        honeypot_id=honeypot_id,
        interaction_type=interaction.interaction_type,
        source_ip=interaction.source_ip,
        source_address=interaction.source_address,
        amount=interaction.amount,
        details=interaction.details,
        timestamp=datetime.utcnow(),
        threat_level=interaction.threat_level,
        auto_responded=auto_responded
    )
    
    # Store the interaction
    honeypot_interactions.append(new_interaction.dict())
    
    # Update honeypot statistics
    honeypot_configs[honeypot_id]["interaction_count"] += 1
    honeypot_configs[honeypot_id]["last_interaction"] = datetime.utcnow()
    
    # Update threat indicators if this is a suspicious activity
    if interaction.threat_level in ["high", "critical"]:
        threat_indicators = honeypot_configs[honeypot_id].get("threat_indicators", [])
        if interaction.interaction_type not in threat_indicators:
            threat_indicators.append(interaction.interaction_type)
            honeypot_configs[honeypot_id]["threat_indicators"] = threat_indicators
    
    return {
        "message": "Interaction recorded successfully",
        "interaction_id": interaction_id,
        "auto_responded": auto_responded
    }


@router.get("/honeypots/{honeypot_id}/interactions", response_model=list[HoneypotInteraction])
async def get_honeypot_interactions(honeypot_id: str, limit: int = 50, offset: int = 0):
    """Get interactions for a specific honeypot."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    
    # Filter interactions for this honeypot
    honeypot_specific_interactions = [
        interaction for interaction in honeypot_interactions 
        if interaction["honeypot_id"] == honeypot_id
    ]
    
    # Sort by timestamp (newest first) and apply pagination
    sorted_interactions = sorted(
        honeypot_specific_interactions, 
        key=lambda x: x["timestamp"], 
        reverse=True
    )[offset:offset + limit]
    
    return [HoneypotInteraction(**interaction) for interaction in sorted_interactions]


@router.get("/interactions", response_model=list[HoneypotInteraction])
async def get_all_interactions(limit: int = 100, offset: int = 0):
    """Get all honeypot interactions across the system."""
    # Sort by timestamp (newest first) and apply pagination
    sorted_interactions = sorted(
        honeypot_interactions, 
        key=lambda x: x["timestamp"], 
        reverse=True
    )[offset:offset + limit]
    
    return [HoneypotInteraction(**interaction) for interaction in sorted_interactions]


@router.post("/honeypots/{honeypot_id}/simulate-interaction")
async def simulate_honeypot_interaction(honeypot_id: str):
    """Simulate a random interaction for testing purposes."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    
    import random
    
    # Generate random interaction data
    interaction_types = ["connection_attempt", "transaction", "scan", "probe", "suspicious_activity"]
    threat_levels = ["low", "medium", "high", "critical"]
    
    simulated_interaction = RecordInteractionRequest(
        interaction_type=random.choice(interaction_types),
        source_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
        source_address=f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
        amount=random.uniform(0.01, 100.0),
        details={
            "user_agent": "Suspicious Bot 1.0",
            "port": random.randint(1000, 9999),
            "protocol": random.choice(["HTTP", "HTTPS", "TCP", "UDP"])
        },
        threat_level=random.choice(threat_levels)
    )
    
    # Record the simulated interaction
    return await record_interaction(honeypot_id, simulated_interaction)
