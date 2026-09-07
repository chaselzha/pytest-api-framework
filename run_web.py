#!/usr/bin/env python
"""
可视化测试平台启动入口 - 使用 Flask 原生方式
"""
import sys
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from web.app import app


def main():
    parser = argparse.ArgumentParser(description='API 测试可视化平台')
    parser.add_argument('--host', default='127.0.0.1', help='监听地址')
    parser.add_argument('--port', type=int, default=5001, help='监听端口')
    parser.add_argument('--debug', action='store_true', default=True, help='调试模式')
    args = parser.parse_args()
    
    print("=" * 60)
    print("  🧪 API 测试可视化平台")
    print("=" * 60)
    print(f"  🌐 地址: http://{args.host}:{args.port}")
    print(f"  📁 项目: {BASE_DIR}")
    print("=" * 60)
    print("  💡 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 使用 Flask 原生方式启动
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
