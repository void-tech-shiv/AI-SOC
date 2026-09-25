import json
import ast

def normalize_raw_event(raw_event):
    if isinstance(raw_event, dict):
        return raw_event
        
    if not isinstance(raw_event, str):
        return {}
        
    # Try json
    try:
        return json.loads(raw_event)
    except Exception:
        pass
        
    # Try ast.literal_eval for old Python-dict-like strings
    try:
        parsed = ast.literal_eval(raw_event)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass
        
    return {}
