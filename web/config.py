"""
可视化平台配置
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Web 配置"""
    # Flask 配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('WEB_HOST', '0.0.0.0')
    PORT = int(os.getenv('WEB_PORT', 5000))

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "web" / "data" / "test_platform.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 测试配置
    TEST_DIR = BASE_DIR / 'tests'
    REPORT_DIR = BASE_DIR / 'reports'
    ALLURE_RESULTS_DIR = REPORT_DIR / 'allure-results'
    ALLURE_REPORT_DIR = REPORT_DIR / 'allure-reports'

    # 日志配置
    LOG_DIR = BASE_DIR / 'logs'

    # 定时任务配置
    SCHEDULER_ENABLED = True

    # 跨域配置
    CORS_ORIGINS = ['*']