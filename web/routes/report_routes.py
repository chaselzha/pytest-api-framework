"""
测试报告 API
"""
import os
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file
from web.models import db, TestRun
from sqlalchemy import func
from datetime import datetime, timedelta

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

report_bp = Blueprint('reports', __name__)


@report_bp.route('/<int:run_id>', methods=['GET'])
def get_report(run_id):
    test_run = TestRun.query.get(run_id)
    if not test_run:
        return jsonify({'code': 404, 'message': '报告不存在'}), 404
    return jsonify({'code': 0, 'data': test_run.to_dict()})


@report_bp.route('/<int:run_id>/html', methods=['GET'])
def get_report_html(run_id):
    test_run = TestRun.query.get(run_id)
    if not test_run or not test_run.report_path:
        return jsonify({'code': 404, 'message': '报告文件不存在'}), 404
    
    # 使用项目根目录拼接路径
    report_path = BASE_DIR / test_run.report_path
    if report_path.exists():
        return send_file(str(report_path), mimetype='text/html')
    
    return jsonify({'code': 404, 'message': f'报告文件不存在: {report_path}'}), 404


@report_bp.route('/statistics', methods=['GET'])
def get_statistics():
    total_runs = TestRun.query.count()
    total_passed = db.session.query(func.sum(TestRun.passed)).scalar() or 0
    total_failed = db.session.query(func.sum(TestRun.failed)).scalar() or 0
    
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_runs = TestRun.query.filter(TestRun.started_at >= seven_days_ago).order_by(TestRun.started_at.asc()).all()
    
    trend = []
    for run in recent_runs:
        trend.append({
            'date': run.started_at.strftime('%Y-%m-%d'),
            'passed': run.passed,
            'failed': run.failed,
            'total': run.total
        })
    
    return jsonify({
        'code': 0,
        'data': {
            'total_runs': total_runs,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'avg_pass_rate': round((total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0, 2),
            'trend': trend
        }
    })
