#!/usr/bin/env python3
"""
run_test.py - Playwright 测试自动执行脚本

功能：
1. 读取 test.env 环境变量
2. 生成带时间戳的测试输出目录
3. 执行 Playwright 测试并捕获输出
4. 汇总测试结果

用法：
    python scripts/run_test.py [--project-path .] [--test-name "01-login-test"]
    python scripts/run_test.py --project-path .  # 执行所有测试
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def load_test_env(project_path):
    """读取测试环境变量"""
    env = {}
    env_path = Path(project_path) / "test.env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env


def generate_output_dir(project_path):
    """生成带时间戳的输出目录"""
    ts = datetime.now().strftime("%Y%m%d%H%M")
    output_dir = Path(project_path) / "test" / "output" / ts
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)


def collect_tests(project_path):
    """收集所有测试文件"""
    test_root = Path(project_path) / "test" / "playwright"
    if not test_root.exists():
        return []

    tests = []
    for py_file in sorted(test_root.rglob("*-test.py")):
        rel = py_file.relative_to(test_root)
        tests.append({
            "path": str(py_file),
            "rel_path": str(rel),
            "module": str(rel).replace(os.sep, ".").replace(".py", ""),
        })
    return tests


def run_single_test(test_info, project_path, output_dir, test_env):
    """执行单个测试文件"""
    # 为每个测试创建独立的子输出目录
    test_output = Path(output_dir) / Path(test_info["rel_path"]).parent.name
    test_output.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.update(test_env)
    env["TEST_OUTPUT_DIR"] = str(test_output)
    env["TEST_BACKEND_URL"] = f"http://localhost:{test_env.get('TEST_BACKEND_PORT', '60001')}"

    result = {
        "test": test_info["rel_path"],
        "output_dir": str(test_output),
        "status": "unknown",
        "duration_ms": 0,
        "assertions": [],
        "console_errors": [],
        "timestamp": datetime.now().isoformat(),
    }

    start = time.time()
    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", test_info["path"], "-v", "--tb=short"],
            cwd=project_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        result["duration_ms"] = int((time.time() - start) * 1000)
        result["status"] = "passed" if proc.returncode == 0 else "failed"
        result["stdout"] = proc.stdout
        result["stderr"] = proc.stderr

        # 解析 pytest 输出
        for line in proc.stdout.splitlines():
            if "PASSED" in line or "FAILED" in line:
                result["assertions"].append({"text": line.strip(), "passed": "PASSED" in line})

    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["duration_ms"] = 120000
        result["stderr"] = "测试执行超时（120秒）"
    except Exception as e:
        result["status"] = "error"
        result["stderr"] = str(e)

    # 保存测试结果
    result_path = test_output / "result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def aggregate_results(results, output_dir):
    """汇总测试结果"""
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] in ("failed", "error", "timeout"))

    summary = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed}/{total}" if total > 0 else "0/0",
        "tests": results,
        "timestamp": datetime.now().isoformat(),
    }

    summary_path = Path(output_dir) / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 打印摘要
    print(f"\n{'='*60}")
    print(f"测试结果摘要")
    print(f"{'='*60}")
    print(f"总测试数: {total}")
    print(f"通过:     {passed} {'✓' if passed == total else ''}")
    print(f"失败:     {failed} {'✗' if failed > 0 else ''}")
    print(f"输出目录: {output_dir}")
    print(f"{'='*60}")

    for r in results:
        status_icon = {"passed": "✓", "failed": "✗", "error": "✗", "timeout": "⏱"}.get(r["status"], "?")
        duration = r["duration_ms"] / 1000
        print(f"  {status_icon} {r['test']} ({duration:.1f}s) - {r['status']}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="运行 Playwright 测试")
    parser.add_argument("--project-path", default=".", help="项目根目录")
    parser.add_argument("--test-name", help="仅运行指定测试（部分匹配）")
    parser.add_argument("--skip-env-check", action="store_true", help="跳过环境就绪检查")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    print(f"项目路径: {project_path}")

    # 加载环境变量
    test_env = load_test_env(project_path)
    if not test_env:
        print("错误: test.env 未找到。请先运行 setup_test_env.py 初始化测试环境。")
        sys.exit(1)

    # 生成输出目录
    output_dir = generate_output_dir(project_path)
    print(f"测试输出目录: {output_dir}")
    test_env["TEST_OUTPUT_DIR"] = output_dir

    # 收集测试
    all_tests = collect_tests(project_path)
    if not all_tests:
        print("错误: 未找到任何测试文件 (test/playwright/*-test.py)")
        sys.exit(1)

    if args.test_name:
        tests_to_run = [t for t in all_tests if args.test_name in t["rel_path"]]
        if not tests_to_run:
            print(f"错误: 未找到匹配 '{args.test_name}' 的测试")
            sys.exit(1)
    else:
        tests_to_run = all_tests

    print(f"找到 {len(tests_to_run)} 个测试")
    for t in tests_to_run:
        print(f"  - {t['rel_path']}")

    # 执行测试
    print(f"\n开始执行测试...\n")
    results = []
    for test_info in tests_to_run:
        print(f"运行: {test_info['rel_path']}")
        result = run_single_test(test_info, project_path, output_dir, test_env)
        results.append(result)
        icon = {"passed": "✓", "failed": "✗", "error": "✗", "timeout": "⏱"}.get(result["status"], "?")
        print(f"  {icon} {result['status']} ({result['duration_ms']/1000:.1f}s)")

    # 汇总结果
    aggregate_results(results, output_dir)


if __name__ == "__main__":
    main()
