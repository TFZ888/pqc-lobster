"""示例：用 pqclaw 加密一个 API Key（演示用假密钥）"""

from pqclaw import keystore

# 1. 初始化（第一次使用）
keystore.init()

# 2. 加密一条机密信息（这里用假密钥演示）
fake_api_key = b"sk-demo-1234567890-abcdef"
keystore.seal(fake_api_key)

# 3. 解密还原
restored = keystore.open_sealed()
print(f"解密还原成功：{restored.decode()}")

# 4. 给配置文件签名并验证
from pathlib import Path

config = Path("config_demo.txt")
config.write_text("openclaw demo config")
keystore.sign_file(config, Path("config_demo.txt.sig"))
ok = keystore.verify_file(config, Path("config_demo.txt.sig"))
print(f"签名验证通过：{ok}")
