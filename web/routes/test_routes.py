import subprocess, threading, re
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from web.models import db, TestSuite, TestCase, TestRun
from web.services.test_runner import TestRunner

test_bp = Blueprint('tests', __name__)

# ===== 套件管理 =====
@test_bp.route('/suites', methods=['GET'])
def get_suites():
    project_id = request.args.get('project_id')
    query = TestSuite.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    suites = query.all()
    return jsonify({'code': 0, 'data': [s.to_dict() for s in suites], 'total': len(suites)})

@test_bp.route('/suites', methods=['POST'])
def create_suite():
    data = request.json
    if not data.get('name') or not data.get('project_id'):
        return jsonify({'code': 400, 'message': '项目ID和名称不能为空'}), 400
    suite = TestSuite(
        project_id=data['project_id'],
        name=data['name'],
        description=data.get('description', ''),
        file_path=data.get('file_path', ''),
        tags=data.get('tags', '')
    )
    db.session.add(suite)
    db.session.commit()
    return jsonify({'code': 0, 'data': suite.to_dict(), 'message': '创建成功'})

@test_bp.route('/suites/<int:suite_id>', methods=['DELETE'])
def delete_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify({'code': 404, 'message': '套件不存在'}), 404
    # 同时删除关联的用例
    TestCase.query.filter_by(suite_id=suite_id).delete()
    db.session.delete(suite)
    db.session.commit()
    return jsonify({'code': 0, 'message': '删除成功'})

# ===== 用例管理 =====
@test_bp.route('/cases', methods=['GET'])
def get_cases():
    suite_id = request.args.get('suite_id')
    status = request.args.get('status')
    query = TestCase.query
    if suite_id:
        query = query.filter_by(suite_id=suite_id)
    if status:
        query = query.filter_by(status=status)
    cases = query.all()
    return jsonify({'code': 0, 'data': [c.to_dict() for c in cases], 'total': len(cases)})

@test_bp.route('/cases', methods=['POST'])
def create_case():
    data = request.json
    if not data.get('name') or not data.get('suite_id'):
        return jsonify({'code': 400, 'message': '用例名称和套件ID不能为空'}), 400
    case = TestCase(
        suite_id=data['suite_id'],
        name=data['name'],
        function_name=data.get('function_name', data['name']),
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        status='pending'
    )
    db.session.add(case)
    db.session.commit()
    return jsonify({'code': 0, 'data': case.to_dict(), 'message': '创建成功'})

@test_bp.route('/cases/<int:case_id>', methods=['DELETE'])
def delete_case(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify({'code': 404, 'message': '用例不存在'}), 404
    db.session.delete(case)
    db.session.commit()
    return jsonify({'code': 0, 'message': '删除成功'})

@test_bp.route('/cases/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    case = TestCase.query.get(case_id)
    if not case:
        return jsonify({'code': 404, 'message': '用例不存在'}), 404
    data = request.json
    if 'name' in data:
        case.name = data['name']
    if 'function_name' in data:
        case.function_name = data['function_name']
    if 'description' in data:
        case.description = data['description']
    if 'priority' in data:
        case.priority = data['priority']
    if 'status' in data:
        case.status = data['status']
    db.session.commit()
    return jsonify({'code': 0, 'data': case.to_dict(), 'message': '更新成功'})

# ===== 执行测试 =====
@test_bp.route('/suites/<int:suite_id>/run', methods=['POST'])
def run_suite(suite_id):
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify({'code': 404, 'message': '套件不存在'}), 404
    data = request.json or {}
    with current_app.app_context():
        test_run = TestRun(
            suite_id=suite_id,
            run_type=data.get('run_type', 'manual'),
            status='running',
            started_at=datetime.now(),
            created_by=data.get('created_by', 'web')
        )
        db.session.add(test_run)
        db.session.commit()
        run_id = test_run.id
    def run_test():
        from web.app import app
        with app.app_context():
            runner = TestRunner(suite_id, run_id)
            runner.execute()
    thread = threading.Thread(target=run_test)
    thread.daemon = True
    thread.start()
    return jsonify({'code': 0, 'data': {'run_id': run_id}, 'message': '测试已启动'})

# ===== 执行历史 =====
@test_bp.route('/runs', methods=['GET'])
def get_runs():
    suite_id = request.args.get('suite_id')
    limit = request.args.get('limit', 50, type=int)
    query = TestRun.query
    if suite_id:
        query = query.filter_by(suite_id=suite_id)
    runs = query.order_by(TestRun.started_at.desc()).limit(limit).all()
    return jsonify({'code': 0, 'data': [r.to_dict() for r in runs], 'total': len(runs)})

# ===== 扫描用例 =====
@test_bp.route('/cases/scan', methods=['POST'])
def scan_cases():
    data = request.json
    suite_id = data.get('suite_id')
    suite = TestSuite.query.get(suite_id)
    if not suite:
        return jsonify({'code': 404, 'message': '套件不存在'}), 404
    file_path = suite.file_path
    if not file_path:
        return jsonify({'code': 400, 'message': '套件未关联测试文件'}), 400
    cmd = ['pytest', file_path, '--collect-only', '-q']
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).resolve().parent.parent.parent))
    patterns = re.findall(r'(\w+::\w+)', result.stdout)
    saved_count = 0
    for p in patterns:
        parts = p.split('::')
        function_name = parts[-1] if len(parts) >= 2 else p
        existing = TestCase.query.filter_by(suite_id=suite_id, function_name=function_name).first()
        if not existing:
            case = TestCase(suite_id=suite_id, name=function_name, function_name=function_name, status='pending')
            db.session.add(case)
            saved_count += 1
    db.session.commit()
    return jsonify({'code': 0, 'data': {'scanned': len(patterns), 'saved': saved_count}, 'message': f'扫描完成，发现 {len(patterns)} 个用例，新增 {saved_count} 个'})
