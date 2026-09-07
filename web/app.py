"""
可视化测试平台 - Flask 应用入口
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from web.config import Config
from web.models import db
from web.routes import register_blueprints

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.config.from_object(Config)

CORS(app)
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

register_blueprints(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


from web.socket_events import register_socket_events
register_socket_events(socketio)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )