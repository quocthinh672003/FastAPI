from openai.agents import Agent
from tools.math_tools import add, subtract, multiply

def guard_no_negative_numbers(input):
    if input < 0:
        raise ValueError("Input must be a positive number")
    return input



agent = Agent(
    name="Math Agent",
    model="gpt-4o-mini",
    instructions="You are a helpful assistant that can perform math operations.",
    tools=[add, subtract, multiply],
    guardrails=[guard_no_negative_numbers],
    max_turns=3
)