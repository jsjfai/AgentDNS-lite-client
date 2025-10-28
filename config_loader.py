# config_loader.py
import json
import os

def load_config(path: str = "configure.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 环境变量优先级最高，如果有环境变量则使用环境变量
    env_lang = os.getenv("AGENTDNS_LANG")
    if env_lang:
        config["language"] = env_lang
    elif "language" not in config:
        # 如果既没有环境变量也没有配置文件设置，使用默认值
        config["language"] = "zh-CN"

    return config
