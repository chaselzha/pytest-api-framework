"""
封装HTTP请求客户端 - 统一处理请求、认证、重试、日志
"""
import time
import json
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import CONFIG
from common.logger import logger


class APIClient:
    """API客户端"""

    def __init__(self):
        self.base_url = CONFIG.BASE_URL
        self.session = requests.Session()
        self.timeout = CONFIG.REQUEST_TIMEOUT

        # 设置默认请求头
        self.session.headers.update(CONFIG.DEFAULT_HEADERS)

        # 配置重试策略
        retry_strategy = Retry(
            total=CONFIG.REQUEST_RETRY,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 认证token
        self.auth_token = None

        # 保存最后的请求和响应（用于失败调试）
        self.last_request = None
        self.last_response = None

    def mask_sensitive_data(self, data):
        """
        脱敏处理敏感信息
        """
        if not data:
            return data

        if isinstance(data, str):
            # 隐藏密码
            data = re.sub(r'"password":\s*"[^"]*"', '"password":"***"', data)
            # 隐藏 token
            data = re.sub(r'"token":\s*"[^"]*"', '"token":"***"', data)
            data = re.sub(r'"access_token":\s*"[^"]*"', '"access_token":"***"', data)
            data = re.sub(r'"refresh_token":\s*"[^"]*"', '"refresh_token":"***"', data)
            # 隐藏手机号中间4位
            data = re.sub(r'"phone":\s*"(\d{3})\d{4}(\d{4})"', r'"phone":"\1****\2"', data)
            # 隐藏身份证中间8位
            data = re.sub(r'"id_card":\s*"(\d{6})\d{8}(\d{4})"', r'"id_card":"\1********\2"', data)
            # 隐藏邮箱用户名部分
            data = re.sub(r'"email":\s*"([^@]+)@([^"]+)"', r'"email":"\1***@\2"', data)
        elif isinstance(data, dict):
            # 递归处理字典
            result = {}
            sensitive_keys = ['password', 'token', 'access_token', 'refresh_token', 'secret', 'api_key']
            for key, value in data.items():
                if key in sensitive_keys:
                    result[key] = '***'
                elif isinstance(value, dict):
                    result[key] = self.mask_sensitive_data(value)
                elif isinstance(value, list):
                    result[key] = [self.mask_sensitive_data(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [self.mask_sensitive_data(item) if isinstance(item, dict) else item for item in data]

        return data

    def set_auth_token(self, token):
        """设置认证令牌"""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        logger.info("已更新认证Token")

    def _log_request(self, method, url, **kwargs):
        """记录请求日志（脱敏）"""
        logger.info(f"=== 请求 ===")
        logger.info(f"Method: {method}")
        logger.info(f"URL: {url}")
        if 'params' in kwargs and kwargs['params']:
            # params 是字典，直接脱敏
            masked_params = self.mask_sensitive_data(kwargs['params'])
            logger.info(f"Params: {masked_params}")
        if 'json' in kwargs and kwargs['json']:
            masked_json = self.mask_sensitive_data(kwargs['json'])
            logger.info(f"Body: {json.dumps(masked_json, ensure_ascii=False)}")
        if 'data' in kwargs and kwargs['data']:
            if isinstance(kwargs['data'], dict):
                masked_data = self.mask_sensitive_data(kwargs['data'])
                logger.info(f"Data: {masked_data}")
            else:
                logger.info(f"Data: {self.mask_sensitive_data(str(kwargs['data']))}")

    def _log_response(self, response):
        """记录响应日志（脱敏 + 耗时监控）"""
        elapsed = response.elapsed.total_seconds()
        logger.info(f"=== 响应 ===")
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response Time: {elapsed:.3f}s")

        # 慢接口告警
        if elapsed > 5.0:
            logger.error(f"❌ 接口响应超慢: {elapsed:.3f}s > 5s")
        elif elapsed > 3.0:
            logger.warning(f"⚠️ 接口响应慢: {elapsed:.3f}s > 3s")

        try:
            body = response.json()
            masked_body = self.mask_sensitive_data(body)
            logger.info(f"Body: {json.dumps(masked_body, ensure_ascii=False)}")
        except:
            # 非JSON响应，截断显示
            text = response.text[:500]
            logger.info(f"Body: {text}")

    def request(self, method, endpoint, **kwargs):
        """
        发送HTTP请求
        :param method: GET/POST/PUT/DELETE
        :param endpoint: 接口路径
        :param kwargs: requests库的其他参数
        """
        url = f"{self.base_url}{endpoint}"

        # 设置默认超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # 记录请求日志
        self._log_request(method, url, **kwargs)

        # 保存最后请求（用于调试）
        self.last_request = {'method': method, 'url': url, 'kwargs': kwargs}

        start_time = time.time()
        try:
            response = self.session.request(method, url, **kwargs)
            # 保存最后响应（用于调试）
            self.last_response = response
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
            raise

        elapsed = time.time() - start_time
        self._log_response(response)

        return response

    def get(self, endpoint, **kwargs):
        """GET请求"""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        """POST请求"""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        """PUT请求"""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        """DELETE请求"""
        return self.request("DELETE", endpoint, **kwargs)


# 单例模式 - 整个测试共用同一个客户端实例
api_client = APIClient()