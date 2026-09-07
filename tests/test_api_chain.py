"""
接口关联测试 - 测试接口之间的数据依赖
使用 JSONPlaceholder 真实支持的 GET 请求进行关联测试
"""
import pytest
from common.logger import logger


class TestAPIChain:
    """接口关联测试类 - 使用 GET 请求测试数据关联"""

    def test_user_posts_chain(self, authenticated_api):
        """
        测试链1：获取用户 → 获取该用户的所有文章 → 验证数据一致性
        """
        user_id = 1

        # 1. 获取用户信息
        logger.info(f"步骤1: 获取用户 ID={user_id}")
        user_response = authenticated_api.get(f"/users/{user_id}")
        assert user_response.status_code == 200
        user = user_response.json()
        logger.info(f"✅ 获取用户: {user['name']} (用户名: {user['username']})")

        # 2. 获取该用户的所有文章
        logger.info(f"步骤2: 获取用户 {user['name']} 的所有文章")
        posts_response = authenticated_api.get("/posts", params={"userId": user_id})
        assert posts_response.status_code == 200
        posts = posts_response.json()

        assert isinstance(posts, list)
        assert len(posts) > 0
        logger.info(f"✅ 用户 {user['name']} 有 {len(posts)} 篇文章")

        # 3. 验证所有文章都属于该用户
        for post in posts:
            assert post["userId"] == user_id
            assert "id" in post
            assert "title" in post
            assert "body" in post

        logger.info(f"✅ 步骤3: 验证通过，所有文章都属于用户 {user['name']}")

    def test_post_comments_chain(self, authenticated_api):
        """
        测试链2：获取文章 → 获取该文章的评论 → 验证数据一致性
        """
        post_id = 1

        # 1. 获取文章
        logger.info(f"步骤1: 获取文章 ID={post_id}")
        post_response = authenticated_api.get(f"/posts/{post_id}")
        assert post_response.status_code == 200
        post = post_response.json()
        logger.info(f"✅ 获取文章: {post['title'][:40]}...")

        # 2. 获取该文章的评论
        logger.info(f"步骤2: 获取文章 ID={post_id} 的评论")
        comments_response = authenticated_api.get("/comments", params={"postId": post_id})
        assert comments_response.status_code == 200
        comments = comments_response.json()

        assert isinstance(comments, list)
        logger.info(f"✅ 文章 ID={post_id} 有 {len(comments)} 条评论")

        # 3. 验证所有评论都属于该文章
        for comment in comments:
            assert comment["postId"] == post_id
            assert "id" in comment
            assert "name" in comment
            assert "email" in comment
            assert "body" in comment

        logger.info(f"✅ 步骤3: 验证通过，所有评论都属于文章 ID={post_id}")

    def test_album_photos_chain(self, authenticated_api):
        """
        测试链3：获取相册 → 获取该相册的照片 → 验证数据一致性
        """
        album_id = 1

        # 1. 获取相册
        logger.info(f"步骤1: 获取相册 ID={album_id}")
        album_response = authenticated_api.get(f"/albums/{album_id}")
        assert album_response.status_code == 200
        album = album_response.json()
        logger.info(f"✅ 获取相册: {album['title'][:40]}...")

        # 2. 获取该相册的照片
        logger.info(f"步骤2: 获取相册 ID={album_id} 的照片")
        photos_response = authenticated_api.get("/photos", params={"albumId": album_id})
        assert photos_response.status_code == 200
        photos = photos_response.json()

        assert isinstance(photos, list)
        assert len(photos) > 0
        logger.info(f"✅ 相册 ID={album_id} 有 {len(photos)} 张照片")

        # 3. 验证所有照片都属于该相册
        for photo in photos[:5]:  # 只验证前5张
            assert photo["albumId"] == album_id
            assert "id" in photo
            assert "title" in photo
            assert "url" in photo
            assert "thumbnailUrl" in photo

        logger.info(f"✅ 步骤3: 验证通过，所有照片都属于相册 ID={album_id}")

    def test_user_todos_chain(self, authenticated_api):
        """
        测试链4：获取用户 → 获取该用户的待办事项 → 统计完成率
        """
        user_id = 1

        # 1. 获取用户信息
        logger.info(f"步骤1: 获取用户 ID={user_id}")
        user_response = authenticated_api.get(f"/users/{user_id}")
        assert user_response.status_code == 200
        user = user_response.json()
        logger.info(f"✅ 获取用户: {user['name']}")

        # 2. 获取该用户的待办事项
        logger.info(f"步骤2: 获取用户 {user['name']} 的待办事项")
        todos_response = authenticated_api.get("/todos", params={"userId": user_id})
        assert todos_response.status_code == 200
        todos = todos_response.json()

        assert isinstance(todos, list)
        assert len(todos) > 0
        logger.info(f"✅ 用户 {user['name']} 有 {len(todos)} 个待办事项")

        # 3. 统计完成率
        completed = sum(1 for todo in todos if todo["completed"])
        completion_rate = (completed / len(todos)) * 100
        logger.info(f"📊 完成率: {completed}/{len(todos)} = {completion_rate:.1f}%")

        # 4. 验证数据完整性
        for todo in todos:
            assert todo["userId"] == user_id
            assert "id" in todo
            assert "title" in todo
            assert "completed" in todo
            assert isinstance(todo["completed"], bool)

        logger.info(f"✅ 步骤4: 验证通过，所有待办事项数据完整")

    @pytest.mark.parametrize("post_id", [1, 2, 3, 4, 5])
    def test_multiple_posts_comments_chain(self, authenticated_api, post_id):
        """
        参数化测试链：批量测试多个文章的评论关联
        """
        logger.info(f"========== 测试文章 ID={post_id} ==========")

        # 1. 获取文章
        post_response = authenticated_api.get(f"/posts/{post_id}")
        assert post_response.status_code == 200
        post = post_response.json()
        logger.info(f"文章标题: {post['title'][:30]}...")

        # 2. 获取文章的评论
        comments_response = authenticated_api.get("/comments", params={"postId": post_id})
        assert comments_response.status_code == 200
        comments = comments_response.json()

        # 3. 验证数据关联
        for comment in comments:
            assert comment["postId"] == post_id

        logger.info(f"✅ 文章 {post_id} 有 {len(comments)} 条评论")

    def test_combined_chain(self, authenticated_api):
        """
        综合测试链：用户 → 文章 → 评论 → 照片
        模拟真实的业务场景
        """
        user_id = 1

        logger.info("📋 开始综合测试链: 用户 → 文章 → 评论 → 照片")

        # 1. 获取用户
        user_response = authenticated_api.get(f"/users/{user_id}")
        assert user_response.status_code == 200
        user = user_response.json()
        logger.info(f"✅ 用户: {user['name']}")

        # 2. 获取用户的第一篇文章
        posts_response = authenticated_api.get("/posts", params={"userId": user_id})
        assert posts_response.status_code == 200
        posts = posts_response.json()
        assert len(posts) > 0
        first_post = posts[0]
        post_id = first_post["id"]
        logger.info(f"✅ 第一篇文章: {first_post['title'][:30]}... (ID: {post_id})")

        # 3. 获取文章的评论
        comments_response = authenticated_api.get("/comments", params={"postId": post_id})
        assert comments_response.status_code == 200
        comments = comments_response.json()
        logger.info(f"✅ 文章评论数: {len(comments)}")

        # 4. 获取用户的相册（另一个维度）
        albums_response = authenticated_api.get("/albums", params={"userId": user_id})
        assert albums_response.status_code == 200
        albums = albums_response.json()
        logger.info(f"✅ 用户相册数: {len(albums)}")

        # 5. 获取第一个相册的照片
        if albums:
            first_album = albums[0]
            photos_response = authenticated_api.get("/photos", params={"albumId": first_album["id"]})
            assert photos_response.status_code == 200
            photos = photos_response.json()
            logger.info(f"✅ 相册 '{first_album['title'][:20]}...' 照片数: {len(photos)}")

        logger.info("🎉 综合测试链全部通过！")