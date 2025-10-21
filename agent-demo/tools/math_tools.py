from openai.agents import Tool
from utils.auth import check_permission

@Tool()
def add(a: int, b: int) -> int:
    check_permission("admin", "add")
    return a + b

@Tool()
def subtract(a: int, b: int) -> int:
    check_permission("admin", "subtract")
    return a - b

@Tool()
def multiply(a: int, b: int) -> int:
    check_permission("admin", "multiply")
    return a * b
