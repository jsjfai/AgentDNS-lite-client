# match.py
import re
from typing import List, Dict
from config_loader import load_config

config = load_config()

# 定义任务关键词映射（后面可以扩展成外部配置文件）
CATEGORY_RULES = config["category_rules"]

def normalize_text(text: str) -> str:
    """小写化并去除特殊字符"""
    return re.sub(r'[^\w\u4e00-\u9fff]+', '', text.lower())

def match_tasks_with_categories(tasks: List[str], categories: List[str]) -> Dict[str, str]:
    """基于规则表匹配任务和 category"""
    mapping = {}
    for task in tasks:
        norm_task = normalize_text(task)
        matched = "unknown"

        for category, keywords in CATEGORY_RULES.items():
            if category not in categories:
                continue  # AgentDNS 不支持的跳过
            if any(keyword in norm_task for keyword in keywords):
                matched = category
                break

        mapping[task] = matched
    return mapping
