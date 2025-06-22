import asyncio
import logging
from datetime import datetime
import random
from typing import Optional

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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
threat_detector = ThreatDetector()
crypto_router = CryptoRouter()
blockchain_service = BlockchainService()

# Balance check task
balance_check_task: Optional[asyncio.Task] = None

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
        "threat_indicators": [],
        "starred": False,
        "created_at": datetime.utcnow(),
        "activated_at": datetime.utcnow(),
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f8b7d2",
        "initial_balance": 1.0,
        "current_balance": 1.0,
        "status": "active"
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
        "threat_indicators": [],
        "starred": False,
        "created_at": datetime.utcnow(),
        "activated_at": datetime.utcnow(),
        "wallet_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
        "initial_balance": 0.01,
        "current_balance": 0.01,
        "status": "active"
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
        "threat_indicators": [],
        "starred": False,
        "created_at": datetime.utcnow(),
        "activated_at": datetime.utcnow(),
        "wallet_address": "0x1234567890123456789012345678901234567890",
        "initial_balance": 100.0,
        "current_balance": 100.0,
        "status": "active"
    }
}

# Track disabled honeypots
disabled_honeypots = set()

# In-memory storage for honeypot interactions
honeypot_interactions = []


async def check_honeypot_balances():
    """Periodically check honeypot wallet balances and detect if funds were drained."""
    logger.info("🚀 Starting honeypot balance monitoring task...")
    check_count = 0
    
    while True:
        try:
            check_count += 1
            active_honeypots = 0
            triggered_honeypots = 0
            total_balance = 0
            
            for honeypot_id, config in honeypot_configs.items():
                if config.get("wallet_address"):
                    current_balance = config.get("current_balance", 0)
                    total_balance += current_balance
                    
                    if config.get("status") == "active":
                        active_honeypots += 1
                    elif config.get("status") == "triggered":
                        triggered_honeypots += 1
            
            # Every 5 minutes (10 checks), log a status report
            if check_count % 10 == 0:
                total_interactions = sum(config.get("interaction_count", 0) for config in honeypot_configs.values())
                print(f"\n📊 HONEYPOT SYSTEM STATUS REPORT (Check #{check_count}):")
                print(f"   🟢 Active honeypots: {active_honeypots}")
                print(f"   🔴 Triggered honeypots: {triggered_honeypots}")
                print(f"   💰 Total balance: {total_balance:.4f}")
                print(f"   📈 Total interactions: {total_interactions}")
                print(f"   ⏰ Next check in 30 seconds\n")
                
            # Now check for balance drains
            for honeypot_id, config in honeypot_configs.items():
                if config.get("status") == "active" and config.get("wallet_address"):
                    current_balance = config.get("current_balance", 0)
                    wallet_address = config.get("wallet_address", "unknown")
                    
                    # Log balance check (every 10th check to avoid spam)
                    if random.random() < 0.1:
                        logger.info(f"💰 Checking balance for {honeypot_id} ({wallet_address[:10]}...): {current_balance}")
                    
                    # 5% chance of being drained per check (adjust this for demo purposes)
                    if random.random() < 0.05 and current_balance > 0:
                        # Honeypot was drained!
                        previous_balance = current_balance
                        config["current_balance"] = 0
                        config["status"] = "triggered"
                        config["last_interaction"] = datetime.utcnow()
                        
                        # Record the drain as an interaction
                        interaction_id = f"int_{len(honeypot_interactions)}_{honeypot_id}"
                        drain_interaction = {
                            "id": interaction_id,
                            "honeypot_id": honeypot_id,
                            "interaction_type": "funds_drained",
                            "source_ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                            "source_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                            "amount": previous_balance,
                            "details": {
                                "message": "Honeypot funds were drained by malicious actor",
                                "previous_balance": previous_balance,
                                "new_balance": 0,
                                "blockchain": config.get("blockchain", "unknown"),
                                "wallet_address": wallet_address
                            },
                            "timestamp": datetime.utcnow(),
                            "threat_level": "critical",
                            "auto_responded": config.get("auto_response", False)
                        }
                        honeypot_interactions.append(drain_interaction)
                        config["interaction_count"] += 1
                        
                        # Add to threat indicators if not already there
                        if "funds_drained" not in config.get("threat_indicators", []):
                            config["threat_indicators"].append("funds_drained")
                        
                        # Multiple alert methods to ensure visibility
                        alert_msg = f"🚨 CRITICAL ALERT: Honeypot {honeypot_id} ({config.get('name', 'Unknown')}) COMPROMISED!"
                        balance_msg = f"💸 Funds drained: {previous_balance} {config.get('blockchain', 'tokens')} from {wallet_address}"
                        
                        logger.error(alert_msg)
                        logger.error(balance_msg)
                        print(f"\n{'='*80}")
                        print(alert_msg)
                        print(balance_msg)
                        print(f"Threat level: CRITICAL | Auto-response: {config.get('auto_response', False)}")
                        print(f"{'='*80}\n")
            
            # Check every 30 seconds
            await asyncio.sleep(30)
            
        except Exception as e:
            error_msg = f"❌ Error in balance check task: {e}"
            logger.error(error_msg)
            print(error_msg)
            await asyncio.sleep(60)  # Wait longer on error


