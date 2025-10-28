# main.py
import asyncio
import json
import os
from question_classify import classify_and_decompose
from ai_agent_dns import get_categories, query_category
from match import match_tasks_with_categories
from task_decompose import smart_query
from config_loader import load_config
from openai import OpenAI
from i18n import init_i18n, t, get_banner_file

config = load_config()

# 初始化国际化
init_i18n(config.get("language", "zh-CN"))

# DeepSeek 客户端（兜底用）
client = OpenAI(
    api_key=config["deepseek"]["api_key"],
    base_url=config["deepseek"]["base_url"]
)

def display_banner():
    """显示启动banner和系统信息"""
    # 清屏
    os.system('clear' if os.name == 'posix' else 'cls')

    # 添加一些科技感的装饰
    # print("=" * 88)
    # print(t("banner.initializing"))
    # print("=" * 88)

    # 读取并显示banner
    banner_path = get_banner_file()
    try:
        with open(banner_path, 'r', encoding='utf-8') as f:
            banner_content = f.read()

            # 为banner添加颜色（使用ANSI颜色代码）
            print("\033[96m")  # 青色
            print(banner_content)
            print("\033[0m")   # 重置颜色
    except FileNotFoundError:
        print(t("error.banner_not_found"))

    print()

async def handle_query(user_input: str):
    tasks = classify_and_decompose(user_input)
    print(t("main.classification_result"), tasks)

    print(t("main.response_header"))
    categories = await get_categories()

    mapping = match_tasks_with_categories(tasks, categories)

    # === 兜底逻辑 ===
    all_unknown = all(cat == "unknown" for cat in mapping.values())
    if all_unknown:
        print(t("main.no_match_warning"))
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个智能助手，直接回答用户的问题"},
                {"role": "user", "content": user_input}
            ],
            stream=True  # ✅ 开启流式输出
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")
        return

    # === 正常走 AgentDNS + Smart 服务 ===
    for task, category in mapping.items():
        if category != "unknown":
            result = await query_category(category)
            baseurl = result.get("baseurl")
            if baseurl:
                await smart_query(baseurl, task, debug=True)


async def main():
    # 显示启动banner
    display_banner()

    while True:
        try:
            user_input = input(t("main.input_prompt"))
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Bye 👋")
                break
            await handle_query(user_input)
        except KeyboardInterrupt:
            print("\nBye 👋")
            break


if __name__ == "__main__":
    asyncio.run(main())
