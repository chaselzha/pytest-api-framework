pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
        ALLURE_VERSION = '2.29.0'
        ALLURE_RESULTS_DIR = 'allure-results'
        ALLURE_REPORT_DIR = 'allure-report'
        WORKSPACE = pwd()
    }

    parameters {
        string(
            name: 'BRANCH',
            defaultValue: 'main',
            description: 'Git 分支'
        )
        string(
            name: 'COMMIT',
            defaultValue: '',
            description: 'Git Commit ID'
        )
        choice(
            name: 'TEST_MARKER',
            choices: ['all', 'smoke', 'regression', 'schema', 'chain'],
            description: '测试标记'
        )
        booleanParam(
            name: 'SKIP_INSTALL',
            defaultValue: false,
            description: '跳过依赖安装'
        )
        booleanParam(
            name: 'DEPLOY_REPORT',
            defaultValue: false,
            description: '是否部署报告'
        )
    }

    stages {
        stage('代码检出') {
            steps {
                script {
                    if (params.BRANCH != '') {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/${params.BRANCH}"]],
                            extensions: [],
                            userRemoteConfigs: [[url: 'git@github.com:chaselzha/pytest-api-framework.git']]
                        ])
                    } else {
                        checkout scm
                    }
                }
                echo "📁 代码检出完成，分支: ${params.BRANCH}"
            }
        }

        stage('环境准备') {
            steps {
                script {
                    if (!params.SKIP_INSTALL) {
                        sh '''
                            echo "🐍 设置 Python 虚拟环境..."
                            if [ ! -d ".venv" ]; then
                                python3 -m venv .venv
                            fi
                            source .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt

                            echo "📊 安装 Allure..."
                            if [ ! -d "/opt/allure-${ALLURE_VERSION}" ]; then
                                wget -q https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip
                                unzip -q allure-${ALLURE_VERSION}.zip -d /opt/
                            fi
                            export PATH="/opt/allure-${ALLURE_VERSION}/bin:\$PATH"
                            allure --version
                        '''
                    }
                }
            }
        }

        stage('代码质量检查') {
            steps {
                sh '''
                    source .venv/bin/activate
                    echo "🔍 运行代码质量检查..."
                    pip install flake8
                    flake8 common/ --max-line-length=120 --count --statistics || true
                    flake8 tests/ --max-line-length=120 --count --statistics || true
                '''
            }
        }

        stage('运行测试') {
            steps {
                script {
                    def marker = params.TEST_MARKER == 'all' ? '' : "-m ${params.TEST_MARKER}"
                    sh """
                        source .venv/bin/activate
                        echo "🚀 开始运行测试..."
                        mkdir -p reports
                        export PATH="/opt/allure-${ALLURE_VERSION}/bin:\$PATH"
                        pytest tests/ ${marker} -v \\
                            --alluredir=${ALLURE_RESULTS_DIR} \\
                            --maxfail=5 \\
                            --tb=short \\
                            --html=reports/report.html
                    """
                }
            }
            post {
                always {
                    // 发布 HTML 报告
                    publishHTML([
                        reportDir: 'reports',
                        reportFiles: 'report.html',
                        reportName: 'Pytest HTML 报告',
                        reportTitles: '测试报告',
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ])
                }
            }
        }

        stage('生成 Allure 报告') {
            steps {
                sh '''
                    export PATH="/opt/allure-${ALLURE_VERSION}/bin:\$PATH"
                    echo "📊 生成 Allure 报告..."
                    /opt/allure-${ALLURE_VERSION}/bin/allure generate ${ALLURE_RESULTS_DIR} -o ${ALLURE_REPORT_DIR} --clean
                '''
            }
            post {
                always {
                    // 发布 Allure 报告
                    allure([
                        includeProperties: false,
                        jdk: '',
                        report: 'allure-report',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }

        stage('部署报告') {
            when {
                expression { params.DEPLOY_REPORT == true && env.BRANCH_NAME == 'main' }
            }
            steps {
                sh '''
                    echo "📤 部署报告到服务器..."
                    # 示例：部署到 Nginx
                    # rsync -avz allure-report/ user@server:/var/www/html/api-test/
                    echo "✅ 报告部署完成"
                '''
            }
        }
    }

    post {
        always {
            script {
                // 归档工件
                archiveArtifacts(
                    artifacts: 'allure-results/*, allure-report/*, reports/*, logs/*',
                    allowEmptyArchive: true,
                    fingerprint: true
                )
                echo "📦 工件归档完成"
            }
        }

        failure {
            script {
                // 发送失败邮件通知
                emailext(
                    subject: "❌ Jenkins 构建失败: ${env.JOB_NAME} - #${env.BUILD_NUMBER}",
                    body: """
                        <h2>❌ 构建失败</h2>
                        <ul>
                            <li><b>项目:</b> ${env.JOB_NAME}</li>
                            <li><b>构建编号:</b> #${env.BUILD_NUMBER}</li>
                            <li><b>分支:</b> ${params.BRANCH}</li>
                            <li><b>测试标记:</b> ${params.TEST_MARKER}</li>
                            <li><b>查看详情:</b> <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></li>
                            <li><b>Allure 报告:</b> <a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></li>
                        </ul>
                    """,
                    to: 'cherryccc0327@gmail.com',
                    replyTo: 'cherryccc0327@gmail.com'
                )
                echo "📧 失败通知已发送"
            }
        }

        success {
            script {
                // 发送成功邮件通知
                emailext(
                    subject: "✅ Jenkins 构建成功: ${env.JOB_NAME} - #${env.BUILD_NUMBER}",
                    body: """
                        <h2>✅ 构建成功</h2>
                        <ul>
                            <li><b>项目:</b> ${env.JOB_NAME}</li>
                            <li><b>构建编号:</b> #${env.BUILD_NUMBER}</li>
                            <li><b>分支:</b> ${params.BRANCH}</li>
                            <li><b>测试标记:</b> ${params.TEST_MARKER}</li>
                            <li><b>查看 Allure 报告:</b> <a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></li>
                        </ul>
                    """,
                    to: 'cherryccc0327@gmail.com',
                    replyTo: 'cherryccc0327@gmail.com'
                )
                echo "📧 成功通知已发送"
            }
        }

        cleanup {
            script {
                // 清理工作空间（可选）
                // cleanWs()
                echo "🧹 清理完成"
            }
        }
    }
}