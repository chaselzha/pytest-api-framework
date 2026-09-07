"""
工具函数模块
"""
import json
import re
import random
import string
from pathlib import Path
from typing import Any, Dict, Union, List
from jsonschema import validate, ValidationError
from common.logger import logger

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_DIR = BASE_DIR / "schemas"


def generate_random_string(length=8, use_digits=True, use_letters=True):
    """生成随机字符串"""
    chars = ""
    if use_letters:
        chars += string.ascii_letters
    if use_digits:
        chars += string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_random_email(domain="test.com"):
    """生成随机邮箱"""
    username = generate_random_string(8)
    return f"{username}@{domain}"


def generate_random_phone():
    """生成随机手机号"""
    return f"1{random.choice(['3','4','5','6','7','8','9'])}{''.join(random.choices(string.digits, k=9))}"


def load_schema(schema_name: str) -> Dict:
    """
    加载 JSON Schema 文件
    :param schema_name: Schema 文件名，如 "post_schema.json"
    :return: Schema 字典
    """
    schema_path = SCHEMA_DIR / schema_name
    if not schema_path.exists():
        logger.error(f"Schema 文件不存在: {schema_path}")
        return {}

    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_json_schema(data: Any, schema: Union[Dict, str]) -> Dict:
    """
    验证 JSON 数据是否符合 Schema

    :param data: 要验证的数据
    :param schema: Schema 字典或 Schema 文件名
    :return: {"valid": bool, "errors": list, "message": str}

    示例:
        result = validate_json_schema(response.json(), "post_schema.json")
        assert result["valid"], result["message"]
    """
    # 如果是字符串，当作文件名加载
    if isinstance(schema, str):
        schema = load_schema(schema)
        if not schema:
            return {
                "valid": False,
                "errors": ["Schema 文件不存在"],
                "message": "Schema 文件不存在"
            }

    try:
        validate(instance=data, schema=schema)
        logger.info(f"✅ JSON Schema 校验通过")
        return {
            "valid": True,
            "errors": [],
            "message": "校验通过"
        }
    except ValidationError as e:
        error_msg = f"❌ JSON Schema 校验失败: {e.message}"
        logger.error(error_msg)
        logger.error(f"  路径: {'.'.join(str(p) for p in e.path) if e.path else '/'}")
        logger.error(f"  实际值: {e.instance}")
        return {
            "valid": False,
            "errors": [e.message],
            "message": error_msg,
            "path": list(e.path),
            "instance": e.instance
        }


def validate_json_schema_list(data_list: List, schema: Union[Dict, str]) -> Dict:
    """
    验证列表中的每个元素是否符合 Schema

    :param data_list: 要验证的数据列表
    :param schema: Schema 字典或 Schema 文件名
    :return: {"valid": bool, "errors": list, "message": str, "total": int, "passed": int, "failed": int}
    """
    if not isinstance(data_list, list):
        return {
            "valid": False,
            "errors": ["数据不是列表类型"],
            "message": "数据不是列表类型",
            "total": 0,
            "passed": 0,
            "failed": 0
        }

    # 如果是字符串，当作文件名加载
    if isinstance(schema, str):
        schema = load_schema(schema)
        if not schema:
            return {
                "valid": False,
                "errors": ["Schema 文件不存在"],
                "message": "Schema 文件不存在",
                "total": 0,
                "passed": 0,
                "failed": 0
            }

    total = len(data_list)
    passed = 0
    failed = 0
    errors = []

    for index, item in enumerate(data_list):
        try:
            validate(instance=item, schema=schema)
            passed += 1
        except ValidationError as e:
            failed += 1
            errors.append(f"索引 {index}: {e.message}")

    valid = failed == 0

    if valid:
        logger.info(f"✅ 列表 Schema 校验通过: {total}/{total} 条数据全部符合")
    else:
        logger.warning(f"⚠️ 列表 Schema 校验: {passed}/{total} 通过, {failed}/{total} 失败")

    return {
        "valid": valid,
        "errors": errors,
        "message": f"通过: {passed}/{total}, 失败: {failed}/{total}" if not valid else f"全部通过: {total}/{total}",
        "total": total,
        "passed": passed,
        "failed": failed
    }


def extract_value_by_jsonpath(data: Any, path: str) -> Any:
    """
    通过简单路径提取JSON数据中的值
    :param data: JSON数据
    :param path: 路径，如 "data.user.id"
    """
    keys = path.split('.')
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return None
    return result


def read_json_file(file_path: str) -> Dict:
    """读取JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def mask_sensitive_data(data: str) -> str:
    """脱敏处理，用于日志输出"""
    patterns = [
        (r'"password":\s*"[^"]*"', '"password":"***"'),
        (r'"token":\s*"[^"]*"', '"token":"***"'),
        (r'"secret":\s*"[^"]*"', '"secret":"***"'),
    ]
    for pattern, replacement in patterns:
        data = re.sub(pattern, replacement, data)
    return data