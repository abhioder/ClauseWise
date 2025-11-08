"""
JSON Validator and Fixer
Attempts to repair malformed JSON from AI model output
"""

import json
import re

def fix_json_string(text: str) -> str:
    """
    Attempt to fix common JSON issues in AI-generated text
    """
    # Remove common prefixes
    prefixes = ["Here is the JSON:", "JSON:", "Output:", "Result:", "```json", "```"]
    for prefix in prefixes:
        if prefix in text:
            text = text.split(prefix)[-1]
    
    # Remove trailing text after JSON
    text = text.strip().strip('`').strip()
    
    # Find JSON object
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, flags=re.DOTALL)
    if not match:
        return None
    
    json_str = match.group()
    
    # Fix common issues
    # 1. Unescaped quotes in values
    json_str = re.sub(r'(?<!\\)"(?=\w)', r'\"', json_str)
    
    # 2. Single quotes instead of double quotes
    json_str = json_str.replace("'", '"')
    
    # 3. Trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # 4. Missing commas between fields
    json_str = re.sub(r'"\s*\n\s*"', '",\n"', json_str)
    
    return json_str

def extract_and_validate_json(text: str, required_fields: list) -> dict:
    """
    Extract JSON from text and validate required fields
    
    Args:
        text: Raw text from AI model
        required_fields: List of required field names
    
    Returns:
        dict: Parsed JSON or None if invalid
    """
    # Try to fix and parse JSON
    fixed_json = fix_json_string(text)
    if not fixed_json:
        return None
    
    try:
        data = json.loads(fixed_json)
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return None
            if not data[field] or str(data[field]).strip() == "":
                return None
        
        return data
    
    except json.JSONDecodeError:
        return None

def create_fallback_json(clause: str, risk: str = "MEDIUM") -> dict:
    """
    Create a fallback JSON response when parsing fails
    """
    return {
        "original": clause,
        "simplified": f"This clause discusses: {clause[:150]}..." if len(clause) > 150 else clause,
        "risk": risk,
        "reason": f"Automated {risk} risk assessment based on clause content"
    }
