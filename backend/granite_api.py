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

# Force CPU mode due to RTX 5050 sm_120 incompatibility with current PyTorch
# TODO: Switch to GPU when PyTorch adds sm_120 support
FORCE_CPU = True

# Load model and tokenizer once at startup
print("🔄 Loading Granite model...")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available() and not FORCE_CPU:
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Simple approach: Load in float16 on GPU if available, else CPU
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
    
    # Remove HTML tags (including self-closing and with attributes)
    clean = re.sub(r'<[^>]+>', '', text)
    
    # Remove common HTML entities
    html_entities = {
        '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
        '&#39;': "'", '&nbsp;': ' ', '&apos;': "'", '&cent;': '¢',
        '&pound;': '£', '&yen;': '¥', '&euro;': '€', '&copy;': '©',
        '&reg;': '®', '&trade;': '™', '&times;': '×', '&divide;': '÷',
        '&mdash;': '—', '&ndash;': '–', '&hellip;': '...',
        '&laquo;': '«', '&raquo;': '»', '&bull;': '•'
    }
    for entity, char in html_entities.items():
        clean = clean.replace(entity, char)
    
    # Remove any remaining HTML entities (numeric)
    clean = re.sub(r'&#?\w+;', '', clean)
    
    # Remove excessive whitespace
    clean = re.sub(r'\s+', ' ', clean)
    
    return clean.strip()

def call_granite(clause: str):
    print(f"   📝 Analyzing clause: {clause[:50]}...")
    
    # Escape quotes in clause to prevent JSON issues
    clause_escaped = clause.replace('"', '\\"').replace('\n', ' ')
    
    # Count words to emphasize thoroughness
    word_count = len(clause.split())
    
    prompt = f"""TASK: Analyze legal clause and output JSON only.

CLAUSE ({word_count} words):
{clause_escaped}

ANALYSIS RULES:
1. Read the clause completely
2. Identify: parties, obligations, penalties, restrictions, liability
3. Classify risk using these criteria:
   HIGH = Contains ANY of: unlimited liability, indemnification, non-compete, unilateral termination, waiver of rights, irrevocable terms, sole discretion, financial penalties without cap, hold harmless, perpetual obligations, at will termination, forfeit rights
   MEDIUM = Contains ANY of: confidentiality requirements, breach definitions, termination conditions, IP assignment, arbitration clauses, specific obligations with defined limits, proprietary information, trade secrets, dispute resolution
   LOW = Contains ONLY: definitions, notices, effective dates, mutual standard terms, administrative procedures, routine notifications, commencement dates
4. Simplify to plain English (no legal jargon, no HTML)
5. Justify risk with specific terms from clause

OUTPUT FORMAT (strict JSON, no other text):
{{
"original": "{clause_escaped}",
"simplified": "plain English explanation",
"risk": "HIGH or MEDIUM or LOW",
"reason": "specific term or phrase that triggered this classification"
}}

Rules:
- Output ONLY the JSON object above
- Do not write "Here is", "I analyzed", or any preamble
- Do not use markdown, code blocks, or formatting
- If uncertain, default to MEDIUM
- Never leave "simplified" empty - always provide explanation
- "reason" must cite specific words from the clause

JSON output:"""

    # Tokenize input
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    print(f"   ⚙️  Analyzing {word_count} words with optimized deterministic prompt...")

    # Generate response with optimized parameters for thorough analysis
    outputs = model.generate(
        **inputs,
        max_new_tokens=400,  # Increased for detailed step-by-step analysis
        do_sample=True,      # Enable sampling for natural language
        temperature=0.2,     # Lower temperature for more focused analysis
        top_p=0.85,          # Slightly lower for more deterministic output
        top_k=50,            # Add top-k sampling for quality
        repetition_penalty=1.15,  # Higher penalty to prevent repetition
        no_repeat_ngram_size=3,   # Prevent 3-gram repetition
        pad_token_id=tokenizer.eos_token_id
    )
    print(f"   ✅ Analysis complete")

    # Decode model output
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"   🔍 Raw output: {text[:200]}...")

    # Try to extract JSON - look for the response after the prompt
    # First try to find JSON after common markers
    for marker in ["JSON output:", "JSON response:", "Output:", "```json", "```"]:
        if marker in text:
            text = text.split(marker)[-1]
    
    # Remove markdown code blocks if present
    text = text.strip().strip('`').strip()
    
    # Extract JSON block
    match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, flags=re.DOTALL)
    if match:
        json_text = match.group()
        
        # Aggressively strip HTML from the JSON string itself before parsing
        json_text = strip_html_tags(json_text)
        
        try:
            parsed = json.loads(json_text)
            # Add original clause
            parsed["original"] = clause
            # Validate required fields
            if "simplified" in parsed and "risk" in parsed and "reason" in parsed:
                # AGGRESSIVE CLEANUP PIPELINE
                # Step 1: Strip HTML tags
                parsed["simplified"] = strip_html_tags(str(parsed["simplified"]))
                parsed["reason"] = strip_html_tags(str(parsed["reason"]))
                
                # Step 2: Remove markdown formatting
                parsed["simplified"] = re.sub(r'\*\*(.+?)\*\*', r'\1', parsed["simplified"])  # **bold**
                parsed["simplified"] = re.sub(r'\*(.+?)\*', r'\1', parsed["simplified"])      # *italic*
                parsed["simplified"] = re.sub(r'`(.+?)`', r'\1', parsed["simplified"])        # `code`
                parsed["reason"] = re.sub(r'\*\*(.+?)\*\*', r'\1', parsed["reason"])
                parsed["reason"] = re.sub(r'\*(.+?)\*', r'\1', parsed["reason"])
                parsed["reason"] = re.sub(r'`(.+?)`', r'\1', parsed["reason"])
                
                # Step 3: Remove extra whitespace and newlines
                parsed["simplified"] = " ".join(parsed["simplified"].split())
                parsed["reason"] = " ".join(parsed["reason"].split())
                
                # Step 4: Ensure non-empty
                if not parsed["simplified"].strip():
                    parsed["simplified"] = f"This clause addresses: {clause[:100]}..."
                if not parsed["reason"].strip():
                    parsed["reason"] = "Analysis based on clause content"
                
                # Step 5: Normalize risk value
                risk = str(parsed["risk"]).upper().strip()
                if risk not in ["HIGH", "MEDIUM", "LOW"]:
                    # Try to extract from text
                    if "HIGH" in risk:
                        risk = "HIGH"
                    elif "MEDIUM" in risk:
                        risk = "MEDIUM"
                    elif "LOW" in risk:
                        risk = "LOW"
                    else:
                        risk = assess_risk_by_keywords(clause)
                
                parsed["risk"] = risk
                print(f"   ✅ Parsed successfully: {risk} risk")
                return True, parsed
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse error: {e}")
            print(f"   🔍 Attempted to parse: {json_text[:200]}...")

    # Fallback - create a basic response with keyword-based risk
    print(f"   ⚠️  Using fallback response with keyword analysis")
    fallback_risk = assess_risk_by_keywords(clause)
    
    # Create a simple simplified version (first 100 chars or first sentence)
    simplified = clause[:100] + "..." if len(clause) > 100 else clause
    
    return True, {
        "original": clause,
        "simplified": f"This clause discusses: {simplified}",
        "risk": fallback_risk,
        "reason": f"Keyword-based analysis indicates {fallback_risk} risk. AI model response was unclear."
    }
