def chat(model, messages, stream=False, options=None):
    """Return a mock response mimicking `ollama.chat`."""
    last_user = next((m['content'] for m in reversed(messages) if m.get('role') == 'user'), '')
    content = f"MOCK RESPONSE: {last_user}"
    return {"message": {"content": content}}
