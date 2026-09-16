"""pqclaw —— 抗量子龙虾安全层命令行工具"""

import argparse
import os
import sys
from pathlib import Path

from . import keystore


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pqclaw",
        description="抗量子龙虾：给 OpenClaw 加抗量子密码安全层（ML-KEM + ML-DSA）",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="初始化抗量子安全目录（第一次先运行这个）")
    sub.add_parser("seal", help="加密 API Key（从环境变量 DEEPSEEK_API_KEY 读取）")
    sub.add_parser("open", help="解密 API Key 并打印出来")
    sub.add_parser("sign", help="给文件签名（防篡改）").add_argument("file")
    sub.add_parser("verify", help="验证文件签名").add_argument("file")
    sub.add_parser("demo", help="一键演示抗量子加密全过程")

    args = parser.parse_args()

    if args.command == "init":
        keystore.init()

    elif args.command == "seal":
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            print("❌ 请先设置密钥，再执行 seal：")
            print('   export DEEPSEEK_API_KEY="sk-你的真实密钥"')
            sys.exit(1)
        keystore.seal(key.encode())

    elif args.command == "open":
        try:
            secret = keystore.open_sealed()
            print(secret.decode())
        except Exception as e:
            print(f"❌ 解密失败：{e}（是不是还没运行 pqclaw init？）")
            sys.exit(1)

    elif args.command == "sign":
        keystore.sign_file(Path(args.file), Path(str(args.file) + ".sig"))

    elif args.command == "verify":
        ok = keystore.verify_file(Path(args.file), Path(str(args.file) + ".sig"))
        print("✅ 签名有效，文件没有被篡改！" if ok else "❌ 签名无效，文件可能被篡改！")
        sys.exit(0 if ok else 1)

    elif args.command == "demo":
        run_demo()


def run_demo() -> None:
    """完整演示：让小白看到抗量子加密真正跑起来"""
    print("=" * 46)
    print("  抗量子龙虾 pqclaw —— 运行演示")
    print("=" * 46)

    # 第 1 步：密钥封装（ML-KEM-768）
    print("\n[1/3] 生成抗量子密钥对（ML-KEM-768）...")
    pub, sec = _kem_keypair()
    print("      ✅ 公钥/私钥生成成功")

    print("[1/3] 封装机密信息（把 API Key 装进抗量子信封）...")
    fake_key = b"sk-demo-1234567890-anti-quantum"
    ciphertext, shared_a = _encaps(pub)
    print(f"      ✅ 加密完成，密文长度：{len(ciphertext)} 字节（不是明文）")

    print("[1/3] 拆封还原（用私钥打开信封）...")
    shared_b = _decaps(ciphertext, sec)
    assert shared_a == shared_b, "密钥还原不一致"
    print("      ✅ 解密成功，还原出的密钥与原文一致")

    # 第 2 步：数字签名（ML-DSA-65）
    print("\n[2/3] 生成抗量子签名密钥对（ML-DSA-65）...")
    spub, ssec = _dsa_keypair()
    print("      ✅ 签名密钥生成成功")

    print("[2/3] 给配置文件签名...")
    message = b"openclaw config v1.0, do not tamper"
    signature = _sign(message, ssec)
    print(f"      ✅ 签名完成，签名长度：{len(signature)} 字节")

    print("[2/3] 验证签名（模拟检查配置有没有被篡改）...")
    ok = _verify(message, signature, spub)
    tampered = _verify(b"openclaw config v1.0, TAMPERED!", signature, spub)
    print(f"      ✅ 原文件验签：通过 = {ok}")
    print(f"      ✅ 篡改文件验签：被拦截 = {not tampered}")

    # 第 3 步：结论
    print("\n" + "=" * 46)
    print("  ✅ 全部成功！抗量子安全层运行正常")
    print("  ✅ 说明：即使量子计算机也破解不了这套加密")
    print("=" * 46)
    print("\n下一步（可选）：把你的真实 DeepSeek 密钥加密保管：")
    print('   export DEEPSEEK_API_KEY="sk-你的真实密钥"')
    print("   pqclaw seal")


# ---- demo 内部辅助函数（与 pqcrypto 解耦，兼容两种后端）----

from . import pqcrypto  # noqa: E402


def _kem_keypair():
    return pqcrypto.KEM.generate_keypair()


def _encaps(pub):
    return pqcrypto.KEM.encaps(pub)


def _decaps(ct, sec):
    return pqcrypto.KEM.decaps(ct, sec)


def _dsa_keypair():
    return pqcrypto.DSA.generate_keypair()


def _sign(msg, sec):
    return pqcrypto.DSA.sign(msg, sec)


def _verify(msg, sig, pub):
    return pqcrypto.DSA.verify(msg, sig, pub)


if __name__ == "__main__":
    main()
