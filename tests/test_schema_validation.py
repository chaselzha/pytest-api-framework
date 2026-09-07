"""
JSON Schema 校验测试用例
"""
import pytest
from common.utils import validate_json_schema, validate_json_schema_list
from common.logger import logger


class TestSchemaValidation:
    """Schema 校验测试类"""

    def test_post_schema_single(self, authenticated_api):
        """
        测试：单条文章数据 Schema 校验
        """
        response = authenticated_api.get("/posts/1")
        assert response.status_code == 200

        data = response.json()
        result = validate_json_schema(data, "post_schema.json")

        assert result["valid"] is True, result["message"]
        logger.info(f"✅ 文章数据 Schema 校验通过")

    def test_post_schema_list(self, authenticated_api):
        """
        测试：文章列表数据 Schema 校验
        """
        response = authenticated_api.get("/posts")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        result = validate_json_schema_list(data, "post_schema.json")

        assert result["valid"] is True, result["message"]
        assert result["total"] == result["passed"]
        logger.info(f"✅ 文章列表 Schema 校验通过: {result['passed']}/{result['total']}")

    def test_user_schema_single(self, authenticated_api):
        """
        测试：单条用户数据 Schema 校验
        """
        response = authenticated_api.get("/users/1")
        assert response.status_code == 200

        data = response.json()
        result = validate_json_schema(data, "user_schema.json")

        assert result["valid"] is True, result["message"]
        logger.info(f"✅ 用户数据 Schema 校验通过")

    def test_comment_schema_single(self, authenticated_api):
        """
        测试：单条评论数据 Schema 校验
        """
        response = authenticated_api.get("/comments/1")
        assert response.status_code == 200

        data = response.json()
        result = validate_json_schema(data, "comment_schema.json")

        assert result["valid"] is True, result["message"]
        logger.info(f"✅ 评论数据 Schema 校验通过")

    def test_comment_schema_list(self, authenticated_api):
        """
        测试：评论列表数据 Schema 校验
        """
        response = authenticated_api.get("/comments", params={"postId": 1})
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        result = validate_json_schema_list(data, "comment_schema.json")

        assert result["valid"] is True, result["message"]
        logger.info(f"✅ 评论列表 Schema 校验通过: {result['passed']}/{result['total']}")