#!/bin/bash
# 触发 Jenkins 构建脚本

set -e

echo "=========================================="
echo "  触发 Jenkins 构建"
echo "=========================================="

# 配置信息
JENKINS_URL="${JENKINS_URL:-https://jenkins.example.com}"
JOB_NAME="${JOB_NAME:-api-test}"
BRANCH="${BRANCH:-main}"
TEST_MARKER="${TEST_MARKER:-all}"

# 检查 Jenkins 凭证
if [ -z "$JENKINS_USER" ] || [ -z "$JENKINS_TOKEN" ]; then
    echo "❌ 请设置 JENKINS_USER 和 JENKINS_TOKEN 环境变量"
    exit 1
fi

echo "📊 Jenkins URL: $JENKINS_URL"
echo "📊 Job Name: $JOB_NAME"
echo "📊 Branch: $BRANCH"
echo "📊 Test Marker: $TEST_MARKER"

# 触发构建
curl -X POST \
    "${JENKINS_URL}/job/${JOB_NAME}/buildWithParameters" \
    --user "${JENKINS_USER}:${JENKINS_TOKEN}" \
    --data-urlencode "BRANCH=${BRANCH}" \
    --data-urlencode "TEST_MARKER=${TEST_MARKER}" \
    --data-urlencode "DEPLOY_REPORT=false"

echo ""
echo "✅ Jenkins 构建已触发！"