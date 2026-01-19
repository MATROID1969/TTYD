import json
import os
from datetime import datetime


LOG_PATH = "conversation_logs.jsonl"


def log_event(data: dict):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
