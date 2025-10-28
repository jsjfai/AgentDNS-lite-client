import asyncio
import json
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from config_loader import load_config

config = load_config()

async def get_categories():
    async with sse_client(config["agentdns"]["sse_url"]) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("category_list", {})
            # print("调试输出:", result)

            # 优先解析 structuredContent
            if result.structuredContent:
                return result.structuredContent.get("result", [])

            # 兼容服务端返回在 content.text 里的情况
            if result.content and hasattr(result.content[0], "text"):
                try:
                    data = json.loads(result.content[0].text)
                    # 如果是 { "weather_forecast": "default", ... } 就取 key 列表
                    if isinstance(data, dict):
                        return list(data.keys())
                    elif isinstance(data, list):
                        return data
                except Exception as e:
                    print("解析 content.text 失败:", e)
                    return []

            return []


async def query_category(category: str):
    """
    调用 AgentDNS 的 category_query tool
    必须传参数 {"category": <string>}
    返回 JSON 结果
    """
    async with sse_client(config["agentdns"]["sse_url"]) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("category_query", {"category": category})

            # 优先解析 structuredContent
            if result.structuredContent:
                return result.structuredContent

            # 如果 structuredContent 为空，解析 content[0].text
            if result.content and hasattr(result.content[0], "text"):
                try:
                    return json.loads(result.content[0].text)
                except Exception:
                    return {"raw": result.content[0].text}

            return None
