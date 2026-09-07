"""
数据库模型
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TestProject(db.Model):
    """测试项目"""
    __tablename__ = 'test_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_url = db.Column(db.String(200))
    env = db.Column(db.String(20), default='test')
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    test_suites = db.relationship('TestSuite', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'base_url': self.base_url,
            'env': self.env,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'suite_count': len(self.test_suites) if self.test_suites else 0
        }


class TestSuite(db.Model):
    """测试套件"""
    __tablename__ = 'test_suites'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('test_projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(200))
    tags = db.Column(db.String(200))
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    test_cases = db.relationship('TestCase', backref='suite', lazy=True, cascade='all, delete-orphan')
    test_runs = db.relationship('TestRun', backref='suite', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'file_path': self.file_path,
            'tags': self.tags.split(',') if self.tags else [],
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'case_count': len(self.test_cases) if self.test_cases else 0
        }


class TestCase(db.Model):
    """测试用例"""
    __tablename__ = 'test_cases'
    
    id = db.Column(db.Integer, primary_key=True)
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    function_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='pending')
    last_run_at = db.Column(db.DateTime)
    last_result = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'suite_id': self.suite_id,
            'name': self.name,
            'function_name': self.function_name,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'last_result': self.last_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TestRun(db.Model):
    """测试执行记录"""
    __tablename__ = 'test_runs'
    
    id = db.Column(db.Integer, primary_key=True)
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'))
    run_type = db.Column(db.String(20), default='manual')
    status = db.Column(db.String(20), default='running')
    total = db.Column(db.Integer, default=0)
    passed = db.Column(db.Integer, default=0)
    failed = db.Column(db.Integer, default=0)
    skipped = db.Column(db.Integer, default=0)
    duration = db.Column(db.Float, default=0)
    report_path = db.Column(db.String(200))
    log_path = db.Column(db.String(200))
    started_at = db.Column(db.DateTime, default=datetime.now)
    finished_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(50), default='system')
    
    def to_dict(self):
        return {
            'id': self.id,
            'suite_id': self.suite_id,
            'run_type': self.run_type,
            'status': self.status,
            'total': self.total,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'pass_rate': round((self.passed / self.total * 100) if self.total > 0 else 0, 2),
            'duration': self.duration,
            'report_path': self.report_path,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'created_by': self.created_by
        }


class ScheduledJob(db.Model):
    """定时任务"""
    __tablename__ = 'scheduled_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    suite_id = db.Column(db.Integer, db.ForeignKey('test_suites.id'))
    cron_expression = db.Column(db.String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    last_run_at = db.Column(db.DateTime)
    next_run_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'suite_id': self.suite_id,
            'cron_expression': self.cron_expression,
            'enabled': self.enabled,
            'last_run_at': self.last_run_at.isoformat() if self.last_run_at else None,
            'next_run_at': self.next_run_at.isoformat() if self.next_run_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
