from openai.agents import Agent

chat_agent = Agent(
    name="Chat Agent",
    model="gpt-4o-mini",
    instructions="you are a chatbot general assistant. If user asks for a math, handoff to math agent handle it",
)