"""
ADVANCED TWO-PASS ANALYSIS SYSTEM
This is an alternative implementation that uses a two-stage approach:
1. First pass: Extract key information and risk signals
2. Second pass: Generate final analysis based on extracted data

To use this instead of the single-pass system:
1. Rename current granite_api.py to granite_api_single.py
2. Rename this file to granite_api.py
3. Restart the backend
"""

import torch
import json
import re
from transformers import AutoTokenizer, AutoModelForCausalLM

# Import for fallback risk assessment
try:
    from risk import assess_risk_by_keywords
except ImportError:
    def assess_risk_by_keywords(text):
        return "MEDIUM"

MODEL_NAME = "ibm-granite/granite-3.1-1b-a400m-instruct"
FORCE_CPU = True

# Load model and tokenizer once at startup
print("🔄 Loading Granite model...")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available() and not FORCE_CPU:
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

try:
    if torch.cuda.is_available() and not FORCE_CPU:
        print("   Attempting to load on GPU...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            dtype=torch.float16,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        print(f"✅ Model loaded on GPU in float16")
    else:
        print("   Loading on CPU (FORCE_CPU=True or no GPU)...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        print(f"✅ Model loaded on CPU in float32")
except Exception as e:
    print(f"⚠️  Error loading model: {str(e)[:200]}")
    print(f"   Trying CPU fallback...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float32,
        device_map="cpu",
        low_cpu_mem_usage=True
    )
    print(f"✅ Model loaded on CPU (fallback)")

def strip_html_tags(text: str) -> str:
    """Aggressively remove HTML tags and entities from text"""
    if not isinstance(text, str):
        return str(text)
    
    clean = re.sub(r'<[^>]+>', '', text)
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
        '&#39;': "'", '&nbsp;': ' ', '&apos;': "'", '&mdash;': '—',
        '&ndash;': '–', '&hellip;': '...', '&bull;': '•'
    }
    for entity, char in html_entities.items():
        clean = clean.replace(entity, char)
    clean = re.sub(r'&#?\w+;', '', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def extract_key_info(clause: str) -> dict:
    """
    PASS 1: Extract key information from the clause
    Forces the model to read every word by asking specific questions
    """
    clause_escaped = clause.replace('"', '\\"').replace('\n', ' ')
    
    prompt = f"""Read this legal clause carefully and answer these questions:

CLAUSE: "{clause_escaped}"

QUESTIONS (answer each one):
1. What are the main parties mentioned? (e.g., Company, Employee, User)
2. What specific action is required, prohibited, or permitted?
3. List any concerning keywords present: unlimited, indemnify, waive, irrevocable, perpetual, sole discretion, without notice, non-compete, hold harmless
4. Are there financial obligations or liability mentioned?
5. Are there time limits or conditions?
6. What happens if someone violates this clause?

Answer in this format:
Parties: [answer]
Action: [answer]
Keywords: [list any found or "none"]
Financial: [yes/no and details]
Conditions: [answer]
Violations: [answer]

Your analysis:"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=250,
        do_sample=False,
        temperature=0.1,
        pad_token_id=tokenizer.eos_token_id
    )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract the analysis part
    if "Your analysis:" in response:
        analysis = response.split("Your analysis:")[-1].strip()
    else:
        analysis = response
    
    return {
        "raw_analysis": analysis,
        "clause": clause
    }

def generate_final_analysis(key_info: dict) -> tuple:
    """
    PASS 2: Generate final JSON output based on extracted information
    """
    clause = key_info["clause"]
    analysis = key_info["raw_analysis"]
    clause_escaped = clause.replace('"', '\\"').replace('\n', ' ')
    
    # Detect risk level from keywords in the analysis
    analysis_lower = analysis.lower()
    high_risk_terms = ["unlimited", "indemnify", "waive", "irrevocable", "perpetual", 
                       "sole discretion", "without notice", "non-compete", "hold harmless"]
    medium_risk_terms = ["breach", "confidential", "arbitration", "termination", 
                         "intellectual property", "default"]
    
    detected_high = [term for term in high_risk_terms if term in analysis_lower]
    detected_medium = [term for term in medium_risk_terms if term in analysis_lower]
    
    if detected_high:
        risk_hint = f"HIGH (detected: {', '.join(detected_high)})"
    elif detected_medium:
        risk_hint = f"MEDIUM (detected: {', '.join(detected_medium)})"
    else:
        risk_hint = "LOW (no major risk indicators)"
    
    prompt = f"""Based on this analysis, create a JSON response:

CLAUSE: "{clause_escaped}"

ANALYSIS:
{analysis}

DETECTED RISK LEVEL: {risk_hint}

Create JSON output:
1. Simplified: Explain what this clause means in plain English (no legal jargon, no HTML)
2. Risk: Use the detected risk level above (HIGH, MEDIUM, or LOW)
3. Reason: Explain why this risk level, citing specific terms

Output ONLY valid JSON (no markdown, no HTML, no extra text):
{{
  "simplified": "plain English explanation",
  "risk": "HIGH or MEDIUM or LOW",
  "reason": "justification with specific terms cited"
}}

JSON:"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=True,
        temperature=0.2,
        top_p=0.9,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id
    )
    
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract JSON
    for marker in ["JSON:", "JSON output:", "```json", "```"]:
        if marker in text:
            text = text.split(marker)[-1]
    
    text = text.strip().strip('`').strip()
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, flags=re.DOTALL)
    
    if match:
        json_text = strip_html_tags(match.group())
        try:
            parsed = json.loads(json_text)
            parsed["original"] = clause
            
            if "simplified" in parsed and "risk" in parsed and "reason" in parsed:
                parsed["simplified"] = strip_html_tags(str(parsed["simplified"]))
                parsed["reason"] = strip_html_tags(str(parsed["reason"]))
                parsed["simplified"] = " ".join(parsed["simplified"].split())
                parsed["reason"] = " ".join(parsed["reason"].split())
                
                risk = str(parsed["risk"]).upper()
                if risk in ["HIGH", "MEDIUM", "LOW"]:
                    parsed["risk"] = risk
                    return True, parsed
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse error: {e}")
    
    # Fallback
    return False, None

def call_granite(clause: str):
    """
    TWO-PASS ANALYSIS:
    Pass 1: Extract key information (forces word-by-word reading)
    Pass 2: Generate final JSON output
    """
    print(f"   📝 Analyzing clause: {clause[:50]}...")
    print(f"   🔍 PASS 1: Extracting key information...")
    
    # Pass 1: Extract information
    key_info = extract_key_info(clause)
    print(f"   ✅ Key info extracted")
    print(f"   🔍 PASS 2: Generating final analysis...")
    
    # Pass 2: Generate final output
    success, result = generate_final_analysis(key_info)
    
    if success:
        print(f"   ✅ Two-pass analysis complete")
        return True, result
    
    # Fallback
    print(f"   ⚠️  Using fallback response")
    fallback_risk = assess_risk_by_keywords(clause)
    simplified = clause[:100] + "..." if len(clause) > 100 else clause
    
    return True, {
        "original": clause,
        "simplified": f"This clause discusses: {simplified}",
        "risk": fallback_risk,
        "reason": f"Keyword-based analysis indicates {fallback_risk} risk. Two-pass analysis was inconclusive."
    }
