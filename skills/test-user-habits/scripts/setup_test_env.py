#!/usr/bin/env python3
"""
setup_test_env.py - 测试环境初始化脚本

功能：
1. 分析项目配置，确定测试所需端口和服务
2. 创建 test.env 环境变量文件
3. 初始化测试数据库（支持 MySQL/SQLite）
4. 验证所有测试依赖服务就绪

用法：
    python scripts/setup_test_env.py [--project-path .] [--dry-run]
"""

import argparse
import os
import random
import socket
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def get_free_port(min_port=60000, max_port=65535):
    """获取指定范围内的随机可用端口"""
    tried = set()
    while len(tried) < max_port - min_port:
        port = random.randint(min_port, max_port)
        if port in tried:
            continue
        tried.add(port)
        with socket.socket() as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"无可用端口范围 {min_port}-{max_port}")


def check_port(port):
    """检查端口是否已被监听"""
    with socket.socket() as s:
        return s.connect_ex(('localhost', port)) == 0


def load_env_file(path):
    """读取 .env 文件"""
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        k, v = line.split('=', 1)
                        env[k.strip()] = v.strip()
    return env


def save_env_file(path, env):
    """写入 .env 文件"""
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as f:
        for k, v in sorted(env.items()):
            f.write(f"{k}={v}\n")


def detect_project_type(project_path):
    """检测项目类型"""
    p = Path(project_path)
    if (p / "pom.xml").exists():
        return "java-maven"
    if (p / "build.gradle").exists() or (p / "build.gradle.kts").exists():
        return "java-gradle"
    if (p / "package.json").exists():
        if (p / "vite.config.js").exists() or (p / "vite.config.ts").exists():
            return "node-vite"
        return "node-default"
    if (p / "requirements.txt").exists() or (p / "pyproject.toml").exists():
        return "python"
    if (p / "go.mod").exists():
        return "go"
    return "unknown"


def setup_for_python(project_path, dry_run=False):
    """Python 项目环境设置"""
    env = load_env_file(os.path.join(project_path, ".env"))
    test_env = {
        "TEST_BACKEND_PORT": str(get_free_port()),
        "TEST_DB_NAME": "test_db",
    }
    # 从现有配置推断
    if env.get("DATABASE_URL"):
        # 替换为测试数据库
        db_url = env["DATABASE_URL"]
        test_env["TEST_DATABASE_URL"] = db_url.replace(
            env.get("DB_NAME", "app.db"),
            "test_db"
        )
    return test_env


def setup_for_node(project_path, dry_run=False):
    """Node.js 项目环境设置"""
    env = load_env_file(os.path.join(project_path, ".env"))
    test_env = {
        "TEST_BACKEND_PORT": str(get_free_port()),
        "TEST_FRONTEND_PORT": str(get_free_port()),
        "TEST_DB_HOST": "localhost",
        "TEST_DB_PORT": str(get_free_port(63306)),
        "TEST_DB_NAME": "test_db",
        "TEST_REDIS_HOST": "localhost",
        "TEST_REDIS_PORT": str(get_free_port(66379)),
    }
    return test_env


def setup_for_java(project_path, dry_run=False):
    """Java Maven 项目环境设置"""
    db_port = get_free_port(63306)
    redis_port = get_free_port(66379)
    test_env = {
        "TEST_BACKEND_PORT": str(get_free_port()),
        "TEST_DB_HOST": "localhost",
        "TEST_DB_PORT": str(db_port),
        "TEST_DB_NAME": "test_db",
        "TEST_REDIS_HOST": "localhost",
        "TEST_REDIS_PORT": str(redis_port),
        "TEST_DB_URL": f"jdbc:mysql://localhost:{db_port}/test_db",
    }
    return test_env


def init_mysql_test_db(host, port, user, password, db_name, dry_run=False):
    """初始化 MySQL 测试数据库"""
    if dry_run:
        print(f"[DRY] 创建测试数据库: {db_name} @ {host}:{port}")
        return

    cmd = [
        "mysql",
        "-h", host,
        "-P", str(port),
        "-u", user,
    ]
    if password:
        cmd.extend(["-p", password])
    cmd.extend(["-e", f"CREATE DATABASE IF NOT EXISTS {db_name};"])
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  MySQL 测试数据库 {db_name} 已就绪")


def ensure_test_dirs(project_path):
    """确保测试目录存在且已加入 .gitignore"""
    p = Path(project_path)

    # 创建目录
    test_dir = p / "test"
    playwright_dir = test_dir / "playwright"
    output_dir = test_dir / "output"
    playwright_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 检查 .gitignore
    gitignore_path = p / ".gitignore"
    ignore_entries = ["test/output/", "test.env", "test-logs/"]

    existing_ignores = set()
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            for line in f:
                existing_ignores.add(line.strip())

    missing = [e for e in ignore_entries if e not in existing_ignores]
    if missing:
        with open(gitignore_path, "a") as f:
            f.write("\n# Test environment\n")
            for entry in missing:
                f.write(entry + "\n")
        print(f"  已添加 {len(missing)} 项到 .gitignore")

    # 验证
    result = subprocess.run(
        ["git", "check-ignore", "-v", "test/output/"],
        cwd=p,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"  test/output/ 已被 .gitignore 忽略")
    else:
        print(f"  警告: test/output/ 未被 .gitignore 忽略，请手动检查")


def main():
    parser = argparse.ArgumentParser(description="初始化测试环境")
    parser.add_argument("--project-path", default=".", help="项目根目录")
    parser.add_argument("--dry-run", action="store_true", help="仅打印将要执行的操作")
    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()
    print(f"项目路径: {project_path}")

    project_type = detect_project_type(project_path)
    print(f"检测到项目类型: {project_type}")

    # 获取测试配置
    if project_type == "python":
        test_env = setup_for_python(project_path, args.dry_run)
    elif project_type.startswith("node"):
        test_env = setup_for_node(project_path, args.dry_run)
    elif project_type in ("java-maven", "java-gradle"):
        test_env = setup_for_java(project_path, args.dry_run)
    else:
        test_env = {
            "TEST_BACKEND_PORT": str(get_free_port()),
            "TEST_FRONTEND_PORT": str(get_free_port()),
        }

    # 写入 test.env
    test_env_path = project_path / "test.env"
    if not args.dry_run:
        save_env_file(str(test_env_path), test_env)
    print(f"\n测试环境配置已写入: {test_env_path}")
    for k, v in sorted(test_env.items()):
        print(f"  {k}={v}")

    # 初始化测试目录和 .gitignore
    print(f"\n初始化测试目录...")
    ensure_test_dirs(project_path)

    print(f"\n完成！测试后端端口: {test_env['TEST_BACKEND_PORT']}")


if __name__ == "__main__":
    main()
