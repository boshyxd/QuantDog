from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ThreatLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CryptoMethod(str, Enum):
    CLASSICAL = "classical"
    POST_QUANTUM = "post_quantum"


class ThreatStatus(BaseModel):
    threat_level: float = Field(..., ge=0, le=100, description="Current threat level (0-100)")
    status: ThreatLevel
    active_crypto: CryptoMethod
    threshold: float
    timestamp: datetime
    message: str


class Transaction(BaseModel):
    id: str
    amount: float = Field(..., gt=0)
    from_address: str
    to_address: str
    timestamp: datetime
    crypto_method: CryptoMethod
    threat_level_at_time: float


class SimulateAttackRequest(BaseModel):
    intensity: float = Field(50.0, ge=0, le=100, description="Attack intensity")
    duration: Optional[int] = Field(None, description="Duration in seconds")


class ReduceThreatRequest(BaseModel):
    amount: float = Field(10.0, ge=0, le=100, description="Amount to reduce threat by")


class HoneypotData(BaseModel):
    id: str
    name: str
    status: str
    last_interaction: Optional[datetime]
    interaction_count: int
    threat_indicators: List[str]


class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    active_connections: int
    processed_transactions: int
    threats_detected: int
    uptime_seconds: float


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)