"""
路由注册
"""
from flask import Blueprint
from web.routes.test_routes import test_bp
from web.routes.report_routes import report_bp
from web.routes.project_routes import project_bp


def register_blueprints(app):
    app.register_blueprint(test_bp, url_prefix='/api/tests')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(project_bp, url_prefix='/api/projects')
