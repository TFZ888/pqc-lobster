"""
keystore.py —— 抗量子密钥保险箱

作用：把 DeepSeek API Key 等机密信息，用抗量子算法加密后存到磁盘，
防止明文泄露。即使文件被偷走，没有抗量子私钥也解不开。

工作流程：
1. init  ：生成一套 ML-KEM 抗量子密钥对，保存在 ~/.pqclaw/ 目录
2. seal  ：用公钥把机密信息加密成密文（存盘的是密文，不是明文）
3. open  ：用私钥解密密文，还原出机密信息
4. sign  ：用 ML-DSA 给配置文件签名（防篡改）
5. verify：验证配置文件签名是否有效
"""

import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from . import pqcrypto

# 安全目录：存放抗量子密钥和密文
CONFIG_DIR = Path.home() / ".pqclaw"
KEM_PUBLIC_FILE = CONFIG_DIR / "kem_public.key"   # 抗量子公钥
KEM_SECRET_FILE = CONFIG_DIR / "kem_secret.key"   # 抗量子私钥（权限 600）
SEALED_FILE = CONFIG_DIR / "api_key.sealed"       # 加密后的机密信息
SIGN_PUBLIC_FILE = CONFIG_DIR / "dsa_public.key"  # 签名公钥
SIGN_SECRET_FILE = CONFIG_DIR / "dsa_secret.key"  # 签名私钥（权限 600）


def init() -> None:
    """第一步：初始化安全目录，生成抗量子密钥对"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # 生成 ML-KEM 密钥封装密钥对
    pub, sec = pqcrypto.KEM.generate_keypair()
    KEM_PUBLIC_FILE.write_bytes(pub)
    KEM_SECRET_FILE.write_bytes(sec)
    os.chmod(KEM_SECRET_FILE, 0o600)

    # 生成 ML-DSA 签名密钥对
    spub, ssec = pqcrypto.DSA.generate_keypair()
    SIGN_PUBLIC_FILE.write_bytes(spub)
    SIGN_SECRET_FILE.write_bytes(ssec)
    os.chmod(SIGN_SECRET_FILE, 0o600)

    print(f"✅ 已初始化抗量子安全目录：{CONFIG_DIR}")


def seal(secret: bytes, output_file: Path = SEALED_FILE) -> Path:
    """第二步：加密机密信息（API Key），保存为密文文件"""
    if not KEM_PUBLIC_FILE.exists():
        raise RuntimeError("还没有初始化，请先运行: pqclaw init")

    public_key = KEM_PUBLIC_FILE.read_bytes()
    ciphertext, shared_secret = pqcrypto.KEM.encaps(public_key)

    # 用抗量子共享密钥做 AES-GCM 加密（密文 = 信封 + 随机数 + 加密数据）
    nonce = os.urandom(12)
    encrypted = AESGCM(shared_secret).encrypt(nonce, secret, None)
    packed = len(ciphertext).to_bytes(2, "big") + ciphertext + nonce + encrypted

    output_file.write_bytes(packed)
    os.chmod(output_file, 0o600)
    print(f"✅ 机密信息已加密保存：{output_file}（磁盘上不是明文）")
    return output_file


def open_sealed(sealed_file: Path = SEALED_FILE) -> bytes:
    """第三步：解密机密信息，还原出明文（只在本机、用抗量子私钥）"""
    if not KEM_SECRET_FILE.exists():
        raise RuntimeError("还没有初始化，请先运行: pqclaw init")

    packed = sealed_file.read_bytes()
    size = int.from_bytes(packed[:2], "big")
    ciphertext = packed[2 : 2 + size]
    nonce = packed[2 + size : 2 + size + 12]
    encrypted = packed[2 + size + 12 :]

    secret_key = KEM_SECRET_FILE.read_bytes()
    shared_secret = pqcrypto.KEM.decaps(ciphertext, secret_key)
    return AESGCM(shared_secret).decrypt(nonce, encrypted, None)


def sign_file(file_path: Path, sig_path: Path) -> None:
    """给文件签名（防篡改），签名保存到 sig_path"""
    if not SIGN_SECRET_FILE.exists():
        raise RuntimeError("还没有初始化，请先运行: pqclaw init")
    data = file_path.read_bytes()
    secret_key = SIGN_SECRET_FILE.read_bytes()
    signature = pqcrypto.DSA.sign(data, secret_key)
    sig_path.write_bytes(signature)
    print(f"✅ 已生成签名：{sig_path}")


def verify_file(file_path: Path, sig_path: Path) -> bool:
    """验证文件签名是否有效"""
    if not SIGN_PUBLIC_FILE.exists():
        raise RuntimeError("还没有初始化，请先运行: pqclaw init")
    data = file_path.read_bytes()
    signature = sig_path.read_bytes()
    public_key = SIGN_PUBLIC_FILE.read_bytes()
    return pqcrypto.DSA.verify(data, signature, public_key)
