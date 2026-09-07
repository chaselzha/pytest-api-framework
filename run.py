#!/usr/bin/env python
"""
测试执行入口
Usage:
    python run.py              # 执行所有测试
    python run.py -m smoke     # 执行冒烟测试
    python run.py -k user      # 执行包含user的测试
    python run.py -n 4         # 并行执行(4进程)
"""
import sys
import pytest
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='API自动化测试执行器')
    parser.add_argument('-m', '--marker', help='执行特定标记的测试，如: smoke, regression')
    parser.add_argument('-k', '--keyword', help='执行匹配关键字的测试')
    parser.add_argument('-n', '--workers', type=int, default=1, help='并行执行进程数')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--html', help='指定HTML报告路径')
    parser.add_argument('--alluredir', help='Allure报告目录')
    parser.add_argument('--failfast', action='store_true', help='遇到第一个失败就停止')

    args = parser.parse_args()

    # 构建pytest参数
    pytest_args = []

    if args.marker:
        pytest_args.extend(['-m', args.marker])

    if args.keyword:
        pytest_args.extend(['-k', args.keyword])

    if args.workers > 1:
        pytest_args.extend(['-n', str(args.workers)])

    if args.verbose:
        pytest_args.append('-v')

    if args.html:
        pytest_args.extend(['--html', args.html, '--self-contained-html'])

    if args.alluredir:
        pytest_args.extend(['--alluredir', args.alluredir])

    if args.failfast:
        pytest_args.append('--maxfail=1')

    # 执行测试
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()