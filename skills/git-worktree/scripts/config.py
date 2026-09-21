#!/usr/bin/env python3
"""git-worktree 配置管理脚本。"""

import json
import os
import sys
from pathlib import Path

def get_config_paths():
    """返回按优先级排序的配置路径列表（高优先级在前）。"""
    cwd = Path.cwd()
    return [
        cwd / ".agents" / "git" / "worktree.config",
        Path.home() / ".agents" / "git" / "worktree.config",
    ]

def load_config():
    """从高优先级到低优先级加载配置，返回合并后的配置 dict。"""
    defaults = {"path": ".agents/worktree", "lan": "zh"}
    for path in get_config_paths():
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                defaults.update(data)
            except (json.JSONDecodeError, OSError) as e:
                print(f"警告: 无法读取 {path}: {e}", file=sys.stderr)
    return defaults

def save_config(config, path):
    """保存配置到指定路径。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    config = load_config()
    print(json.dumps(config, ensure_ascii=False, indent=4))
