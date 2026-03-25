import os
import anthropic

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def call_claude(system_prompt, user_message, model="claude-opus-4-6", max_tokens=4096, tools=None, tool_choice=None):
    client = get_client()

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }
    if tools:
        kwargs["tools"] = tools
    if tool_choice:
        kwargs["tool_choice"] = tool_choice

    try:
        message = client.messages.create(**kwargs)
    except anthropic.APIStatusError as e:
        print(f"API error {e.status_code}: {e.message}")
        raise

    if message.stop_reason == "max_tokens":
        print("Warning: response was truncated, consider increasing max_tokens")
        # TODO: throw error, agent needs to bubble error up to runner who should mark the run as FAILED_MAX_TOKENS

    print(f"Usage — input tokens: {message.usage.input_tokens}, output tokens: {message.usage.output_tokens}")

    tool_use_block = next((b for b in message.content if b.type == "tool_use"), None)
    if tool_use_block:
        return tool_use_block.input

    return message.content[0].text