"""ReAct Agent - Reasoning + Acting Agent using LangGraph.

This agent follows the ReAct pattern:
1. Observation → 2. Thought → 3. Action → 4. Observation → 5. Answer
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
import requests

class Context(TypedDict):
    """Context parameters for the agent."""
    openai_api_key: str


@dataclass
class State:
    """State for the ReAct Agent."""
    # Input
    user_input: str = ""
    
    # ReAct loop state
    thought: str = ""
    action: str = ""
    observation: str = ""
    answer: str = ""


# Tools
def weather_tool(location: str) -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 21.0285,
        "longitude": 105.8542,
        "current_weather": "true",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
        "timezone": "Asia/Ho_Chi_Minh"
    }
    response = requests.get(url, params = params)
    return response.json()

def calculator_tool(expression: str) -> str:
    try:
        safe_expr = re.sub(r'[^0-9+\-*/().\s]', '', expression)
        result = eval(safe_expr)
        return f"Kết quả: {expression} = {result}"
    except Exception as e:
        return f"Lỗi tính toán: {str(e)}"


def search_tool(query: str) -> str:
    search_results = {
        "python": "Python là ngôn ngữ lập trình phổ biến, dễ học và mạnh mẽ.",
        "ai": "AI (Trí tuệ nhân tạo) là công nghệ mô phỏng trí thông minh con người.",
        "langgraph": "LangGraph là framework xây dựng AI Agent với graph-based architecture."
    }
    
    query_lower = query.lower()
    for keyword, result in search_results.items():
        if keyword in query_lower:
            return result
    
    return f"Tìm kiếm '{query}': Không tìm thấy kết quả cụ thể. Hãy thử từ khóa khác."


# ReAct Agent Nodes
async def think_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    prompt = """
    You are a ReAct Agent.
    Your task is get input from user and think(thought) and act(action) based on the input.
    
    """

async def act_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    user_input = state.user_input
    if state.action == "weather":
        observation = weather_tool(user_input)
    elif state.action == "calculator":
        observation = calculator_tool(user_input)
    elif state.action == "search":
        observation = search_tool(user_input)
    else:
        observation = f"trả lời trực tiếp: {user_input}"
    return { "observation": observation }


async def answer_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    thought = state.thought
    action = state.action
    observation = state.observation
    
    answer = f"""
🤔 Suy nghĩ: {thought}
⚡ Hành động: {action}
👀 Quan sát: {observation}
✅ Trả lời: {observation}
"""
    
    return {
        "answer": answer
    }


def should_continue(state: State) -> str:
    """Determine if we should continue or finish."""
    # If we have an answer, go to answer node
    if state.answer:
        return "answer"
    # Otherwise, continue with action
    return "act"


# Define the ReAct graph
graph = (
    StateGraph(State, context_schema=Context)
    .add_node("think", think_node)
    .add_node("act", act_node)
    .add_edge("__start__", "think")
    .add_edge("think", "act")
    .add_edge("act", "answer")
    .add_edge("answer", "__end__")
    .compile()
)
