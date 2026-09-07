"""
配置管理模块 - 支持多环境切换
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """基础配置"""
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = BASE_DIR / "logs"

    # 报告配置
    REPORT_DIR = BASE_DIR / "reports"

    # 超时配置（支持环境变量）
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    REQUEST_RETRY = int(os.getenv("REQUEST_RETRY", 3))

    # 认证配置
    AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "admin123")

    # 默认请求头
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


class TestConfig(Config):
    """测试环境配置"""
    BASE_URL = os.getenv("TEST_BASE_URL", "https://jsonplaceholder.typicode.com")


class DevConfig(Config):
    """开发环境配置"""
    BASE_URL = os.getenv("DEV_BASE_URL", "https://jsonplaceholder.typicode.com")


class ProdConfig(Config):
    """生产环境配置（谨慎使用）"""
    BASE_URL = os.getenv("PROD_BASE_URL", "https://api.example.com")


# 环境映射
ENV_MAP = {
    "dev": DevConfig,
    "test": TestConfig,
    "prod": ProdConfig
}

# 从环境变量获取当前环境，默认test
ENV = os.getenv("API_ENV", "test")
CONFIG = ENV_MAP.get(ENV, TestConfig)()