import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
from web.models import db, TestRun, TestCase

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))


class TestRunner:
    def __init__(self, suite_id, run_id):
        self.suite_id = suite_id
        self.run_id = run_id
        self.output = []
    
    def execute(self):
        from web.socket_events import emit_log, emit_test_progress
        from web.app import app
        
        with app.app_context():
            try:
                emit_log(self.run_id, 'info', '🚀 开始执行测试...')
                
                # 生成带时间戳的报告文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"report_{self.run_id}_{timestamp}.html"
                report_path = f"reports/{report_filename}"
                
                cmd = [
                    sys.executable, '-m', 'pytest',
                    'tests/test_jsonplaceholder_api.py',
                    '-v',
                    '--tb=short',
                    f'--html={report_path}',
                    '--self-contained-html'
                ]
                
                emit_log(self.run_id, 'info', f'📋 执行命令: {" ".join(cmd)}')
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(BASE_DIR)
                )
                
                passed = 0
                failed = 0
                passed_tests = []
                failed_tests = []
                
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.output.append(line)
                        emit_log(self.run_id, 'info', line.strip())
                        
                        if 'PASSED' in line:
                            passed += 1
                            emit_test_progress(self.run_id, 'passed')
                            match = re.search(r'(\w+)\[.*?\]\s+PASSED', line)
                            if not match:
                                match = re.search(r'(\w+)\s+PASSED', line)
                            if match:
                                passed_tests.append(match.group(1))
                        elif 'FAILED' in line:
                            failed += 1
                            emit_test_progress(self.run_id, 'failed')
                            match = re.search(r'(\w+)\[.*?\]\s+FAILED', line)
                            if not match:
                                match = re.search(r'(\w+)\s+FAILED', line)
                            if match:
                                failed_tests.append(match.group(1))
                
                process.wait()
                
                # 更新 TestRun
                test_run = TestRun.query.get(self.run_id)
                if test_run:
                    test_run.status = 'completed' if process.returncode == 0 else 'failed'
                    test_run.finished_at = datetime.now()
                    test_run.passed = passed
                    test_run.failed = failed
                    test_run.total = passed + failed
                    test_run.report_path = report_path
                    db.session.commit()
                
                # 更新 TestCase 状态
                suite = TestCase.query.filter_by(suite_id=self.suite_id).all()
                for case in suite:
                    func_name = case.function_name or case.name
                    is_passed = any(func_name in pt or pt in func_name for pt in passed_tests)
                    is_failed = any(func_name in ft or ft in func_name for ft in failed_tests)
                    if is_passed:
                        case.status = 'passed'
                        case.last_result = 'passed'
                        case.last_run_at = datetime.now()
                    elif is_failed:
                        case.status = 'failed'
                        case.last_result = 'failed'
                        case.last_run_at = datetime.now()
                db.session.commit()
                
                emit_log(self.run_id, 'info', f'✅ 测试执行完成！')
                emit_log(self.run_id, 'info', f'📊 通过: {passed}, 失败: {failed}')
                emit_log(self.run_id, 'info', f'📁 报告: {report_path}')
                
            except Exception as e:
                emit_log(self.run_id, 'error', f'❌ 执行失败: {str(e)}')
