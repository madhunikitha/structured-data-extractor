import json
import datetime
import os

AUDIT_LOG_JSON = "audit_log.json"

def log_to_json(query, field_instruction, prompt, llm_output):
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user_query": query,
        "field_instruction": field_instruction,
        "prompt": prompt,
        "llm_output": llm_output
    }

    # Load existing logs if file exists
    if os.path.exists(AUDIT_LOG_JSON):
        with open(AUDIT_LOG_JSON, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new log
    data.append(log_entry)

    # Save updated logs
    with open(AUDIT_LOG_JSON, "w") as f:
        json.dump(data, f, indent=2)
