"""
Pytest Fixtures - 全局共享资源
"""
import pytest
import json
import yaml
from pathlib import Path
from common.client import api_client
from common.logger import logger
from config.settings import CONFIG

# 测试数据目录
TESTDATA_DIR = Path(__file__).parent.parent / "testdata"


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    """整个测试会话的初始化和清理"""
    logger.info(f"========== 开始API自动化测试 ==========")
    logger.info(f"测试环境: {CONFIG.BASE_URL}")

    yield

    logger.info(f"========== API自动化测试结束 ==========")


@pytest.fixture(scope="function")
def api():
    """每个测试函数获取APIClient实例"""
    return api_client


@pytest.fixture(scope="session")
def auth_token(api):
    """获取认证Token - 会话级别，只执行一次"""
    logger.info("获取认证Token...")

    # 模拟登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }

    try:
        response = api.post("/api/auth/login", json=login_data)
        token = response.json().get("data", {}).get("token")
        api.set_auth_token(token)
        logger.info("Token获取成功")
        return token
    except Exception as e:
        logger.error(f"获取Token失败: {e}")
        return None


@pytest.fixture(scope="function")
def authenticated_api(auth_token, api):
    """已认证的API客户端"""
    if auth_token:
        api.set_auth_token(auth_token)
    return api


@pytest.fixture(scope="function")
def test_data():
    """加载测试数据"""

    def _load_data(filename):
        file_path = TESTDATA_DIR / filename
        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif file_path.suffix in ['.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")

    return _load_data


@pytest.fixture(scope="function")
def create_test_user(api):
    """创建测试用户fixture"""
    created_users = []

    def _create_user(user_data):
        response = api.post("/api/users", json=user_data)
        user_id = response.json().get("data", {}).get("id")
        if user_id:
            created_users.append(user_id)
        return response

    yield _create_user

    # 清理：删除创建的用户
    for user_id in created_users:
        try:
            api.delete(f"/api/users/{user_id}")
            logger.info(f"清理测试用户: {user_id}")
        except Exception as e:
            logger.warning(f"清理用户失败 {user_id}: {e}")