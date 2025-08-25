"helper methods used in routes"

from src.configs.typing import InterviewerType


def get_formatted_messages(messages: list[dict]) -> str:
    """Format messages for LLM input"""
    return " ".join(
        [
            f"{m.get("type")} {m.get("content")}"
            for m in messages
            if m.get("type") != InterviewerType.COACH
        ]
    )
