#!/bin/bash
# Jenkins 环境配置脚本

set -e

echo "=========================================="
echo "  Jenkins 环境配置"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 Python
echo -e "${YELLOW}检查 Python...${NC}"
python3 --version || {
    echo -e "${RED}请安装 Python 3.11+${NC}"
    exit 1
}

# 安装 Allure
if ! command -v allure &> /dev/null; then
    echo -e "${YELLOW}安装 Allure...${NC}"
    ALLURE_VERSION="2.29.0"
    wget https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip
    unzip allure-${ALLURE_VERSION}.zip -d /opt/
    sudo ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure
    rm allure-${ALLURE_VERSION}.zip
fi

# 验证 Allure
echo -e "${YELLOW}验证 Allure...${NC}"
allure --version

# 安装 Python 依赖
echo -e "${YELLOW}安装 Python 依赖...${NC}"
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo -e "${GREEN}=========================================="
echo -e "  ✅ Jenkins 环境配置完成！"
echo -e "==========================================${NC}"