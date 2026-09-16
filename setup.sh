#!/usr/bin/env bash
# =====================================================
# 抗量子龙虾 pqclaw —— 一键安装脚本（小白友好）
# 运行方法：在项目文件夹里执行  ./setup.sh
# =====================================================
set -e
cd "$(dirname "$0")"

echo "=========================================="
echo " 抗量子龙虾 pqclaw 一键安装开始"
echo "=========================================="

echo ""
echo "[1/5] 安装系统工具（需要输入密码，输入时屏幕不显示是正常的）..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

echo ""
echo "[2/5] 创建运行环境..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo ""
echo "[3/5] 安装 Python 依赖（首次需要 2-5 分钟，请耐心等待）..."
pip install --upgrade pip
pip install -e . || pip install .

# 检查首选抗量子库是否装好；失败则自动改用备用库
if ! python -c "import oqs" 2>/dev/null; then
  echo "  （liboqs 安装未成功，自动改用备用抗量子库 pqcrypto ...）"
  pip install pqcrypto
fi

echo ""
echo "[4/5] 运行自动化测试（验证一切正常）..."
pytest -v

echo ""
echo "[5/5] 安装完成！"
echo ""
echo "接下来请运行演示（复制下面两行）："
echo ""
echo "    source .venv/bin/activate"
echo "    pqclaw demo"
echo ""
