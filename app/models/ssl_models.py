from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class SSLCertificate(BaseModel):
    """SSL Certificate Information"""
    domain: str
    isValid: bool
    issuer: str
    subject: str
    notBefore: datetime
    notAfter: datetime
    daysUntilExpiry: int
    isExpired: bool
    isExpiringSoon: bool
    keySize: int
    signatureAlgorithm: str
    sanList: List[str] = []
    serialNumber: str

class SSLCheckResult(BaseModel):
    """SSL Check Result"""
    domain: str
    success: bool
    certificate: Optional[SSLCertificate] = None
    error: Optional[str] = None
    checkedAt: datetime = Field(default_factory=datetime.utcnow)
    warnings: List[str] = []
