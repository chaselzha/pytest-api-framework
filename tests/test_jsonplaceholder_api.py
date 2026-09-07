"""
JSONPlaceholder API 测试用例
测试地址: https://jsonplaceholder.typicode.com
"""
import pytest
import requests
import allure
from common.logger import logger
from common.utils import validate_json_schema


@allure.epic("JSONPlaceholder API 测试")
@allure.feature("文章模块")
class TestJSONPlaceholderPosts:
    """测试 /posts 接口"""

    @allure.story("获取文章列表")
    @allure.title("测试获取所有文章列表成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "regression")
    def test_get_all_posts_success(self, authenticated_api):
        """
        测试：获取所有文章列表成功
        """
        with allure.step("发送 GET 请求获取所有文章"):
            response = authenticated_api.get("/posts")

        with allure.step("验证响应状态码为 200"):
            assert response.status_code == 200

        with allure.step("验证返回数据为列表且包含必要字段"):
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

            # 验证前5条数据
            for post in data[:5]:
                assert "id" in post
                assert "userId" in post
                assert "title" in post
                assert "body" in post

        logger.info(f"成功获取 {len(data)} 篇文章")

    @allure.story("获取单个文章")
    @allure.title("测试根据ID获取单篇文章成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke")
    def test_get_single_post_success(self, authenticated_api):
        """测试：根据ID获取单篇文章成功"""
        post_id = 1

        with allure.step(f"发送 GET 请求获取文章 ID={post_id}"):
            response = authenticated_api.get(f"/posts/{post_id}")

        with allure.step("验证响应状态码为 200"):
            assert response.status_code == 200

        with allure.step("验证返回数据正确"):
            data = response.json()
            assert data["id"] == post_id
            assert data["userId"] == 1
            assert "title" in data
            assert "body" in data

        logger.info(f"成功获取文章 ID: {post_id}")

    @allure.story("异常场景")
    @allure.title("测试获取不存在的文章返回404")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("regression")
    def test_get_post_not_found(self, authenticated_api):
        """测试：获取不存在的文章"""
        post_id = 99999

        with allure.step(f"发送 GET 请求获取不存在的文章 ID={post_id}"):
            with pytest.raises(requests.exceptions.HTTPError) as exc_info:
                authenticated_api.get(f"/posts/{post_id}")

        with allure.step("验证返回 404 状态码"):
            assert exc_info.value.response.status_code == 404
            logger.info(f"不存在的文章 {post_id} 返回 404，符合预期")

    @allure.story("参数化测试")
    @allure.title("根据userId获取文章列表 - 参数化测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("user_id, expected_count", [
        (1, 10),
        (2, 10),
        (10, 10),
        (99, 0),
        (0, 0),
    ])
    def test_get_posts_by_user_id(self, authenticated_api, user_id, expected_count):
        """参数化测试：根据userId获取文章列表"""
        with allure.step(f"发送 GET 请求获取 userId={user_id} 的文章"):
            response = authenticated_api.get("/posts", params={"userId": user_id})

        with allure.step("验证响应状态码为 200"):
            assert response.status_code == 200

        with allure.step("验证所有文章都属于该用户"):
            data = response.json()
            assert isinstance(data, list)
            for post in data:
                assert post["userId"] == user_id

        actual_count = len(data)
        if expected_count == 10:
            assert actual_count <= 10
        else:
            assert actual_count == expected_count

        logger.info(f"userId={user_id} 的文章数量: {actual_count}")

    @allure.story("参数化测试")
    @allure.title("批量测试多个文章ID")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("post_id", [1, 5, 10, 50, 100])
    def test_multiple_posts_by_id(self, authenticated_api, post_id):
        """参数化测试：批量测试多个文章ID"""
        with allure.step(f"发送 GET 请求获取文章 ID={post_id}"):
            response = authenticated_api.get(f"/posts/{post_id}")

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == post_id
            assert "title" in data
            assert "body" in data

        logger.info(f"文章 {post_id} 获取成功")


@allure.epic("JSONPlaceholder API 测试")
@allure.feature("评论模块")
class TestJSONPlaceholderComments:
    """测试 /comments 接口"""

    @allure.story("获取评论")
    @allure.title("测试获取某篇文章的评论")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_comments_for_post(self, authenticated_api):
        """测试：获取某篇文章的评论"""
        post_id = 1

        with allure.step(f"发送 GET 请求获取文章 {post_id} 的评论"):
            response = authenticated_api.get("/comments", params={"postId": post_id})

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

        with allure.step("验证所有评论都属于该文章"):
            for comment in data:
                assert comment["postId"] == post_id

        logger.info(f"文章 {post_id} 有 {len(data)} 条评论")

    @allure.story("获取评论")
    @allure.title("测试根据ID获取单条评论")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_comment_by_id(self, authenticated_api):
        """测试：根据ID获取单条评论"""
        comment_id = 1

        with allure.step(f"发送 GET 请求获取评论 ID={comment_id}"):
            response = authenticated_api.get(f"/comments/{comment_id}")

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == comment_id
            assert "postId" in data
            assert "name" in data
            assert "email" in data
            assert "body" in data


