# Pytest API 自动化测试框架

基于 Python + Pytest + Requests 构建的企业级 API 自动化测试框架，支持多环境配置、Allure 报告、可视化测试平台、CI/CD 集成。

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4.3-green)](https://docs.pytest.org/)
[![Allure](https://img.shields.io/badge/Allure-2.29.0-orange)](https://allurereport.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightblue)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 目录

- [项目简介](#project-intro)
- [核心特性](#features)
- [技术栈](#tech-stack)
- [项目结构](#project-structure)
- [快速开始](#quick-start)
- [运行测试](#run-tests)
- [可视化测试平台](#web-platform)
- [测试报告](#test-reports)
- [环境配置](#env-config)
- [CI/CD 集成](#cicd-integration)
- [常见问题](#faq)
- [贡献指南](#contributing)
- [许可证](#license)

---

## <span id="project-intro">📖 项目简介</span>

这是一个功能完备的 **API 自动化测试框架**，专为 RESTful API 接口测试设计。框架提供了完整的测试生命周期管理，从接口请求、数据校验、日志记录到报告生成，一站式解决方案。

### 核心能力

| 功能 | 说明 |
|------|------|
| 🔧 **HTTP 客户端** | 封装 Requests，支持 GET/POST/PUT/DELETE |
| 🔄 **自动重试** | 失败请求自动重试（可配置） |
| 🛡️ **数据脱敏** | 密码、Token、手机号等敏感信息自动脱敏 |
| ⏱️ **耗时监控** | 接口响应时间告警（3秒警告，5秒错误） |
| 📋 **JSON Schema 校验** | 接口返回数据结构自动校验 |
| 🔗 **接口关联测试** | 支持接口间数据依赖传递 |
| 📝 **日志系统** | 完整的请求/响应日志（含脱敏） |
| 📊 **Allure 报告** | 美观的测试报告，支持历史追踪 |
| 🌍 **多环境配置** | 支持 dev/test/prod 环境切换 |
| 🖥️ **可视化平台** | Flask Web 界面管理测试用例和执行测试 |
| 🚀 **CI/CD 集成** | GitHub Actions / Jenkins 开箱即用 |

---

## <span id="features">✨ 核心特性</span>

### 1. 数据脱敏

敏感信息自动脱敏，保护数据安全：

| 字段 | 脱敏前 | 脱敏后 |
|------|--------|--------|
| password | `"password":"123456"` | `"password":"***"` |
| token | `"token":"abc123"` | `"token":"***"` |
| phone | `"phone":"13812345678"` | `"phone":"138****5678"` |

### 2. 耗时监控

接口响应时间自动监控：

| 耗时 | 日志级别 |
|------|----------|
| < 3s | INFO |
| 3s ~ 5s | WARNING ⚠️ |
| > 5s | ERROR ❌ |

### 3. JSON Schema 校验

使用 JSON Schema 校验接口返回数据结构：

```python
from common.utils import validate_json_schema

result = validate_json_schema(response.json(), "post_schema.json")
assert result["valid"], result["message"]
```

### 4. 失败自动保存

测试失败时自动保存请求和响应信息：

```
reports/errors/test_name_20260907_220530/
├── request.json
└── response.json
```

### 5. 可视化测试平台

基于 Flask 的 Web 界面，支持：
- 📋 查看测试用例列表
- 📁 添加/删除测试套件
- 📋 添加/删除测试用例
- ▶️ 一键执行测试
- 📊 查看执行历史和统计
- 📈 查看测试报告

---

## <span id="tech-stack">🛠️ 技术栈</span>

| 组件 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10 / 3.11 | 编程语言 |
| **Pytest** | 7.4.3 | 测试框架 |
| **Requests** | 2.31.0 | HTTP 客户端 |
| **Loguru** | 0.7.2 | 日志系统 |
| **Allure** | 2.29.0 | 测试报告 |
| **PyYAML** | 6.0.1 | YAML 数据解析 |
| **Jsonschema** | 4.20.0 | Schema 校验 |
| **Faker** | 20.1.0 | 测试数据生成 |
| **python-dotenv** | 1.0.0 | 环境变量管理 |
| **Flask** | 2.3.3 | Web 框架 |
| **Flask-SQLAlchemy** | 3.1.1 | ORM 数据库 |
| **Flask-CORS** | 4.0.0 | 跨域支持 |

---

## <span id="project-structure">📁 项目结构</span>

```text
pytest-api-framework/
├── .github/workflows/          # GitHub Actions CI/CD
│   └── test.yml
├── config/                     # 配置管理
│   ├── __init__.py
│   └── settings.py             # 多环境配置
├── common/                     # 公共模块
│   ├── __init__.py
│   ├── client.py               # HTTP 客户端（含脱敏、重试）
│   ├── logger.py               # 日志系统
│   └── utils.py                # 工具函数（含 Schema 校验）
├── schemas/                    # JSON Schema 定义
│   ├── post_schema.json
│   ├── user_schema.json
│   └── comment_schema.json
├── testdata/                   # 测试数据
│   ├── user_data.yaml
│   └── jsonplaceholder_data.yaml
├── tests/                      # 测试用例
│   ├── __init__.py
│   ├── conftest.py             # Pytest Fixtures
│   ├── test_jsonplaceholder_api.py  # JSONPlaceholder 测试 (27)
│   ├── test_api_chain.py       # 接口关联测试 (10)
│   └── test_schema_validation.py    # Schema 校验测试 (5)
├── web/                        # 可视化测试平台
│   ├── __init__.py
│   ├── app.py                  # Flask 应用入口
│   ├── config.py               # Web 配置
│   ├── models.py               # 数据库模型
│   ├── routes/                 # API 路由
│   │   ├── __init__.py
│   │   ├── project_routes.py   # 项目管理 API
│   │   ├── report_routes.py    # 报告 API
│   │   └── test_routes.py      # 测试管理 API
│   ├── services/               # 服务层
│   │   ├── __init__.py
│   │   └── test_runner.py      # 测试执行服务
│   ├── templates/              # HTML 模板
│   │   └── index.html          # 前端页面
│   └── data/                   # 数据库
│       └── test_platform.db    # SQLite 数据库
├── reports/                    # 测试报告
│   ├── allure-reports/         # Allure 报告（带时间戳）
│   ├── allure-results/         # Allure 数据
│   ├── errors/                 # 失败保存目录
│   └── report.html             # HTML 测试报告
├── logs/                       # 日志文件（含时分秒）
├── .env                        # 环境变量配置
├── requirements.txt            # 依赖清单
├── pytest.ini                  # Pytest 配置
├── run.py                      # 测试执行入口
├── run_web.py                  # Web 平台启动入口
├── run_allure.py               # Allure 报告执行器
├── Jenkinsfile                 # Jenkins Pipeline
└── README.md                   # 项目说明
```

---

## <span id="quick-start">🚀 快速开始</span>

### 1. 克隆项目

```bash
git clone git@github.com:chaselzha/pytest-api-framework.git
cd pytest-api-framework
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，配置你的 API 地址
```

```env
API_ENV=test
TEST_BASE_URL=https://jsonplaceholder.typicode.com
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

### 5. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行冒烟测试
pytest tests/ -m smoke -v

# 运行指定测试文件
pytest tests/test_jsonplaceholder_api.py -v
```

---

## <span id="run-tests">📊 运行测试</span>

### 基本命令

| 命令 | 说明 |
|------|------|
| `pytest tests/ -v` | 运行所有测试（详细输出） |
| `pytest tests/ -m smoke` | 运行冒烟测试 |
| `pytest tests/ -m regression` | 运行回归测试 |
| `pytest tests/test_xxx.py` | 运行指定测试文件 |
| `pytest tests/ -n 4` | 并行执行（4 进程） |
| `pytest tests/ --maxfail=5` | 失败 5 次后停止 |

### 使用 run.py

```bash
# 运行所有测试
python run.py

# 运行冒烟测试
python run.py -m smoke

# 并行执行（4 进程）
python run.py -n 4

# 生成 HTML 报告
python run.py --html=reports/report.html
```

### 使用 run_allure.py

```bash
# 运行测试并生成 Allure 报告
python run_allure.py --open

# 运行冒烟测试并生成报告
python run_allure.py -m smoke --open

# 清理旧数据（保留最新 5 份）
python run_allure.py --clean

# 查看最新报告地址
python run_allure.py --show-path

# 列出所有报告
python run_allure.py --list

# 清理所有数据（慎用）
python run_allure.py --clean-all
```

---

## <span id="web-platform">🖥️ 可视化测试平台</span>

### 启动 Web 平台

```bash
# 启动可视化测试平台
python run_web.py --port 5001

# 指定地址和端口
python run_web.py --host 0.0.0.0 --port 8080
```

### 访问平台

浏览器打开：`http://localhost:5001`

### 平台功能

| 功能 | 说明 |
|------|------|
| 📊 **统计面板** | 显示总测试数、通过/失败数、通过率 |
| ▶️ **执行测试** | 选择测试套件一键执行 |
| 📋 **测试用例管理** | 查看、添加、删除测试用例 |
| 📁 **测试套件管理** | 查看、添加、删除测试套件 |
| 📋 **执行日志** | 实时查看测试执行日志 |
| 📊 **执行历史** | 查看历史执行记录和通过率 |
| 📈 **测试报告** | 在线查看 HTML 测试报告 |

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/projects` | GET/POST | 项目管理 |
| `/api/tests/suites` | GET/POST/DELETE | 套件管理 |
| `/api/tests/cases` | GET/POST/DELETE | 用例管理 |
| `/api/tests/suites/<id>/run` | POST | 执行测试 |
| `/api/tests/runs` | GET | 执行历史 |
| `/api/reports/<id>/html` | GET | 查看报告 |
| `/api/reports/statistics` | GET | 统计信息 |

---

## <span id="test-reports">📈 测试报告</span>

### Allure 报告（推荐）

```bash
# 安装 Allure (macOS)
brew install allure

# 生成并打开报告
python run_allure.py --open

# 或手动生成
pytest tests/ --alluredir=allure-results
allure generate allure-results -o allure-report --clean
allure open allure-report
```

**报告地址**：`reports/allure-reports/latest/index.html`

### HTML 报告

```bash
# 生成 HTML 报告
pytest tests/ --html=reports/report.html --self-contained-html
```

**报告地址**：`reports/report.html`

### 日志文件

日志文件保存在 `logs/` 目录，按天轮转，文件名包含时分秒：

```
logs/
├── api_test_2026-09-07_22-30-45.log
├── api_test_2026-09-07_23-15-20.log
└── api_error_2026-09-07_22-30-45.log
```

---

## <span id="env-config">🌍 环境配置</span>

### 多环境支持

框架支持 3 种环境，通过 `API_ENV` 环境变量切换：

| 环境 | 变量 | 说明 |
|------|------|------|
| **测试环境** | `API_ENV=test` | 默认，用于 CI/CD |
| **开发环境** | `API_ENV=dev` | 用于本地开发 |
| **生产环境** | `API_ENV=prod` | 谨慎使用 |

### 配置方式

**方式一：.env 文件**

```env
API_ENV=test
TEST_BASE_URL=https://jsonplaceholder.typicode.com
REQUEST_TIMEOUT=30
LOG_LEVEL=INFO
```

**方式二：环境变量**

```bash
API_ENV=dev pytest tests/ -v
```

**方式三：settings.py 硬编码**

```python
# config/settings.py
ENV = "test"  # 默认值
```

---

## <span id="cicd-integration">🔄 CI/CD 集成</span>

### GitHub Actions

项目已配置 GitHub Actions 工作流，每次推送代码自动运行测试。

**配置文件**：`.github/workflows/test.yml`

**触发条件**：
- 推送 `main` / `develop` 分支
- 创建 Pull Request
- 每天 2:00 定时执行
- 手动触发

**查看结果**：
```
https://github.com/chaselzha/pytest-api-framework/actions
```

### Jenkins

**配置文件**：`Jenkinsfile`

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `BRANCH` | String | `main` | Git 分支 |
| `TEST_MARKER` | Choice | `all` | 测试标记 |
| `SKIP_INSTALL` | Boolean | `false` | 跳过依赖安装 |
| `DEPLOY_REPORT` | Boolean | `false` | 是否部署报告 |

**触发方式**：

```bash
# API 触发
curl -X POST "https://jenkins.example.com/job/api-test/buildWithParameters" \
  --user "username:api_token" \
  --data-urlencode "BRANCH=main" \
  --data-urlencode "TEST_MARKER=smoke"
```

**详细配置**：参见 [JENKINS_SETUP.md](JENKINS_SETUP.md)

---

## <span id="faq">❓ 常见问题</span>

### 1. 测试连接失败

**问题**：连接 `test-api.example.com` 失败

**解决**：修改 `config/settings.py` 中的 `BASE_URL`

```python
class TestConfig(Config):
    BASE_URL = "https://your-api-server.com"
```

### 2. Allure 报告未生成

**问题**：`allure: command not found`

**解决**：安装 Allure

```bash
# macOS
brew install allure

# Ubuntu
sudo apt-get install allure

# Windows (Scoop)
scoop install allure
```

### 3. 可视化平台启动失败

**问题**：端口被占用

**解决**：使用其他端口启动

```bash
python run_web.py --port 5002
```

### 4. 依赖安装失败

**问题**：pip 安装依赖失败

**解决**：升级 pip 和 setuptools

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt --no-cache-dir
```

### 5. 数据库表不存在

**问题**：`no such table: test_projects`

**解决**：创建数据库表

```bash
python -c "from web.app import app; from web.models import db; with app.app_context(): db.create_all(); print('✅ 表创建成功')"
```

---

## <span id="contributing">🤝 贡献指南</span>

欢迎贡献代码、提出 Issue 或提交 Pull Request！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 编码规范
- 添加必要的注释和文档
- 编写单元测试覆盖新功能
- 确保所有测试通过

---

## <span id="license">📄 许可证</span>

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📞 联系方式

- **作者**：Chasel Zha
- **GitHub**：[chaselzha](https://github.com/chaselzha)
- **项目地址**：[pytest-api-framework](https://github.com/chaselzha/pytest-api-framework)

---

## ⭐ 支持

如果这个项目对你有帮助，请给个 Star ⭐ 支持一下！

[![Star](https://img.shields.io/github/stars/chaselzha/pytest-api-framework?style=social)](https://github.com/chaselzha/pytest-api-framework)

---

**Happy Testing! 🚀**