"""
Cryptographic Handler - Kriptografik Ä°ÅŸlemler
Mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼ ve kimlik doÄŸrulama iÃ§in kriptografik fonksiyonlar
"""

import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


class CryptoHandler:
    """
    Kriptografik iÅŸlemler iÃ§in handler
    - HMAC ile mesaj bÃ¼tÃ¼nlÃ¼ÄŸÃ¼
    - RSA ile dijital imza
    - Zaman damgasÄ± doÄŸrulama
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Args:
            secret_key: HMAC iÃ§in paylaÅŸÄ±lan gizli anahtar
        """
        # HMAC iÃ§in paylaÅŸÄ±lan anahtar
        self.secret_key = secret_key or "shared-secret-key-ev-charging-2025"
        
        # RSA anahtar Ã§ifti oluÅŸtur
        self.private_key = None
        self.public_key = None
        self._generate_rsa_keys()
        
        # Zaman damgasÄ± toleransÄ± (saniye)
        self.timestamp_tolerance = 60  # 60 saniye
        
    def _generate_rsa_keys(self):
        """RSA anahtar Ã§ifti oluÅŸtur"""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
    
    def calculate_hmac(self, message: Dict) -> str:
        """
        Mesaj iÃ§in HMAC-SHA256 hesapla
        
        Args:
            message: OCPP mesajÄ±
            
        Returns:
            HMAC deÄŸeri (hex string)
        """
        # MesajÄ± JSON string'e Ã§evir (sÄ±ralÄ±)
        message_str = json.dumps(message, sort_keys=True)
        message_bytes = message_str.encode('utf-8')
        
        # HMAC hesapla
        h = hmac.new(
            self.secret_key.encode('utf-8'),
            message_bytes,
            hashlib.sha256
        )
        
        return h.hexdigest()
    
    def verify_hmac(self, message: Dict, received_hmac: str) -> bool:
        """
        HMAC doÄŸrulamasÄ± yap
        
        Args:
            message: OCPP mesajÄ±
            received_hmac: AlÄ±nan HMAC deÄŸeri
            
        Returns:
            DoÄŸrulama sonucu
        """
        calculated_hmac = self.calculate_hmac(message)
        return hmac.compare_digest(calculated_hmac, received_hmac)
    
    def sign_message(self, message: Dict) -> bytes:
        """
        MesajÄ± RSA ile dijital olarak imzala
        
        Args:
            message: OCPP mesajÄ±
            
        Returns:
            Dijital imza (bytes)
        """
        # MesajÄ± JSON string'e Ã§evir
        message_str = json.dumps(message, sort_keys=True)
        message_bytes = message_str.encode('utf-8')
        
        # RSA imza oluÅŸtur
        signature = self.private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_signature(self, message: Dict, signature: bytes, public_key=None) -> bool:
        """
        Dijital imzayÄ± doÄŸrula
        
        Args:
            message: OCPP mesajÄ±
            signature: Dijital imza
            public_key: Public key (None ise kendi public key'i kullan)
            
        Returns:
            DoÄŸrulama sonucu
        """
        if public_key is None:
            public_key = self.public_key
        
        # MesajÄ± JSON string'e Ã§evir
        message_str = json.dumps(message, sort_keys=True)
        message_bytes = message_str.encode('utf-8')
        
        try:
            public_key.verify(
                signature,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def add_security_fields(self, message: Dict, use_hmac: bool = True, 
                           use_signature: bool = True) -> Dict:
        """
        Mesaja gÃ¼venlik alanlarÄ± ekle
        
        Args:
            message: Orijinal mesaj
            use_hmac: HMAC ekle
            use_signature: Dijital imza ekle
            
        Returns:
            GÃ¼venli mesaj
        """
        secure_message = message.copy()
        
        # Zaman damgasÄ± ekle (yoksa)
        if "timestamp" not in secure_message:
            secure_message["timestamp"] = datetime.now().isoformat()
        
        # Nonce ekle (replay attack korumasÄ±)
        secure_message["nonce"] = hashlib.sha256(
            f"{secure_message['timestamp']}{id(message)}".encode()
        ).hexdigest()[:16]
        
        # HMAC ekle
        if use_hmac:
            # HMAC hesaplarken security alanlarÄ±nÄ± hariÃ§ tut
            msg_for_hmac = {k: v for k, v in secure_message.items() 
                           if k not in ['hmac', 'signature']}
            secure_message["hmac"] = self.calculate_hmac(msg_for_hmac)
        
        # Dijital imza ekle
        if use_signature:
            # Ä°mza hesaplarken security alanlarÄ±nÄ± hariÃ§ tut
            msg_for_signature = {k: v for k, v in secure_message.items() 
                                if k not in ['hmac', 'signature']}
            signature_bytes = self.sign_message(msg_for_signature)
            # Bytes'Ä± hex string'e Ã§evir
            secure_message["signature"] = signature_bytes.hex()
        
        return secure_message
    
    def verify_message_security(self, message: Dict, check_timestamp: bool = True) -> Dict:
        """
        MesajÄ±n gÃ¼venlik doÄŸrulamasÄ±nÄ± yap
        
        Args:
            message: GÃ¼venli mesaj
            check_timestamp: Zaman damgasÄ± kontrolÃ¼ yap
            
        Returns:
            DoÄŸrulama sonuÃ§larÄ±
        """
        result = {
            "valid": True,
            "checks": {},
            "errors": []
        }
        
        # Zaman damgasÄ± kontrolÃ¼
        if check_timestamp and "timestamp" in message:
            try:
                msg_time = datetime.fromisoformat(message["timestamp"])
                now = datetime.now()
                time_diff = abs((now - msg_time).total_seconds())
                
                if time_diff > self.timestamp_tolerance:
                    result["valid"] = False
                    result["errors"].append(
                        f"Timestamp out of range: {time_diff}s (max: {self.timestamp_tolerance}s)"
                    )
                    result["checks"]["timestamp"] = False
                else:
                    result["checks"]["timestamp"] = True
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Invalid timestamp format: {e}")
                result["checks"]["timestamp"] = False
        
        # HMAC kontrolÃ¼
        if "hmac" in message:
            received_hmac = message["hmac"]
            msg_for_hmac = {k: v for k, v in message.items() 
                           if k not in ['hmac', 'signature']}
            
            if self.verify_hmac(msg_for_hmac, received_hmac):
                result["checks"]["hmac"] = True
            else:
                result["valid"] = False
                result["errors"].append("HMAC verification failed")
                result["checks"]["hmac"] = False
        
        # Dijital imza kontrolÃ¼
        if "signature" in message:
            try:
                signature_bytes = bytes.fromhex(message["signature"])
                msg_for_signature = {k: v for k, v in message.items() 
                                    if k not in ['hmac', 'signature']}
                
                if self.verify_signature(msg_for_signature, signature_bytes):
                    result["checks"]["signature"] = True
                else:
                    result["valid"] = False
                    result["errors"].append("Digital signature verification failed")
                    result["checks"]["signature"] = False
            except Exception as e:
                result["valid"] = False
                result["errors"].append(f"Signature verification error: {e}")
                result["checks"]["signature"] = False
        
        return result
    
    def export_public_key(self) -> bytes:
        """Public key'i export et"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def import_public_key(self, pem_bytes: bytes):
        """Public key'i import et"""
        return serialization.load_pem_public_key(
            pem_bytes,
            backend=default_backend()
        )


if __name__ == "__main__":
    print("=== Cryptographic Handler Test ===\n")
    
    # Crypto handler oluÅŸtur
    crypto = CryptoHandler(secret_key="test-secret-key-123")
    
    # Test mesajÄ±
    test_message = {
        "message_type": "StatusNotification",
        "vehicle_id": "EV-12345",
        "battery_data": {
            "soc": 85.0,
            "voltage": 380.5,
            "temperature": 35.2
        }
    }
    
    print("Original Message:")
    print(json.dumps(test_message, indent=2))
    
    # GÃ¼venli mesaj oluÅŸtur
    print("\n1. Adding security fields...")
    secure_message = crypto.add_security_fields(test_message)
    print(f"   âœ… HMAC: {secure_message['hmac'][:32]}...")
    print(f"   âœ… Signature: {secure_message['signature'][:32]}...")
    print(f"   âœ… Nonce: {secure_message['nonce']}")
    
    # DoÄŸrulama
    print("\n2. Verifying security...")
    verification = crypto.verify_message_security(secure_message)
    print(f"   Valid: {verification['valid']}")
    print(f"   Checks: {verification['checks']}")
    
    # ManipÃ¼lasyon testi
    print("\n3. Testing manipulation detection...")
    manipulated_message = secure_message.copy()
    manipulated_message["battery_data"] = {
        "soc": 30.0,  # ManipÃ¼le edilmiÅŸ deÄŸer
        "voltage": 380.5,
        "temperature": 35.2
    }
    
    verification = crypto.verify_message_security(manipulated_message)
    print(f"   Valid: {verification['valid']}")
    print(f"   Errors: {verification['errors']}")
    
    if not verification['valid']:
        print("   âœ… Manipulation detected successfully!")
    
    # Replay attack testi
    print("\n4. Testing replay attack detection...")
    import time
    old_message = secure_message.copy()
    old_message["timestamp"] = (
        datetime.now() - timedelta(seconds=120)
    ).isoformat()
    
    # Yeni HMAC hesapla
    msg_for_hmac = {k: v for k, v in old_message.items() 
                   if k not in ['hmac', 'signature']}
    old_message["hmac"] = crypto.calculate_hmac(msg_for_hmac)
    
    verification = crypto.verify_message_security(old_message)
    print(f"   Valid: {verification['valid']}")
    print(f"   Errors: {verification['errors']}")
    
    if not verification['valid']:
        print("   âœ… Replay attack detected successfully!")
