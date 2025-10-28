# question_classify.py
from openai import OpenAI
import re
from config_loader import load_config

config = load_config()

client = OpenAI(
    api_key=config["deepseek"]["api_key"],
    base_url=config["deepseek"]["base_url"]
)

def classify_and_decompose(user_input: str):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个任务分类器，负责将用户请求拆分为简洁的编号子任务，只输出任务列表"},
            {"role": "user", "content": user_input}
        ]
    )
    raw_output = response.choices[0].message.content

    tasks = []
    for line in raw_output.splitlines():
        if re.match(r'^\d+\.', line.strip()):
            tasks.append(line.strip())
    return tasks
