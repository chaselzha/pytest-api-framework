#!/usr/bin/env python
"""
Allure 测试报告执行器
Usage:
    python run_allure.py              # 执行所有测试并生成 Allure 报告
    python run_allure.py -m smoke     # 执行冒烟测试
    python run_allure.py --clean      # 清理旧数据并重新生成报告
    python run_allure.py --open       # 生成并打开最新的 Allure 报告
    python run_allure.py --no-run     # 只生成报告，不运行测试
"""
import os
import sys
import subprocess
import argparse
import shutil
import webbrowser
from pathlib import Path
from datetime import datetime

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# Allure 目录配置（放在 reports 目录下）
ALLURE_RESULTS_BASE_DIR = BASE_DIR / "reports" / "allure-results"
ALLURE_REPORT_BASE_DIR = BASE_DIR / "reports" / "allure-reports"


def get_timestamp():
    """获取当前时间戳字符串（精确到秒）"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_report_dir():
    """获取带时间戳的报告目录"""
    timestamp = get_timestamp()
    return ALLURE_REPORT_BASE_DIR / f"allure-report_{timestamp}"


def get_results_dir():
    """获取带时间戳的结果目录"""
    timestamp = get_timestamp()
    return ALLURE_RESULTS_BASE_DIR / f"allure-results_{timestamp}"


def get_latest_report_dir():
    """获取最新的报告目录"""
    if not ALLURE_REPORT_BASE_DIR.exists():
        return None

    # 获取所有 allure-report_* 目录
    report_dirs = sorted(
        [d for d in ALLURE_REPORT_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("allure-report_")],
        key=lambda x: x.name,
        reverse=True
    )

    if report_dirs:
        return report_dirs[0]
    return None


def get_latest_results_dir():
    """获取最新的结果目录"""
    if not ALLURE_RESULTS_BASE_DIR.exists():
        return None

    results_dirs = sorted(
        [d for d in ALLURE_RESULTS_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("allure-results_")],
        key=lambda x: x.name,
        reverse=True
    )

    if results_dirs:
        return results_dirs[0]
    return None


def ensure_directories():
    """确保基础目录存在"""
    ALLURE_RESULTS_BASE_DIR.mkdir(parents=True, exist_ok=True)
    ALLURE_REPORT_BASE_DIR.mkdir(parents=True, exist_ok=True)


def run_tests(marker=None, keyword=None, workers=1):
    """运行 pytest 并生成 Allure 数据"""
    ensure_directories()

    # 使用带时间戳的结果目录
    results_dir = get_results_dir()
    results_dir.mkdir(parents=True, exist_ok=True)

    pytest_args = ["pytest"]

    if marker:
        pytest_args.extend(["-m", marker])

    if keyword:
        pytest_args.extend(["-k", keyword])

    if workers > 1:
        pytest_args.extend(["-n", str(workers)])

    pytest_args.extend(["--alluredir", str(results_dir)])
    pytest_args.append("-v")

    print(f"🔧 执行命令: {' '.join(pytest_args)}")
    print(f"📁 Allure 数据目录: {results_dir}")

    result = subprocess.call(pytest_args)

    if result == 0:
        # 创建符号链接指向最新的结果目录
        latest_link = ALLURE_RESULTS_BASE_DIR / "latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(results_dir.name, target_is_directory=True)

    return result, results_dir


def generate_report(results_dir=None, report_dir=None):
    """生成 Allure HTML 报告"""
    ensure_directories()

    # 如果没有指定结果目录，使用最新的
    if results_dir is None:
        results_dir = get_latest_results_dir()
        if results_dir is None:
            print("❌ 未找到 Allure 数据，请先运行测试: python run_allure.py")
            return 1

    # 如果没有指定报告目录，创建带时间戳的
    if report_dir is None:
        report_dir = get_report_dir()
        report_dir.mkdir(parents=True, exist_ok=True)

    # 检查 allure 命令是否存在
    if not shutil.which("allure"):
        print("❌ 未安装 allure 命令行工具")
        print("   请执行: brew install allure (macOS)")
        print("   或访问: https://github.com/allure-framework/allure2/releases")
        return 1

    print(f"📊 正在生成 Allure 报告...")
    print(f"📁 数据源: {results_dir}")
    print(f"📁 报告输出: {report_dir}")

    cmd = ["allure", "generate", str(results_dir), "-o", str(report_dir), "--clean"]
    result = subprocess.call(cmd)

    if result == 0:
        report_index = report_dir / "index.html"

        # 创建符号链接指向最新的报告
        latest_link = ALLURE_REPORT_BASE_DIR / "latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(report_dir.name, target_is_directory=True)

        print(f"✅ Allure 报告已生成: {report_index}")
        print(f"📁 报告目录: {report_dir}")

        # 保存报告地址到文件
        report_path_file = ALLURE_REPORT_BASE_DIR / "allure_report_path.txt"
        with open(report_path_file, 'w', encoding='utf-8') as f:
            f.write(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"报告目录: {report_dir.absolute()}\n")
            f.write(f"报告地址: {report_index.absolute()}\n")
            f.write(f"数据目录: {results_dir.absolute()}\n")
        print(f"📄 报告地址已保存: {report_path_file}")

        # 更新最新报告地址文件
        latest_report_file = BASE_DIR / "reports" / "latest_report_path.txt"
        with open(latest_report_file, 'w', encoding='utf-8') as f:
            f.write(f"{report_index.absolute()}\n")

        # 自动打开报告（如果指定）
        return 0, report_dir
    else:
        print("❌ 生成 Allure 报告失败")
        return 1, None


def open_report(report_dir=None):
    """打开 Allure 报告"""
    if report_dir is None:
        # 尝试获取最新的报告
        latest_link = ALLURE_REPORT_BASE_DIR / "latest"
        if latest_link.exists():
            try:
                report_dir = ALLURE_REPORT_BASE_DIR / latest_link.readlink()
            except:
                report_dir = get_latest_report_dir()
        else:
            report_dir = get_latest_report_dir()

    if report_dir is None:
        print("⚠️ 未找到任何报告，请先生成报告: python run_allure.py")
        return 1

    if not shutil.which("allure"):
        print("❌ 未安装 allure 命令行工具")
        return 1

    report_index = report_dir / "index.html"

    # 如果报告不存在，先尝试生成
    if not report_index.exists():
        print("⚠️ 报告不存在，正在生成...")
        if generate_report() != 0:
            return 1
        report_dir = get_latest_report_dir()
        report_index = report_dir / "index.html"

    print(f"🌐 打开报告: {report_index}")

    # 使用 allure open 命令
    cmd = ["allure", "open", str(report_dir)]
    result = subprocess.call(cmd)

    # 如果 allure open 失败，尝试用浏览器直接打开
    if result != 0:
        print("使用浏览器直接打开...")
        webbrowser.open(str(report_index))

    return 0


def clean_dirs():
    """清理旧数据（保留最新的5份报告和结果）"""
    # 清理结果目录
    if ALLURE_RESULTS_BASE_DIR.exists():
        results_dirs = sorted(
            [d for d in ALLURE_RESULTS_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("allure-results_")],
            key=lambda x: x.name,
            reverse=True
        )
        # 保留最新的5份，删除其余的
        for d in results_dirs[5:]:
            shutil.rmtree(d)
            print(f"🧹 已清理: {d}")

    # 清理报告目录
    if ALLURE_REPORT_BASE_DIR.exists():
        report_dirs = sorted(
            [d for d in ALLURE_REPORT_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("allure-report_")],
            key=lambda x: x.name,
            reverse=True
        )
        for d in report_dirs[5:]:
            shutil.rmtree(d)
            print(f"🧹 已清理: {d}")

    # 清理符号链接（但不删除）
    print("✅ 清理完成（保留最新5份）")


def show_report_path():
    """显示最新报告地址"""
    latest_link = ALLURE_REPORT_BASE_DIR / "latest"

    if latest_link.exists():
        try:
            report_dir = ALLURE_REPORT_BASE_DIR / latest_link.readlink()
            report_index = report_dir / "index.html"
            print(f"📊 最新 Allure 报告:")
            print(f"   文件路径: {report_index.absolute()}")
            print(f"   目录路径: {report_dir.absolute()}")

            # 读取报告地址文件
            report_path_file = ALLURE_REPORT_BASE_DIR / "allure_report_path.txt"
            if report_path_file.exists():
                print("\n📄 报告信息:")
                with open(report_path_file, 'r', encoding='utf-8') as f:
                    print(f.read())
        except:
            print("⚠️ 无法读取最新报告链接")
    else:
        # 尝试获取最新的报告目录
        report_dir = get_latest_report_dir()
        if report_dir:
            report_index = report_dir / "index.html"
            print(f"📊 最新 Allure 报告:")
            print(f"   文件路径: {report_index.absolute()}")
            print(f"   目录路径: {report_dir.absolute()}")
        else:
            print("⚠️ 报告尚未生成，请先运行测试: python run_allure.py")


def list_reports():
    """列出所有报告"""
    if not ALLURE_REPORT_BASE_DIR.exists():
        print("⚠️ 暂无报告")
        return

    report_dirs = sorted(
        [d for d in ALLURE_REPORT_BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("allure-report_")],
        key=lambda x: x.name,
        reverse=True
    )

    if not report_dirs:
        print("⚠️ 暂无报告")
        return

    print(f"📁 共有 {len(report_dirs)} 份报告:")
    for d in report_dirs:
        index_file = d / "index.html"
        status = "✅" if index_file.exists() else "❌"
        print(f"   {status} {d.name} -> {index_file.absolute()}")


def main():
    parser = argparse.ArgumentParser(description='Allure 测试报告执行器')
    parser.add_argument('-m', '--marker', help='执行特定标记的测试')
    parser.add_argument('-k', '--keyword', help='执行匹配关键字的测试')
    parser.add_argument('-n', '--workers', type=int, default=1, help='并行执行进程数')
    parser.add_argument('--clean', action='store_true', help='清理旧数据（保留最新5份）')
    parser.add_argument('--open', action='store_true', help='生成并打开最新报告')
    parser.add_argument('--no-run', action='store_true', help='只生成报告，不运行测试')
    parser.add_argument('--show-path', action='store_true', help='显示最新报告地址')
    parser.add_argument('--list', action='store_true', help='列出所有报告')
    parser.add_argument('--clean-all', action='store_true', help='清理所有数据（慎用）')

    args = parser.parse_args()

    # 显示报告地址
    if args.show_path:
        show_report_path()
        return

    # 列出所有报告
    if args.list:
        list_reports()
        return

    # 清理所有数据
    if args.clean_all:
        print("⚠️ 正在清理所有数据...")
        shutil.rmtree(ALLURE_RESULTS_BASE_DIR, ignore_errors=True)
        shutil.rmtree(ALLURE_REPORT_BASE_DIR, ignore_errors=True)
        print("✅ 清理完成")
        return

    # 清理旧数据
    if args.clean:
        clean_dirs()
        if args.no_run and not args.open:
            print("✅ 清理完成")
            return

    # 运行测试
    if not args.no_run:
        print("🚀 开始运行测试...")
        result, results_dir = run_tests(
            marker=args.marker,
            keyword=args.keyword,
            workers=args.workers
        )

        if result != 0:
            print("❌ 测试执行失败")
            sys.exit(result)

    # 生成报告
    generate_report()

    # 打开报告
    if args.open:
        open_report()

    # 显示报告地址
    print("\n" + "=" * 60)
    show_report_path()
    print("=" * 60)

    print("\n🎉 完成！")
    print(f"📊 查看报告: python run_allure.py --open")
    print(f"📋 列出所有报告: python run_allure.py --list")


if __name__ == '__main__':
    main()