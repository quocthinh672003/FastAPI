from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")


async def main():
    async for chunk in client.runs.stream(
        None,  # project ID (để None nếu local)
        "agent",  # tên graph mặc định
        input={"messages": [{"role": "human", "content": "Hello, what is LangGraph?"}]},
    ):
        if hasattr(chunk.data, "delta"):
            print(chunk.data.delta, end="")


asyncio.run(main())
