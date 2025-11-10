from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils, ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import time
import base64


# --- Anahtar Yönetimi ---
def generate_key_pair():
    """ECDRSA anahtar çifti oluşturur (Hafif ve hızlıdır)."""
    private_key = ec.generate_private_key(
        ec.SECP256K1(),
        default_backend()
    )

    # 🛑 DÜZELTME: public_key değişkeni burada tanımlanmalıydı.
    public_key = private_key.public_key()
    # 🛑

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


# --- Mesaj İşlemleri ---
def calculate_hash(message: str) -> str:
    """Verilen mesajın hash'ini (zaman damgası dahil) hesaplar."""
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    # Zaman damgasını ekleyerek tekrar saldırısını (replay attack) önlüyoruz
    data_to_hash = f"{message}|{int(time.time())}".encode('utf-8')
    digest.update(data_to_hash)
    return digest.finalize().hex()


def sign_message(private_pem: str, data_to_sign: str) -> str:
    """Verilen veriyi gizli anahtar ile imzalar."""
    private_key = serialization.load_pem_private_key(
        private_pem.encode('utf-8'),
        password=None,
        backend=default_backend()
    )

    signature = private_key.sign(
        data_to_sign.encode('utf-8'),
        ec.ECDSA(hashes.SHA256())
    )
    return base64.b64encode(signature).decode('utf-8')


def verify_signature(public_pem: str, data_to_verify: str, signature_b64: str) -> bool:
    """Verilen verinin dijital imzasını açık anahtar ile doğrular."""
    public_key = serialization.load_pem_public_key(
        public_pem.encode('utf-8'),
        backend=default_backend()
    )
    signature = base64.b64decode(signature_b64.encode('utf-8'))

    try:
        public_key.verify(
            signature,
            data_to_verify.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
        return True
    except:
        return False