"""
项目管理 API
"""
from flask import Blueprint, request, jsonify
from web.models import db, TestProject

project_bp = Blueprint('projects', __name__)


@project_bp.route('', methods=['GET'])
def get_projects():
    projects = TestProject.query.all()
    return jsonify({'code': 0, 'data': [p.to_dict() for p in projects], 'total': len(projects)})


@project_bp.route('', methods=['POST'])
def create_project():
    data = request.json
    if not data.get('name'):
        return jsonify({'code': 400, 'message': '项目名称不能为空'}), 400
    project = TestProject(
        name=data['name'],
        description=data.get('description', ''),
        base_url=data.get('base_url', ''),
        env=data.get('env', 'test')
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'code': 0, 'data': project.to_dict(), 'message': '创建成功'})


@project_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = TestProject.query.get(project_id)
    if not project:
        return jsonify({'code': 404, 'message': '项目不存在'}), 404
    data = request.json
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'base_url' in data:
        project.base_url = data['base_url']
    if 'env' in data:
        project.env = data['env']
    if 'status' in data:
        project.status = data['status']
    db.session.commit()
    return jsonify({'code': 0, 'data': project.to_dict(), 'message': '更新成功'})


@project_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = TestProject.query.get(project_id)
    if not project:
        return jsonify({'code': 404, 'message': '项目不存在'}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({'code': 0, 'message': '删除成功'})
