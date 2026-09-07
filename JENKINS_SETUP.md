# 🔧 Jenkins 配置指南

[![Jenkins](https://img.shields.io/badge/Jenkins-2.375%2B-blue)](https://www.jenkins.io/)
[![Allure](https://img.shields.io/badge/Allure-2.29.0-orange)](https://allurereport.org/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-green)](https://www.python.org/)

---

## 📋 目录

- [前提条件](#prerequisites)
- [安装 Allure](#install-allure)
- [安装 Jenkins 插件](#install-plugins)
- [配置 Jenkins 任务](#configure-job)
- [配置凭证](#configure-credentials)
- [触发构建](#trigger-build)
- [查看报告](#view-reports)
- [通知配置](#notifications)
- [常见问题](#faq-jenkins)

---

## <span id="prerequisites">📋 前提条件</span>

| 项目 | 要求 |
|------|------|
| Jenkins | 2.375 或更高版本 |
| Python | 3.10 / 3.11 |
| Git | 2.30 或更高版本 |
| Allure | 2.29.0 或更高版本 |

### 已安装的 Jenkins 插件

| 插件 | 用途 |
|------|------|
| **Pipeline** | Pipeline 支持 |
| **Git** | Git 集成 |
| **Allure Jenkins Plugin** | Allure 报告 |
| **HTML Publisher Plugin** | HTML 报告发布 |
| **Email Extension Plugin** | 邮件通知 |
| **GitHub Integration Plugin** | GitHub 集成 |

---

## <span id="install-allure">1️⃣ 安装 Allure</span>

### Linux (Ubuntu/Debian)

```bash
# 下载 Allure
wget https://github.com/allure-framework/allure2/releases/download/2.29.0/allure-2.29.0.zip

# 解压到 /opt
sudo unzip allure-2.29.0.zip -d /opt/

# 创建软链接
sudo ln -s /opt/allure-2.29.0/bin/allure /usr/local/bin/allure

# 验证安装
allure --version

# 清理
rm allure-2.29.0.zip
macOS
bash
# 使用 Homebrew 安装
brew install allure

# 验证安装
allure --version
Windows
bash
# 使用 Scoop 安装
scoop install allure

# 验证安装
allure --version
<span id="install-plugins">2️⃣ 安装 Jenkins 插件</span>
方式一：通过 Jenkins 管理界面
打开 Jenkins → 管理 Jenkins → 插件管理

切换到 可选插件 选项卡

搜索并安装以下插件：

插件名称	必需
Allure Jenkins Plugin	✅ 是
HTML Publisher Plugin	✅ 是
Email Extension Plugin	✅ 是
Pipeline	✅ 是
Git	✅ 是
GitHub Integration Plugin	推荐
GitHub Branch Source Plugin	推荐
Dingding Notification Plugin	可选
Slack Notification Plugin	可选
安装完成后重启 Jenkins

方式二：使用插件管理器 CLI
bash
# 下载插件管理器
wget https://github.com/jenkinsci/plugin-installation-manager-tool/releases/latest/download/jenkins-plugin-manager-2.12.11.jar

# 安装插件
java -jar jenkins-plugin-manager-2.12.11.jar \
  --plugin-file jenkins_plugins.txt \
  --war /usr/share/jenkins/jenkins.war
<span id="configure-job">3️⃣ 配置 Jenkins 任务</span>
步骤 1：新建 Pipeline 任务
打开 Jenkins 首页

点击 新建任务

输入任务名称：pytest-api-framework

选择 Pipeline

点击 确定

步骤 2：配置 Pipeline
方式 A：从 SCM 加载（推荐）

在任务配置页面，找到 Pipeline 部分

Definition 选择：Pipeline script from SCM

SCM 选择：Git

配置 Git 仓库：

Repository URL：git@github.com:chaselzha/pytest-api-framework.git

Credentials：选择已配置的 SSH 密钥（或点击添加）

Branches to build：*/main

Script Path：Jenkinsfile

点击 保存

方式 B：直接输入脚本

在任务配置页面，找到 Pipeline 部分

Definition 选择：Pipeline script

在 Script 框中粘贴 Jenkinsfile 的内容

点击 保存

步骤 3：配置构建参数
Jenkinsfile 已包含以下参数，会自动显示在构建页面：

参数	类型	默认值	说明
BRANCH	String	main	Git 分支
COMMIT	String	(空)	Git Commit ID
TEST_MARKER	Choice	all	测试标记
SKIP_INSTALL	Boolean	false	跳过依赖安装
DEPLOY_REPORT	Boolean	false	是否部署报告
<span id="configure-credentials">4️⃣ 配置凭证</span>
配置 GitHub SSH 密钥
Jenkins → 管理 Jenkins → 凭证

点击 系统 → 全局凭证 → 添加凭证

选择 Kind：SSH Username with private key

填写信息：

ID：github-ssh-key

Description：GitHub SSH Key

Username：git

Private Key：粘贴 GitHub 私钥（~/.ssh/id_rsa）

点击 创建

配置 GitHub Token（备用）
Jenkins → 管理 Jenkins → 凭证

点击 系统 → 全局凭证 → 添加凭证

选择 Kind：Secret text

填写信息：

Secret：粘贴 GitHub Personal Access Token

ID：github-token

Description：GitHub Token

点击 创建

配置邮件服务器
Jenkins → 管理 Jenkins → 系统配置

找到 邮件通知 / E-mail Notification

配置：

SMTP 服务器：smtp.gmail.com（或其他邮件服务器）

默认后缀：@example.com

用户名：your-email@gmail.com

密码：your-app-password

SSL/TLS：勾选 Use SSL

端口：465

点击 保存

<span id="trigger-build">5️⃣ 触发构建</span>
方式一：手动触发
打开 Jenkins 任务页面

点击 Build with Parameters

选择参数值

点击 Build

方式二：API 触发
bash
# 触发构建
curl -X POST \
  "https://jenkins.example.com/job/pytest-api-framework/buildWithParameters" \
  --user "username:api_token" \
  --data-urlencode "BRANCH=main" \
  --data-urlencode "TEST_MARKER=smoke" \
  --data-urlencode "DEPLOY_REPORT=false"
方式三：使用脚本触发
bash
# 设置环境变量
export JENKINS_URL="https://jenkins.example.com"
export JENKINS_USER="your-username"
export JENKINS_TOKEN="your-api-token"
export BRANCH="main"
export TEST_MARKER="smoke"

# 执行触发脚本
./scripts/jenkins_trigger.sh
方式四：GitHub Webhook 触发
在 Jenkins 任务配置中，勾选 GitHub hook trigger for GITScm polling

在 GitHub 仓库设置 Webhook：

Payload URL：https://jenkins.example.com/github-webhook/

Content type：application/json

Events：Just the push event

保存设置

<span id="view-reports">6️⃣ 查看报告</span>
Allure 报告（推荐）
打开 Jenkins 构建页面

在构建历史中点击构建编号

点击 Allure Report 链接

查看详细测试报告

报告内容：

测试用例总数、通过率

测试分类（Epic/Feature/Story）

测试严重性分布

失败用例详情

测试执行时间

HTML 报告
打开 Jenkins 构建页面

点击 Pytest HTML 报告 链接

查看测试结果

日志文件
打开 Jenkins 构建页面

点击 控制台输出

查看详细执行日志

归档工件
打开 Jenkins 构建页面

点击 Artifacts 链接

下载以下文件：

allure-results/ - Allure 原始数据

allure-report/ - Allure 报告

reports/report.html - HTML 报告

logs/ - 日志文件

<span id="notifications">7️⃣ 通知配置</span>
邮件通知
Jenkinsfile 中已配置邮件通知：

groovy
emailext(
    subject: "✅ Jenkins 构建成功: ${env.JOB_NAME} - #${env.BUILD_NUMBER}",
    body: """
        <h2>✅ 构建成功</h2>
        <ul>
            <li><b>项目:</b> ${env.JOB_NAME}</li>
            <li><b>构建编号:</b> #${env.BUILD_NUMBER}</li>
            <li><b>分支:</b> ${params.BRANCH}</li>
            <li><b>查看 Allure 报告:</b> <a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></li>
        </ul>
    """,
    to: 'team@example.com'
)
修改收件人：将 team@example.com 改为实际邮箱

钉钉通知（可选）
安装钉钉插件后，添加以下配置：

groovy
dingtalk(
    robot: 'default',
    type: 'markdown',
    title: '✅ API 测试完成',
    text: """
        ## ✅ 构建成功
        > **项目**: ${env.JOB_NAME}
        > **构建**: #${env.BUILD_NUMBER}
        > **分支**: ${params.BRANCH}
        > **查看**: ${env.BUILD_URL}
    """
)
企业微信通知（可选）
groovy
wechatWork(
    webhookUrl: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx',
    msgType: 'markdown',
    content: """
        ## ✅ 构建成功
        > 项目: ${env.JOB_NAME}
        > 构建: #${env.BUILD_NUMBER}
        > 分支: ${params.BRANCH}
        > [查看详情](${env.BUILD_URL})
    """
)
<span id="faq-jenkins">❓ 常见问题</span>
Q1: Allure 报告未生成
错误：allure: command not found

解决：

bash
# 检查 Allure 是否安装
allure --version

# 如果未安装，使用以下命令安装
# macOS
brew install allure

# Ubuntu
sudo apt-get install allure

# 检查 Jenkins 中 Allure 插件是否安装
# 管理 Jenkins → 插件管理 → 已安装
Q2: 无法拉取 GitHub 代码
错误：Permission denied (publickey)

解决：

bash
# 测试 SSH 连接
ssh -T git@github.com

# 如果没有输出 "Hi username"，配置 SSH 密钥
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
cat ~/.ssh/id_rsa.pub

# 将公钥添加到 GitHub
# GitHub → Settings → SSH and GPG keys → New SSH Key
Q3: 邮件通知未发送
错误：Failed to send email

解决：

检查邮件服务器配置

检查发件人邮箱权限

检查防火墙设置

使用测试邮件功能验证

Q4: 构建参数未生效
问题：参数值没有传递给 Pipeline

解决：

确保 Jenkinsfile 中使用了 params.参数名

检查参数名称拼写

在 Pipeline 开始处打印参数值调试

groovy
pipeline {
    stages {
        stage('Debug') {
            steps {
                echo "BRANCH: ${params.BRANCH}"
                echo "TEST_MARKER: ${params.TEST_MARKER}"
            }
        }
    }
}
Q5: 构建超时
问题：长时间运行导致构建超时

解决：添加超时配置

groovy
options {
    timeout(time: 30, unit: 'MINUTES')
}
Q6: 并行构建冲突
问题：多个构建同时运行时产生冲突

解决：禁用并发构建

groovy
options {
    disableConcurrentBuilds()
}
Q7: 依赖安装失败
问题：pip install 超时或失败

解决：

groovy
stage('环境准备') {
    steps {
        sh '''
            pip install --upgrade pip
            pip install -r requirements.txt --timeout 100
        '''
    }
}
Q8: 构建历史过多
问题：构建历史占用大量磁盘空间

解决：配置构建保留策略

groovy
properties([
    buildDiscarder(
        logRotator(
            numToKeepStr: '30',
            daysToKeepStr: '90',
            artifactNumToKeepStr: '30'
        )
    )
])
📞 获取帮助
Jenkins 文档：https://www.jenkins.io/doc/

Allure 文档：https://allurereport.org/docs/

项目 GitHub：https://github.com/chaselzha/pytest-api-framework

Happy Testing! 🚀
