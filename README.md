# pqclaw —— 抗量子龙虾 🦞

给开源 AI 智能体 OpenClaw（昵称"龙虾"）加上**抗量子密码安全层**。

量子计算机成熟后，现有的 RSA / ECC 加密会被轻易破解。本项目使用 NIST 标准化的
新一代抗量子算法，为你的 API 密钥和配置文件提供量子计算机也破解不了的保护。

## ✨ 特性

- **ML-KEM-768 密钥封装**：API 密钥用抗量子算法加密存储，磁盘上永远没有明文
- **ML-DSA-65 数字签名**：配置文件防篡改，被改动立刻发现
- **一键安装**：`./setup.sh` 自动完成全部安装与测试
- **一键演示**：`pqclaw demo` 展示完整加解密流程
- **自动化测试**：pytest 全绿 + GitHub Actions CI

## 🚀 快速开始（3 条命令搞定）

```bash
# 1. 进入项目文件夹
cd pqclaw

# 2. 一键安装（自动装环境、装依赖、跑测试）
bash setup.sh

# 3. 运行演示，看到"全部成功"即完成
source .venv/bin/activate
pqclaw demo
```

> 首次安装需要 2-5 分钟（要下载依赖），请耐心等待。

## 📖 常用命令

| 命令 | 作用 |
|---|---|
| `pqclaw init` | 初始化抗量子安全目录（第一次先运行） |
| `pqclaw seal` | 加密你的 API Key（从环境变量 `DEEPSEEK_API_KEY` 读取） |
| `pqclaw open` | 解密并显示你的 API Key |
| `pqclaw sign 文件名` | 给文件签名（防篡改） |
| `pqclaw verify 文件名` | 验证文件有没有被篡改 |
| `pqclaw demo` | 一键演示整个抗量子加密流程 |

### 加密你的真实 API Key

```bash
export DEEPSEEK_API_KEY="sk-你的真实密钥"
pqclaw seal     # 加密并保存（磁盘上是密文）
pqclaw open     # 需要时解密出来使用
```

## 🗂 项目结构

```
pqclaw/
├── pqclaw/
│   ├── pqcrypto.py   # 抗量子密码核心（ML-KEM + ML-DSA）
│   ├── keystore.py   # 密钥保险箱（加密存储 API Key）
│   └── cli.py        # 命令行工具
├── tests/            # 自动化测试
├── examples/         # 使用示例
├── docs/             # 文档
└── setup.sh          # 一键安装脚本
```

## 🔒 安全说明

- 本项目为**学习与演示性质**的安全加固，算法使用 NIST 标准实现（ML-KEM-768 / ML-DSA-65）
- 请妥善保管 `~/.pqclaw/` 目录下的私钥文件，丢失后密文将无法解密
- 不要把你的真实密钥提交到公开仓库

## 📄 许可证

MIT License
