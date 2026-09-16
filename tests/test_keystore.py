"""密钥保险箱的自动化测试"""

from pqclaw import keystore
from pqclaw.keystore import CONFIG_DIR, SEALED_FILE, SIGN_PUBLIC_FILE, SIGN_SECRET_FILE


def _clean():
    import shutil
    if CONFIG_DIR.exists():
        shutil.rmtree(CONFIG_DIR)


def test_seal_open_roundtrip():
    """加密后能正确解密，且密文文件不含明文"""
    _clean()
    keystore.init()
    secret = b"sk-test-1234567890"
    keystore.seal(secret)
    assert keystore.open_sealed() == secret
    # 密文文件里不应该出现明文
    raw = SEALED_FILE.read_bytes()
    assert b"sk-test" not in raw, "密文中不应包含明文"


def test_sign_verify_file():
    """文件签名与验签"""
    _clean()
    keystore.init()
    target = CONFIG_DIR / "demo_config.txt"
    target.write_text("openclaw safe config")
    keystore.sign_file(target, CONFIG_DIR / "demo_config.txt.sig")
    assert keystore.verify_file(target, CONFIG_DIR / "demo_config.txt.sig") is True
    # 篡改后验签失败
    target.write_text("openclaw EVIL config")
    assert keystore.verify_file(target, CONFIG_DIR / "demo_config.txt.sig") is False
