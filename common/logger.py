"""
日志模块 - 使用loguru实现优雅日志
"""
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from config.settings import CONFIG

# 移除默认handler
logger.remove()

# 日志格式
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# 控制台输出
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level=CONFIG.LOG_LEVEL,
    colorize=True
)

# 文件输出 - 使用自定义时间格式
LOG_DIR = CONFIG.LOG_DIR
LOG_DIR.mkdir(exist_ok=True)


def get_current_time_str():
    """获取当前时间的格式化字符串"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d_%H-%M-%S")


# 主日志文件 - 每次运行生成新的日志文件
main_log_path = LOG_DIR / f"api_test_{get_current_time_str()}.log"
logger.add(
    main_log_path,
    format=LOG_FORMAT,
    level="DEBUG",
    rotation="1 day",
    retention="30 days",
    encoding="utf-8",
    enqueue=True
)

# 错误日志单独输出
error_log_path = LOG_DIR / f"api_error_{get_current_time_str()}.log"
logger.add(
    error_log_path,
    format=LOG_FORMAT,
    level="ERROR",
    rotation="1 day",
    retention="30 days",
    encoding="utf-8",
    enqueue=True
)

__all__ = ["logger"]