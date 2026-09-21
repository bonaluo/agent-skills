#!/usr/bin/env python3
"""git-worktree 配置管理脚本。"""

import json
import os
import sys
import argparse
from pathlib import Path

def get_config_paths(agent_dir=None):
    """
    返回按优先级排序的配置路径列表（高优先级在前）。
    优先级：当前Agent目录 > 通用 .agents 目录
    """
    cwd = Path.cwd()
    home = Path.home()
    skill_rel_path = Path("skills/git-worktree/git-worktree.config")
    
    paths = []
    
    # 1. 当前工作目录
    if agent_dir:
        paths.append(cwd / f".{agent_dir}" / skill_rel_path)
    paths.append(cwd / ".agents" / skill_rel_path)
    
    # 2. 用户主目录
    if agent_dir:
        paths.append(home / f".{agent_dir}" / skill_rel_path)
    paths.append(home / ".agents" / skill_rel_path)
    
    return paths

def load_config(agent_dir=None):
    """从高优先级到低优先级加载配置，返回合并后的配置 dict。"""
    defaults = {"path": ".agents/worktree", "lan": "zh"}
    for path in get_config_paths(agent_dir):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # 我们采用第一个找到的文件作为最终配置（因为优先级已排序），
                # 或者根据需求决定是否 merge。这里采用第一个匹配的文件优先级最高。
                return {**defaults, **data}
            except (json.JSONDecodeError, OSError) as e:
                print(f"警告: 无法读取 {path}: {e}", file=sys.stderr)
    return defaults

def save_config(config, path):
    """保存配置到指定路径。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", help="当前运行的 Agent 目录名 (如 claude, pi)", default=None)
    args = parser.parse_args()
    
    config = load_config(args.agent)
    print(json.dumps(config, ensure_ascii=False, indent=4))
