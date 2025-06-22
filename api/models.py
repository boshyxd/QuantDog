from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


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
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: str
    name: str
    status: str
    last_interaction: Optional[datetime]
    interaction_count: int
    threat_indicators: list[str]
    protection_type: Optional[str] = None
    monitoring_sensitivity: Optional[str] = None
    blockchain: Optional[str] = None
    description: Optional[str] = None
    starred: bool = False
    activated_at: Optional[datetime] = None
    wallet_address: Optional[str] = None
    current_balance: Optional[float] = None
    initial_balance: Optional[float] = None


class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    active_connections: int
    processed_transactions: int
    threats_detected: int
    uptime_seconds: float


class WebSocketMessage(BaseModel):
    type: str
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HoneypotConfig(BaseModel):
    monitoring_sensitivity: str = Field(..., pattern="^(low|medium|high)$")
    protection_type: str = Field(..., pattern="^(rsa|ecdsa)$")
    auto_response: bool
    routing_method: str = Field(..., pattern="^(classical|post_quantum)$")


class SystemSettings(BaseModel):
    email_alerts: bool
    push_notifications: bool
    threat_threshold: str = Field(..., pattern="^(low|medium|high)$")
    auto_response: bool
    monitoring_interval: int = Field(..., ge=1, le=3600)
    retention_period: int = Field(..., ge=1, le=365)


class DeployHoneypotRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    blockchain: str = Field(..., pattern="^(ethereum|bitcoin|quantum)$")
    protection_type: str = Field(..., pattern="^(rsa|ecdsa)$")
    monitoring_sensitivity: str = Field(..., pattern="^(low|medium|high)$")
    auto_response: bool = True
    description: Optional[str] = Field(None, max_length=500)


class HoneypotInteraction(BaseModel):
    id: str
    honeypot_id: str
    interaction_type: str = Field(..., pattern="^(connection_attempt|transaction|scan|probe|suspicious_activity)$")
    source_ip: str
    source_address: Optional[str] = None
    amount: Optional[float] = None
    details: dict[str, Any] = {}
    timestamp: datetime
    threat_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    auto_responded: bool = False


class RecordInteractionRequest(BaseModel):
    interaction_type: str = Field(..., pattern="^(connection_attempt|transaction|scan|probe|suspicious_activity)$")
    source_ip: str = Field(..., min_length=7, max_length=45)  # IPv4 and IPv6 support
    source_address: Optional[str] = None
    amount: Optional[float] = Field(None, ge=0)
    details: dict[str, Any] = {}
    threat_level: str = Field("medium", pattern="^(low|medium|high|critical)$")
