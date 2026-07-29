"""
chatbot.py – OpenAI-powered weather assistant.

Takes a live weather summary (from weather.py) and a user message,
then streams a helpful explanation and prediction back.
"""

import os
from openai import OpenAI

SYSTEM_PROMPT = """You are a friendly and knowledgeable weather assistant.

You are given real-time weather data and a short-range forecast at the start of
every conversation. Your job is to:
1. Explain what the current conditions mean in plain, accessible language.
2. Give simple, practical predictions based on the forecast data provided.
3. Answer any follow-up questions the user has about the weather.
4. Suggest appropriate clothing, activities, or precautions when relevant.

Always base your answers on the weather data you have been given. If you are
unsure about something that goes beyond the data, say so clearly. Keep answers
concise and helpful."""


def _client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. "
            "Add it to your .env file (see .env.example)."
        )
    return OpenAI(api_key=key)


def build_messages(weather_summary: str, history: list[dict]) -> list[dict]:
    """Assemble the full message list to send to the Chat Completions API.

    history is a list of {"role": "user"|"assistant", "content": "..."} dicts
    representing the conversation so far (excluding the weather context message).
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "Here is the latest weather data you must use:\n\n"
                + weather_summary
            ),
        },
    ]
    messages.extend(history)
    return messages


def chat(weather_summary: str, history: list[dict], model: str = "gpt-4o-mini") -> str:
    """Send the conversation to OpenAI and return the assistant reply.

    Args:
        weather_summary: Plain-text weather block from weather.summarise_for_chatbot().
        history: List of prior {role, content} turns in this session.
        model: OpenAI model name to use.

    Returns:
        The assistant's reply as a string.
    """
    client = _client()
    messages = build_messages(weather_summary, history)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()
