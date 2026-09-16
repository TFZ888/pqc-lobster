"""抗量子密码模块的自动化测试"""

from pqclaw import pqcrypto


def test_kem_roundtrip():
    """密钥封装：加密后能正确解密还原"""
    pub, sec = pqcrypto.KEM.generate_keypair()
    ciphertext, shared_a = pqcrypto.KEM.encaps(pub)
    shared_b = pqcrypto.KEM.decaps(ciphertext, sec)
    assert shared_a == shared_b, "双方共享密钥不一致"


def test_dsa_sign_verify():
    """签名验证：正常文件验签通过"""
    spub, ssec = pqcrypto.DSA.generate_keypair()
    message = b"hello anti-quantum lobster"
    signature = pqcrypto.DSA.sign(message, ssec)
    assert pqcrypto.DSA.verify(message, signature, spub) is True


def test_dsa_tamper_detected():
    """篡改检测：文件被改动后验签必须失败"""
    spub, ssec = pqcrypto.DSA.generate_keypair()
    message = b"important config"
    signature = pqcrypto.DSA.sign(message, ssec)
    tampered = b"important confiX"
    assert pqcrypto.DSA.verify(tampered, signature, spub) is False