# Functions to start and stop the balance checking task
async def start_honeypot_monitoring():
    """Start the honeypot balance monitoring task."""
    global balance_check_task
    balance_check_task = asyncio.create_task(check_honeypot_balances())
    startup_msg = "🌟 QuantDog Honeypot System STARTED - Background monitoring active"
    logger.info(startup_msg)
    print(f"\n{'='*80}")
    print(startup_msg)
    print(f"Active honeypots: {len(honeypot_configs)}")
    print(f"Check interval: 30 seconds")
    print(f"{'='*80}\n")
    return balance_check_task


async def stop_honeypot_monitoring():
    """Stop the honeypot balance monitoring task."""
    global balance_check_task
    if balance_check_task:
        balance_check_task.cancel()
        try:
            await balance_check_task
        except asyncio.CancelledError:
            pass
    shutdown_msg = "🛑 QuantDog Honeypot System STOPPED - Background monitoring disabled"
    logger.info(shutdown_msg)
    print(shutdown_msg)


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

        # Determine status based on whether honeypot is disabled or triggered
        if honeypot_id in disabled_honeypots:
            status = "disabled"
        else:
            # Use the actual status from config, default to active
            status = config.get("status", "active")

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
            description=config.get("description", ""),
            starred=config.get("starred", False),
            activated_at=config.get("activated_at"),
            wallet_address=config.get("wallet_address"),
            current_balance=config.get("current_balance"),
            initial_balance=config.get("initial_balance")
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


