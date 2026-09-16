"""
pqcrypto.py —— 抗量子密码核心模块

提供两类 NIST 标准抗量子算法：
1. ML-KEM-768（原 Kyber768）：密钥封装，用于安全加密机密信息
2. ML-DSA-65（原 Dilithium3）：数字签名，用于防止文件被篡改

自动适配两种底层库（用户无需关心）：
- 优先使用 liboqs（NIST 标准实现）
- 若安装失败，自动改用 pqcrypto 轻量库
"""

try:
    import oqs  # 首选：liboqs 库
    BACKEND = "liboqs"
except ImportError:
    # 备选：pqcrypto 库
    BACKEND = "pqcrypto"
    from pqcrypto.kem import ml_kem_768
    from pqcrypto.sign import ml_dsa_65


class KEM:
    """ML-KEM-768 密钥封装：用于给机密信息加密（抗量子）"""

    @staticmethod
    def generate_keypair():
        """生成一套密钥对，返回 (公钥, 私钥)"""
        if BACKEND == "liboqs":
            kem = oqs.KeyEncapsulation("ML-KEM-768")
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
            return public_key, secret_key
        return ml_kem_768.keygen()

    @staticmethod
    def encaps(public_key):
        """封装：拿公钥把机密信息装进'抗量子信封'，返回 (密文, 共享密钥)"""
        if BACKEND == "liboqs":
            kem = oqs.KeyEncapsulation("ML-KEM-768")
            ciphertext, shared_secret = kem.encap_secret(public_key)
            return ciphertext, shared_secret
        return ml_kem_768.encaps(public_key)

    @staticmethod
    def decaps(ciphertext, secret_key):
        """拆封：拿私钥打开信封，还原出同一个共享密钥"""
        if BACKEND == "liboqs":
            kem = oqs.KeyEncapsulation("ML-KEM-768")
            kem.secret_key = secret_key
            return kem.decap_secret(ciphertext)
        return ml_kem_768.decaps(secret_key, ciphertext)


class DSA:
    """ML-DSA-65 数字签名：用于证明文件/消息没被篡改（抗量子）"""

    @staticmethod
    def generate_keypair():
        """生成一套签名密钥对，返回 (公钥, 私钥)"""
        if BACKEND == "liboqs":
            sig = oqs.Signature("ML-DSA-65")
            public_key = sig.generate_keypair()
            secret_key = sig.export_secret_key()
            return public_key, secret_key
        return ml_dsa_65.keygen()

    @staticmethod
    def sign(message, secret_key):
        """对消息签名，返回签名结果"""
        if BACKEND == "liboqs":
            sig = oqs.Signature("ML-DSA-65")
            sig.secret_key = secret_key
            return sig.sign(message)
        return ml_dsa_65.sign(secret_key, message)

    @staticmethod
    def verify(message, signature, public_key):
        """验证签名，签名有效返回 True，被篡改返回 False"""
        if BACKEND == "liboqs":
            sig = oqs.Signature("ML-DSA-65")
            return sig.verify(message, signature, public_key)
        try:
            ml_dsa_65.verify(public_key, message, signature)
            return True  # pqcrypto 后端：成功返回 None，失败抛异常
        except Exception:
            return False
