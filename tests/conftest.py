"""
Pytest Fixtures - 全局共享资源
"""
import pytest
import json
import yaml
from pathlib import Path
from datetime import datetime
import allure
from common.client import api_client
from common.logger import logger
from config.settings import CONFIG

# 测试数据目录
TESTDATA_DIR = Path(__file__).parent.parent / "testdata"
REPORT_DIR = CONFIG.REPORT_DIR
ERROR_DIR = REPORT_DIR / "errors"


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    """整个测试会话的初始化和清理"""
    # 创建错误报告目录
    ERROR_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"========== 开始API自动化测试 ==========")
    logger.info(f"测试环境: {CONFIG.BASE_URL}")

    # Allure 环境信息 - 通过写入文件方式（方式二，最稳定）
    allure_results_dir = Path("allure-results")
    allure_results_dir.mkdir(exist_ok=True)

    environment_file = allure_results_dir / "environment.properties"
    with open(environment_file, 'w', encoding='utf-8') as f:
        f.write(f"测试环境={CONFIG.__class__.__name__}\n")
        f.write(f"API地址={CONFIG.BASE_URL}\n")
        f.write(f"执行时间={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python版本=3.11.16\n")
        f.write(f"测试框架=Pytest\n")
        f.write(f"执行平台=macOS\n")

    yield

    logger.info(f"========== API自动化测试结束 ==========")


@pytest.fixture(scope="session")
def api():
    """获取APIClient实例 - 会话级别"""
    return api_client


@pytest.fixture(scope="session")
def auth_token(api):
    """
    获取认证Token - JSONPlaceholder 不需要认证
    这里返回一个模拟token，保持框架兼容性
    """
    logger.info("JSONPlaceholder 无需认证，使用模拟Token")
    mock_token = "mock_token_for_jsonplaceholder"
    api.set_auth_token(mock_token)
    return mock_token


@pytest.fixture(scope="function")
def authenticated_api(auth_token, api):
    """已认证的API客户端 - function级别，每个用例独立"""
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
    """创建测试用户fixture - JSONPlaceholder 支持POST创建"""
    created_users = []

    def _create_user(user_data):
        response = api.post("/users", json=user_data)
        user_id = response.json().get("id")
        if user_id:
            created_users.append(user_id)
        return response

    yield _create_user

    # 清理：JSONPlaceholder 不支持真实删除，仅记录日志
    for user_id in created_users:
        logger.info(f"JSONPlaceholder 模拟清理用户: {user_id}")


@pytest.fixture(scope="function")
def created_post(authenticated_api):
    """
    接口关联 Fixture：创建一篇文章并返回文章数据
    用于后续测试（如更新、删除、获取评论等）
    """
    post_data = {
        "title": "自动化测试文章",
        "body": "这是通过自动化测试创建的文章内容",
        "userId": 1
    }

    logger.info("创建测试文章...")
    response = authenticated_api.post("/posts", json=post_data)
    assert response.status_code == 201

    post = response.json()
    post_id = post.get("id")
    logger.info(f"✅ 创建测试文章成功，ID: {post_id}")

    yield post

    # 清理：删除创建的文章
    try:
        delete_response = authenticated_api.delete(f"/posts/{post_id}")
        if delete_response.status_code == 200:
            logger.info(f"🧹 清理测试文章成功，ID: {post_id}")
        else:
            logger.warning(f"清理测试文章失败，ID: {post_id}")
    except Exception as e:
        logger.warning(f"清理测试文章异常: {e}")


# ============================================================
# Allure 报告自定义装饰器
# ============================================================

def allure_step(title):
    """Allure 步骤装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with allure.step(title):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def allure_attach_json(data, name="JSON数据", attachment_type=allure.attachment_type.JSON):
    """将 JSON 数据附加到 Allure 报告"""
    if data:
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name=name,
            attachment_type=attachment_type
        )


def allure_attach_text(text, name="文本数据"):
    """将文本附加到 Allure 报告"""
    if text:
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )


# ============================================================
# 失败自动保存 Hook
# ============================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试失败时自动保存请求和响应信息
    """
    outcome = yield
    rep = outcome.get_result()

    # 只在测试失败时处理
    if rep.when == "call" and rep.failed:
        # 获取测试名称
        test_name = item.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 创建本次失败的报告目录
        error_dir = ERROR_DIR / f"{test_name}_{timestamp}"
        error_dir.mkdir(parents=True, exist_ok=True)

        # 尝试获取 API 客户端实例
        try:
            api_client_obj = None
            # 从 fixture 中获取 authenticated_api
            if hasattr(item, "funcargs"):
                api_client_obj = item.funcargs.get("authenticated_api")
                if not api_client_obj:
                    api_client_obj = item.funcargs.get("api")

            if api_client_obj and hasattr(api_client_obj, "last_request"):
                # 保存请求信息
                if api_client_obj.last_request:
                    request_file = error_dir / "request.json"
                    with open(request_file, 'w', encoding='utf-8') as f:
                        json.dump(api_client_obj.last_request, f, ensure_ascii=False, indent=2)
                    logger.info(f"📁 请求信息已保存: {request_file}")

                    # 附加到 Allure 报告
                    allure_attach_json(api_client_obj.last_request, "失败请求信息")

                # 保存响应信息
                if hasattr(api_client_obj, "last_response") and api_client_obj.last_response:
                    response_data = {
                        "status_code": api_client_obj.last_response.status_code,
                        "headers": dict(api_client_obj.last_response.headers),
                        "url": api_client_obj.last_response.url,
                        "text": api_client_obj.last_response.text[:5000]
                    }
                    # 尝试解析 JSON
                    try:
                        response_data["json"] = api_client_obj.last_response.json()
                    except:
                        pass

                    response_file = error_dir / "response.json"
                    with open(response_file, 'w', encoding='utf-8') as f:
                        json.dump(response_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"📁 响应信息已保存: {response_file}")

                    # 附加到 Allure 报告
                    allure_attach_json(response_data, "失败响应信息")

        except Exception as e:
            logger.warning(f"保存失败信息时出错: {e}")