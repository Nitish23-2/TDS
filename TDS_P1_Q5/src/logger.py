import os
import json
import time

LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "run.jsonl")

def log_agent_run(chat_id: int, question: str, thoughts: list, tool_calls: list, answer: dict, log_url: str):
    """
    Appends a single JSON log object per run line to run.jsonl as required by the autograder.
    """
    entry = {
        "timestamp": time.time(),
        "chat_id": chat_id,
        "question": question,
        "thoughts": thoughts,
        "tool_calls": tool_calls,
        "answer": answer,
        "log_url": log_url
    }
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
