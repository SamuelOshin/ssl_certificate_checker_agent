import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from typing import Optional, List

from app.models.ssl_models import SSLCertificate, SSLCheckResult

class SSLCheckerService:
    """SSL Certificate Checking Service"""
    
    def __init__(self, timeout: int = 10, warning_days: int = 30):
        self.timeout = timeout
        self.warning_days = warning_days
    
    def check_certificate(self, domain: str, port: int = 443) -> SSLCheckResult:
        """Check SSL certificate for domain (synchronous)"""
        try:
            cert_der = self._get_certificate(domain, port)
            certificate = self._parse_certificate(cert_der, domain)
            warnings = self._generate_warnings(certificate)
            
            return SSLCheckResult(
                domain=domain,
                success=True,
                certificate=certificate,
                warnings=warnings
            )
        
        except socket.timeout:
            return SSLCheckResult(domain=domain, success=False, error="Connection timeout")
        except socket.gaierror:
            return SSLCheckResult(domain=domain, success=False, error="Domain not found (DNS error)")
        except ssl.SSLError as e:
            return SSLCheckResult(domain=domain, success=False, error=f"SSL error: {str(e)}")
        except Exception as e:
            return SSLCheckResult(domain=domain, success=False, error=f"Unexpected error: {str(e)}")
    
    async def check_domain(self, domain: str, port: int = 443) -> SSLCheckResult:
        """Async version for backward compatibility"""
        return self.check_certificate(domain, port)
        """Check SSL certificate for domain"""
        try:
            cert_der = self._get_certificate(domain, port)
            certificate = self._parse_certificate(cert_der, domain)
            warnings = self._generate_warnings(certificate)
            
            return SSLCheckResult(
                domain=domain,
                success=True,
                certificate=certificate,
                warnings=warnings
            )
        
        except socket.timeout:
            return SSLCheckResult(domain=domain, success=False, error="Connection timeout")
        except socket.gaierror:
            return SSLCheckResult(domain=domain, success=False, error="Domain not found (DNS error)")
        except ssl.SSLError as e:
            return SSLCheckResult(domain=domain, success=False, error=f"SSL error: {str(e)}")
        except Exception as e:
            return SSLCheckResult(domain=domain, success=False, error=f"Unexpected error: {str(e)}")
    
    def _get_certificate(self, domain: str, port: int) -> bytes:
        """Retrieve SSL certificate"""
        context = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.getpeercert(binary_form=True)
    
    def _parse_certificate(self, cert_der: bytes, domain: str) -> SSLCertificate:
        """Parse certificate data"""
        cert = x509.load_der_x509_certificate(cert_der, default_backend())
        
        # Extract issuer CN
        issuer_cn = "Unknown"
        for attr in cert.issuer:
            if attr.oid._name == "commonName":
                issuer_cn = attr.value
                break
        
        # Extract subject CN
        subject_cn = domain
        for attr in cert.subject:
            if attr.oid._name == "commonName":
                subject_cn = attr.value
                break
        
        # Dates
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc
        now = datetime.now(not_after.tzinfo)
        
        days_until_expiry = (not_after - now).days
        is_expired = now > not_after
        is_expiring_soon = 0 < days_until_expiry <= self.warning_days
        
        # Key info
        public_key = cert.public_key()
        key_size = public_key.key_size
        
        # SANs
        san_list = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            san_list = [dns.value for dns in san_ext.value if isinstance(dns, x509.DNSName)]
        except x509.ExtensionNotFound:
            pass
        
        return SSLCertificate(
            domain=domain,
            isValid=not is_expired,
            issuer=issuer_cn,
            subject=subject_cn,
            notBefore=not_before.replace(tzinfo=None),
            notAfter=not_after.replace(tzinfo=None),
            daysUntilExpiry=days_until_expiry,
            isExpired=is_expired,
            isExpiringSoon=is_expiring_soon,
            keySize=key_size,
            signatureAlgorithm=cert.signature_algorithm_oid._name,
            sanList=san_list,
            serialNumber=hex(cert.serial_number)[:16]
        )
    
    def _generate_warnings(self, cert: SSLCertificate) -> List[str]:
        """Generate warnings"""
        warnings = []
        
        if cert.isExpired:
            warnings.append(f"⚠️ Certificate EXPIRED {abs(cert.daysUntilExpiry)} days ago")
        elif cert.daysUntilExpiry <= 7:
            warnings.append(f"🚨 Certificate expires in {cert.daysUntilExpiry} days (CRITICAL)")
        elif cert.isExpiringSoon:
            warnings.append(f"⚠️ Certificate expires in {cert.daysUntilExpiry} days")
        
        if cert.keySize < 2048:
            warnings.append("⚠️ Weak key size (< 2048 bits)")
        
        return warnings