@router.post("/honeypots/{honeypot_id}/star")
async def toggle_honeypot_star(honeypot_id: str):
    """Toggle the starred status of a honeypot."""
    # Check if honeypot exists
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    
    # Toggle starred status
    current_starred = honeypot_configs[honeypot_id].get("starred", False)
    honeypot_configs[honeypot_id]["starred"] = not current_starred
    
    action = "starred" if not current_starred else "unstarred"
    logger.info(f"⭐ Honeypot {honeypot_id} ({honeypot_configs[honeypot_id].get('name', 'Unknown')}) {action}")
    
    return {
        "message": f"Honeypot {honeypot_id} {action}",
        "starred": not current_starred
    }


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
    logger.info(f"🚀 Deploying new honeypot: {request.name} on {request.blockchain}")
    
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

    # Generate wallet address based on blockchain
    import secrets
    if request.blockchain == "ethereum":
        wallet_address = f"0x{secrets.token_hex(20)}"
    elif request.blockchain == "bitcoin":
        wallet_address = f"bc1q{secrets.token_hex(16)[:32]}"
    else:  # quantum
        wallet_address = f"0x{secrets.token_hex(20)}"
    
    # Set initial balance based on blockchain
    initial_balance = 1.0 if request.blockchain == "ethereum" else 0.01 if request.blockchain == "bitcoin" else 100.0

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
        "threat_indicators": [],
        "starred": False,
        "created_at": datetime.utcnow(),
        "activated_at": datetime.utcnow(),
        "wallet_address": wallet_address,
        "initial_balance": initial_balance,
        "current_balance": initial_balance,
        "status": "active"
    }

    # In a real implementation, this would:
    # 1. Provision infrastructure on the specified blockchain
    # 2. Deploy smart contracts or monitoring services
    # 3. Configure network routing and security policies
    # 4. Initialize threat detection algorithms
    # 5. Set up logging and alerting systems

    # Log successful deployment
    logger.info(f"✅ Honeypot deployed successfully: {new_honeypot_id} ({request.name})")
    logger.info(f"📍 Wallet address: {wallet_address}")
    logger.info(f"💰 Initial balance: {initial_balance} {request.blockchain}")
    
    print(f"\n🎯 NEW HONEYPOT DEPLOYED:")
    print(f"   ID: {new_honeypot_id}")
    print(f"   Name: {request.name}")
    print(f"   Blockchain: {request.blockchain}")
    print(f"   Wallet: {wallet_address}")
    print(f"   Balance: {initial_balance}")
    print(f"   Protection: {request.protection_type}")
    print(f"   Status: ACTIVE\n")

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
    
    # Log the interaction
    honeypot_name = honeypot_configs[honeypot_id].get("name", "Unknown")
    logger.info(f"🔍 Interaction recorded for {honeypot_id} ({honeypot_name})")
    logger.info(f"   Type: {interaction.interaction_type}")
    logger.info(f"   Source: {interaction.source_ip}")
    logger.info(f"   Threat: {interaction.threat_level}")
    logger.info(f"   Auto-response: {auto_responded}")
    
    if interaction.threat_level in ["high", "critical"]:
        print(f"\n⚠️  HIGH THREAT INTERACTION DETECTED:")
        print(f"   Honeypot: {honeypot_name} ({honeypot_id})")
        print(f"   Type: {interaction.interaction_type}")
        print(f"   Source IP: {interaction.source_ip}")
        print(f"   Threat Level: {interaction.threat_level.upper()}")
        print(f"   Amount: {interaction.amount}")
        print(f"   Auto-responded: {auto_responded}\n")
    
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
    
    honeypot_name = honeypot_configs[honeypot_id].get("name", "Unknown")
    logger.info(f"🎲 Simulating interaction for {honeypot_id} ({honeypot_name})")
    
    import random
    
    # Generate random interaction data
    interaction_types = ["connection_attempt", "transaction", "scan", "probe", "suspicious_activity"]
    threat_levels = ["low", "medium", "high", "critical"]
    
    selected_type = random.choice(interaction_types)
    selected_threat = random.choice(threat_levels)
    
    simulated_interaction = RecordInteractionRequest(
        interaction_type=selected_type,
        source_ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
        source_address=f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
        amount=random.uniform(0.01, 100.0),
        details={
            "user_agent": "Suspicious Bot 1.0",
            "port": random.randint(1000, 9999),
            "protocol": random.choice(["HTTP", "HTTPS", "TCP", "UDP"]),
            "simulated": True
        },
        threat_level=selected_threat
    )
    
    print(f"🎭 SIMULATING INTERACTION:")
    print(f"   Honeypot: {honeypot_name} ({honeypot_id})")
    print(f"   Type: {selected_type}")
    print(f"   Threat: {selected_threat}")
    print(f"   Source: {simulated_interaction.source_ip}")
    
    # Record the simulated interaction
    return await record_interaction(honeypot_id, simulated_interaction)


