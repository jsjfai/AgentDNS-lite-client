# task_decompose.py (改进后的 smart_query)
import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from config_loader import load_config
from openai import OpenAI

config = load_config()

# === 构建 DeepSeek 客户端 ===
def build_deepseek_client():
    return OpenAI(
        api_key=config["deepseek"]["api_key"],
        base_url=config["deepseek"]["base_url"],
    )

# === 使用 DeepSeek 生成 arguments ===
def generate_args_by_deepseek(tool_schema, user_query: str) -> dict:
    client = build_deepseek_client()
    system_prompt = (
        "You are a JSON argument generator. "
        "Given a tool inputSchema (JSON Schema) and a user's natural-language query, "
        "produce a minimal valid JSON object that satisfies the schema. "
        "⚠️ Important rules:\n"
        "1. ONLY output the JSON object, nothing else.\n"
        "2. If the schema includes 'district_id', return the correct 6-digit adcode "
        "for the mentioned city at the CITY level (not province). Example: "
        "'北京' → '110100', '上海' → '310100'.\n"
        "3. Ensure the result is valid JSON, no extra commentary."
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Schema: {tool_schema}\nQuery: {user_query}"},
        ],
        temperature=0,
    )

    raw = resp.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"error": f"Invalid JSON from model: {raw}"}


# === 用 DeepSeek 选择最合适的工具 ===
def choose_tool_by_deepseek(user_query: str, tools: list) -> dict:
    """
    传入 user_query 和 get_available_tools 返回的工具列表，
    让 DeepSeek 选择最合适的 tool。
    返回选中的 tool dict。
    """
    client = build_deepseek_client()
    tool_names = [t.get("name") for t in tools]

    system_prompt = (
        "You are a tool selector. "
        "I will give you a user query and a list of available tools. "
        "Your job is to pick the BEST matching tool name. "
        "Rules:\n"
        "1. ONLY output the tool name string, nothing else.\n"
        "2. If multiple tools could work, pick the most specific one.\n"
        "3. If none match well, pick the closest.\n"
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Query: {user_query}\nAvailable Tools: {tool_names}"},
        ],
        temperature=0,
    )

    tool_name = resp.choices[0].message.content.strip()
    for t in tools:
        if t.get("name") == tool_name:
            return t
    return tools[0]  # fallback：如果大模型返回的名字不在列表里，就用第一个


# === 使用 DeepSeek 流式解释结果 ===
async def explain_result_stream(smart_result: dict):
    client = build_deepseek_client()
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个结果解释助手。请将提供的 JSON 查询结果转换为简明扼要的中文说明，便于普通用户理解。"},
            {"role": "user", "content": json.dumps(smart_result, ensure_ascii=False)},
        ],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print("\n")


# === 核心逻辑 ===
async def smart_query(baseurl: str, user_query: str, debug: bool = False):
    async with streamablehttp_client(baseurl) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Step 1: get_available_tools
            # print("请求 get_available_tools ...")
            tools_result = await session.call_tool("get_available_tools", {"query": user_query})
            if tools_result.content and hasattr(tools_result.content[0], "text"):
                try:
                    tools_data = json.loads(tools_result.content[0].text)
                except Exception as e:
                    print("解析工具列表失败:", e)
                    return None
            else:
                print("未返回工具列表")
                return None

            tools = tools_data.get("tools", [])
            # print(f"get_available_tools -> {len(tools)} candidate tools")

            if not tools:
                return None

            # Step 2: 用 DeepSeek 挑选最合适的工具
            chosen_tool = choose_tool_by_deepseek(user_query, tools)
            tool_name = chosen_tool.get("name")
            schema = chosen_tool.get("inputSchema", {})

            # print(f"\n选择的工具: {tool_name}")
            args = generate_args_by_deepseek(schema, user_query)
            # print("  生成的 arguments:", args)

            # Step 3: 执行选中的工具
            try:
                exec_result = await session.call_tool("execute_tool", {
                    "toolName": tool_name,
                    "arguments": args
                })

                if exec_result.content and hasattr(exec_result.content[0], "text"):
                    text_result = exec_result.content[0].text
                    try:
                        parsed_result = json.loads(text_result)
                    except Exception:
                        parsed_result = text_result
                else:
                    parsed_result = exec_result.structuredContent or None

                smart_result = {
                    "found": parsed_result is not None,
                    "tool": tool_name,
                    "arguments": args,
                    "result": parsed_result,
                }

                # 输出中文解释
                await explain_result_stream(smart_result)

                # if debug:
                #     print("\n=== Smart 服务执行结果（JSON 调试信息） ===")
                #     print(json.dumps(smart_result, ensure_ascii=False, indent=2))

                return smart_result

            except Exception as e:
                print(f"  执行工具 {tool_name} 出错:", e)
                return None


# === 测试入口 ===
if __name__ == "__main__":
    baseurl = "http://192.168.201.180:30013/mcp/$smart"
    query = "查询北京的天气信息"

    result = asyncio.run(smart_query(baseurl, query, debug=True))
