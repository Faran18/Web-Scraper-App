# backend/utils/json_formatter.py
import json
import re

def extract_json(text: str) -> dict:
    """
    Try to extract and validate JSON from LLM output.
    If invalid JSON is returned, attempt cleanup.
    """
    if not text:
        return {"error": "Empty response from LLM"}

    # Step 1: Try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 2: Extract JSON-like substring with regex
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Step 3: Fallback → return wrapped string
    return {"raw_output": text.strip(), "error": "Could not parse valid JSON"}

def format_to_json(data: dict, indent: int = 2) -> str:
    """
    Nicely format Python dict into a JSON string.
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to format JSON: {str(e)}"})