@router.get("/debug/system-status")
async def get_system_debug_status():
    """Get detailed system status for debugging."""
    active_count = sum(1 for config in honeypot_configs.values() if config.get("status") == "active")
    triggered_count = sum(1 for config in honeypot_configs.values() if config.get("status") == "triggered")
    total_balance = sum(config.get("current_balance", 0) for config in honeypot_configs.values())
    total_interactions = sum(config.get("interaction_count", 0) for config in honeypot_configs.values())
    
    status = {
        "total_honeypots": len(honeypot_configs),
        "active_honeypots": active_count,
        "triggered_honeypots": triggered_count,
        "total_balance": total_balance,
        "total_interactions": total_interactions,
        "total_recorded_interactions": len(honeypot_interactions),
        "monitoring_active": balance_check_task is not None and not balance_check_task.done(),
        "honeypots": {
            honeypot_id: {
                "name": config.get("name"),
                "status": config.get("status"),
                "balance": config.get("current_balance"),
                "interactions": config.get("interaction_count", 0),
                "starred": config.get("starred", False),
                "wallet": config.get("wallet_address")
            }
            for honeypot_id, config in honeypot_configs.items()
        }
    }
    
    print(f"\n🔍 SYSTEM DEBUG STATUS:")
    print(f"   Total honeypots: {len(honeypot_configs)}")
    print(f"   Active: {active_count}, Triggered: {triggered_count}")
    print(f"   Total balance: {total_balance:.4f}")
    print(f"   Total interactions: {total_interactions}")
    print(f"   Monitoring task running: {status['monitoring_active']}")
    print()
    
    return status


@router.post("/debug/trigger-drain/{honeypot_id}")
async def trigger_manual_drain(honeypot_id: str):
    """Manually trigger a fund drain for testing purposes."""
    if honeypot_id not in honeypot_configs:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    
    config = honeypot_configs[honeypot_id]
    if config.get("status") != "active":
        raise HTTPException(status_code=400, detail="Honeypot is not active")
    
    current_balance = config.get("current_balance", 0)
    if current_balance <= 0:
        raise HTTPException(status_code=400, detail="Honeypot already has no balance")
    
    # Manually trigger drain
    previous_balance = current_balance
    config["current_balance"] = 0
    config["status"] = "triggered"
    config["last_interaction"] = datetime.utcnow()
    
    # Record the manual drain
    interaction_id = f"int_{len(honeypot_interactions)}_{honeypot_id}"
    drain_interaction = {
        "id": interaction_id,
        "honeypot_id": honeypot_id,
        "interaction_type": "manual_funds_drained",
        "source_ip": "127.0.0.1",
        "source_address": "manual_trigger",
        "amount": previous_balance,
        "details": {
            "message": "Manually triggered fund drain for testing",
            "previous_balance": previous_balance,
            "new_balance": 0,
            "manual": True
        },
        "timestamp": datetime.utcnow(),
        "threat_level": "critical",
        "auto_responded": config.get("auto_response", False)
    }
    honeypot_interactions.append(drain_interaction)
    config["interaction_count"] += 1
    
    if "funds_drained" not in config.get("threat_indicators", []):
        config["threat_indicators"].append("funds_drained")
    
    honeypot_name = config.get("name", "Unknown")
    alert_msg = f"🧪 MANUAL TEST: Honeypot {honeypot_id} ({honeypot_name}) DRAINED"
    
    logger.error(alert_msg)
    print(f"\n{'='*80}")
    print(alert_msg)
    print(f"💸 Amount drained: {previous_balance}")
    print(f"🔬 This was a manual test trigger")
    print(f"{'='*80}\n")
    
    return {
        "message": f"Successfully drained {previous_balance} from {honeypot_id}",
        "previous_balance": previous_balance,
        "honeypot_name": honeypot_name,
        "interaction_id": interaction_id
    }
