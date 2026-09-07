"""
WebSocket 事件处理
"""
from datetime import datetime
from flask import request
from flask_socketio import emit, join_room, leave_room

connected_clients = {}


def register_socket_events(socketio):
    
    @socketio.on('connect')
    def handle_connect():
        connected_clients[request.sid] = {'rooms': []}
        emit('connected', {'status': 'ok'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        if request.sid in connected_clients:
            del connected_clients[request.sid]
    
    @socketio.on('join_run')
    def handle_join_run(data):
        run_id = data.get('run_id')
        if run_id:
            room = f'run_{run_id}'
            join_room(room)
            if request.sid in connected_clients:
                connected_clients[request.sid]['rooms'].append(room)
            emit('joined', {'run_id': run_id}, room=room)


def emit_log(run_id, level, message):
    try:
        emit('log', {
            'run_id': run_id,
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=f'run_{run_id}')
    except:
        pass


def emit_test_progress(run_id, status):
    try:
        emit('progress', {
            'run_id': run_id,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }, room=f'run_{run_id}')
    except:
        pass
