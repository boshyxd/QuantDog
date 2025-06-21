from fastapi import APIRouter, HTTPException, Depends
from typing import List
import asyncio
from datetime import datetime

from api.models import (
    ThreatStatus, Transaction, SimulateAttackRequest,
    ReduceThreatRequest, HoneypotData, SystemMetrics,
    CryptoMethod, ThreatLevel
)
from core.threat_detector import ThreatDetector
from core.router import CryptoRouter
from core.monitoring import ThreatMonitor
from services.blockchain import BlockchainService
from utils.config import get_settings

router = APIRouter()
settings = get_settings()

# Initialize services
threat_detector = ThreatDetector()
crypto_router = CryptoRouter()
blockchain_service = BlockchainService()


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


@router.get("/transactions", response_model=List[Transaction])
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


@router.get("/honeypots", response_model=List[HoneypotData])
async def get_honeypots():
    """Get status of all honeypot systems."""
    # Load honeypot data (would normally be from a database)
    honeypots = []
    for i in range(3):
        honeypots.append(HoneypotData(
            id=f"honeypot_{i}",
            name=f"Quantum Honeypot {i+1}",
            status="active" if i < 2 else "triggered",
            last_interaction=datetime.utcnow() if i == 2 else None,
            interaction_count=i * 5,
            threat_indicators=["unusual_pattern"] if i == 2 else []
        ))
    
    return honeypots


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics():
    """Get current system performance metrics."""
    import psutil
    import time
    
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