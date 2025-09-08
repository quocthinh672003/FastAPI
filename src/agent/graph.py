from __future__ import annotations

import asyncio
import json
import operator
import re
from dataclasses import dataclass
from typing import Any, Dict, TypedDict

import aiohttp
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


class Context(TypedDict):
    """Context parameters for the agent."""

    openai_api_key: str


@dataclass
class State:
    """State for the ReAct Agent."""

    user_input: str = ""
    thought: str = ""
    action: str = ""
    action_input: str = ""
    observation: str = ""


# Tools
async def weather_tool(location: str) -> str:
    """Get weather information for a location using Open-Meteo API."""
    try:
        async with aiohttp.ClientSession() as session:
            # Geocode location
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            }

            async with session.get(geo_url, params=geo_params, timeout=15) as resp:
                geo_data = await resp.json()

            if not geo_data.get("results"):
                return f"Location '{location}' not found. Please try a more specific location."

            place = geo_data["results"][0]
            lat, lon = place["latitude"], place["longitude"]
            name = place.get("name", location)
            admin = place.get("admin1", "")

            # Get weather
            wx_url = "https://api.open-meteo.com/v1/forecast"
            wx_params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "timezone": "auto",
            }

            async with session.get(wx_url, params=wx_params, timeout=15) as resp:
                wx_data = await resp.json()

            current = wx_data.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")

            location_str = f"{name}, {admin}" if admin else name
            return f"Current weather in {location_str}: {temp}°C, wind {wind} km/h"

    except Exception as e:
        return f"Failed to get weather for '{location}': {str(e)}"


def calculator_tool(expression: str) -> str:
    """Safely evaluate mathematical expressions."""
    try:
        # Remove dangerous characters and validate
        safe_expr = re.sub(r"[^0-9+\-*/().\s]", "", expression)
        if not safe_expr.strip():
            return "Invalid expression"

        # Use operator module for safe evaluation
        allowed_ops = {
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.truediv,
            "**": operator.pow,
        }

        # Simple evaluation for basic math
        result = eval(safe_expr, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"

    except Exception as e:
        return f"Calculation error: {str(e)}"


def search_tool(query: str) -> str:
    """Simple knowledge search tool."""
    knowledge_base = {
        "python": "Python is a popular, easy-to-learn programming language.",
        "ai": "AI (Artificial Intelligence) simulates human intelligence in machines.",
        "langgraph": "LangGraph is a framework for building AI agents with graph-based architecture.",
        "react": "ReAct (Reasoning + Acting) is an AI agent pattern that combines reasoning and action.",
    }

    query_lower = query.lower()
    for keyword, result in knowledge_base.items():
        if keyword in query_lower:
            return result

    return f"Search for '{query}': No specific results found. Try different keywords."


# Helper function to create LLM instance
def _get_llm(runtime: Runtime[Context]) -> ChatOpenAI:
    """Get configured LLM instance."""
    api_key = runtime.context.get("openai_api_key") if runtime.context else None
    return ChatOpenAI(model="gpt-4o-mini", api_key=api_key)


# ReAct Agent Nodes
async def think_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Analyze user input and decide on action."""
    prompt = f"""You are a ReAct Agent. Analyze the user input and decide on the best action.

Available actions:
- weather: get weather information (action_input = location name)
- calculator: evaluate math expression (action_input = expression)
- search: search knowledge base (action_input = query)
- answer: answer directly (action_input = user question)

Return JSON with keys: thought, action, action_input
User Input: "{state.user_input}"
Output:"""

    try:
        llm = _get_llm(runtime)
        response = await llm.ainvoke([{"role": "system", "content": prompt}])
        data = json.loads(response.content)
    except (json.JSONDecodeError, Exception):
        data = {
            "thought": "Failed to parse JSON response",
            "action": "answer",
            "action_input": state.user_input,
        }

    return {
        "thought": str(data.get("thought", "")),
        "action": str(data.get("action", "answer")),
        "action_input": str(data.get("action_input", state.user_input)),
    }


async def act_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Execute the chosen action."""
    query = state.action_input or state.user_input
    action = (state.action or "answer").lower()

    if action == "weather":
        observation = await weather_tool(query)
    elif action == "calculator":
        observation = calculator_tool(query)
    elif action == "search":
        observation = search_tool(query)
    else:
        # Direct answer using LLM
        try:
            llm = _get_llm(runtime)
            response = await llm.ainvoke(
                [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Provide concise, accurate answers.",
                    },
                    {"role": "user", "content": query},
                ]
            )
            observation = response.content
        except Exception as e:
            observation = f"Error generating response: {str(e)}"

    return {"observation": observation}


# Define the ReAct graph
graph = (
    StateGraph(State, context_schema=Context)
    .add_node("think", think_node)
    .add_node("act", act_node)
    .add_edge("__start__", "think")
    .add_edge("think", "act")
    .add_edge("act", "__end__")
    .compile()
)