@allure.epic("JSONPlaceholder API 测试")
@allure.feature("用户模块")
class TestJSONPlaceholderUsers:
    """测试 /users 接口"""

    @allure.story("获取用户")
    @allure.title("测试获取所有用户列表")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_all_users_success(self, authenticated_api):
        """测试：获取所有用户列表"""
        with allure.step("发送 GET 请求获取所有用户"):
            response = authenticated_api.get("/users")

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 10

        with allure.step("验证用户数据结构完整"):
            for user in data:
                assert "id" in user
                assert "name" in user
                assert "username" in user
                assert "email" in user
                assert "address" in user
                assert "phone" in user
                assert "website" in user
                assert "company" in user

    @allure.story("获取用户")
    @allure.title("测试根据ID获取单个用户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_single_user_success(self, authenticated_api):
        """测试：根据ID获取单个用户"""
        user_id = 1

        with allure.step(f"发送 GET 请求获取用户 ID={user_id}"):
            response = authenticated_api.get(f"/users/{user_id}")

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == user_id
            assert data["name"] == "Leanne Graham"
            assert data["username"] == "Bret"
            assert data["email"] == "Sincere@april.biz"

    @allure.story("参数化测试")
    @allure.title("验证多个用户的名称 - 参数化测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("user_id, expected_name", [
        (1, "Leanne Graham"),
        (2, "Ervin Howell"),
        (3, "Clementine Bauch"),
        (4, "Patricia Lebsack"),
        (5, "Chelsey Dietrich"),
    ])
    def test_users_name_check(self, authenticated_api, user_id, expected_name):
        """参数化测试：验证多个用户的名称"""
        with allure.step(f"发送 GET 请求获取用户 ID={user_id}"):
            response = authenticated_api.get(f"/users/{user_id}")

        with allure.step("验证用户名称正确"):
            assert response.status_code == 200
            data = response.json()
            assert data["name"] == expected_name


@allure.epic("JSONPlaceholder API 测试")
@allure.feature("相册模块")
class TestJSONPlaceholderAlbums:
    """测试 /albums 接口"""

    @allure.story("获取相册")
    @allure.title("测试获取指定用户的相册")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_albums_by_user(self, authenticated_api):
        """测试：获取指定用户的相册"""
        user_id = 1

        with allure.step(f"发送 GET 请求获取用户 {user_id} 的相册"):
            response = authenticated_api.get("/albums", params={"userId": user_id})

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 10

        with allure.step("验证所有相册都属于该用户"):
            for album in data:
                assert album["userId"] == user_id
                assert "id" in album
                assert "title" in album

    @allure.story("获取照片")
    @allure.title("测试获取相册的照片")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_album_photos(self, authenticated_api):
        """测试：获取相册的照片"""
        album_id = 1

        with allure.step(f"发送 GET 请求获取相册 {album_id} 的照片"):
            response = authenticated_api.get("/photos", params={"albumId": album_id})

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 50

        with allure.step("验证照片数据结构完整"):
            for photo in data[:5]:
                assert photo["albumId"] == album_id
                assert "id" in photo
                assert "title" in photo
                assert "url" in photo
                assert "thumbnailUrl" in photo


@allure.epic("JSONPlaceholder API 测试")
@allure.feature("待办事项模块")
class TestJSONPlaceholderTodos:
    """测试 /todos 接口"""

    @allure.story("获取待办")
    @allure.title("测试获取指定用户的待办事项")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_todos_by_user(self, authenticated_api):
        """测试：获取指定用户的待办事项"""
        user_id = 1

        with allure.step(f"发送 GET 请求获取用户 {user_id} 的待办事项"):
            response = authenticated_api.get("/todos", params={"userId": user_id})

        with allure.step("验证响应成功"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 20

        with allure.step("验证待办数据结构完整"):
            for todo in data:
                assert todo["userId"] == user_id
                assert "id" in todo
                assert "title" in todo
                assert "completed" in todo
                assert isinstance(todo["completed"], bool)

    @allure.story("获取待办")
    @allure.title("测试获取已完成的待办事项")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_completed_todos(self, authenticated_api):
        """测试：获取已完成的待办事项"""
        with allure.step("发送 GET 请求获取已完成的待办事项"):
            response = authenticated_api.get("/todos", params={"completed": True})

        with allure.step("验证所有待办都是已完成状态"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            for todo in data:
                assert todo["completed"] is True

    @allure.story("获取待办")
    @allure.title("测试获取未完成的待办事项")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_incomplete_todos(self, authenticated_api):
        """测试：获取未完成的待办事项"""
        with allure.step("发送 GET 请求获取未完成的待办事项"):
            response = authenticated_api.get("/todos", params={"completed": False})

        with allure.step("验证所有待办都是未完成状态"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            for todo in data:
                assert todo["completed"] is False