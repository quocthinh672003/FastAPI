

def check_permission(role: str, tool_name: str):
    roles = {
        "admin": ["math", "weather", "handoff"],
        "user": ["weather"]
    }

    if tool_name not in roles.get(role, []):
        raise PermissionError(f"User {role} does not have permission to perform {action}")
