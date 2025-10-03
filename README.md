# Python AI Development Project

A clean project to learn and experiment with Python AI SDKs (OpenAI, Anthropic).

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment:**
   ```bash
   # Copy the example environment file
   copy env.example .env
   
   # Edit .env and add your OpenAI API key
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Run the example:**
   ```bash
   python main.py
   ```

## Python AI SDK Features to Explore

- **OpenAI**: GPT-4, GPT-3.5, DALL-E, Whisper
- **Anthropic**: Claude-3 (Haiku, Sonnet, Opus)
- **Text Generation**: Chat completions
- **Structured Output**: JSON mode, function calling
- **Streaming**: Real-time responses
- **Multi-modal**: Text, images, audio

## Project Structure

```
├── main.py              # Main example file
├── requirements.txt     # Dependencies
├── env.example         # Environment template
├── .env                # Your API keys (create this)
└── README.md           # This file
```

## Next Steps

1. Start with `main.py` to understand basic AI SDK v5 usage
2. Experiment with different models and providers
3. Try structured outputs and tool calling
4. Build more complex AI applications

Happy learning! 🚀