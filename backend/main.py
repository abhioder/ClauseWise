from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import json
import re

# Fallback path adjustment to ensure local imports work when launched from different CWDs
try:
    from text_extraction import extract_text
    from clause_segmentation import segment_clauses
    from granite_api import call_granite, MODEL_NAME
    from risk import assess_risk_by_keywords, enhance_risk_assessment
except ImportError:
    import sys as _sys
    import os as _os
    _sys.path.append(_os.path.dirname(_os.path.abspath(__file__)))
    from text_extraction import extract_text
    from clause_segmentation import segment_clauses
    from granite_api import call_granite, MODEL_NAME
    from risk import assess_risk_by_keywords, enhance_risk_assessment


app = FastAPI(title="ClauseWise API")

# CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Main endpoint: accepts document, returns analyzed clauses.
    """

    # Validate file type
    if not file.filename.lower().endswith(('.pdf', '.docx', '.txt')):
        raise HTTPException(400, "Only PDF, DOCX, and TXT files are supported")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        # Save uploaded file
        print(f"\n📄 Received file: {file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Extract text
        print("📖 Step 1: Extracting text...")
        text = extract_text(file_path)
        print(f"   Extracted {len(text)} characters")

        if not text:
            raise HTTPException(400, "No text could be extracted from the document")

        # Step 2: Segment into clauses
        print("✂️  Step 2: Segmenting clauses...")
        clauses = segment_clauses(text)
        print(f"   Found {len(clauses)} clauses")

        if not clauses:
            raise HTTPException(400, "No meaningful clauses found in the document")

        # Step 3: Analyze clauses with Granite
        print(f"🤖 Step 3: Analyzing {len(clauses)} clauses with Granite AI...")
        results = []

        for idx, clause in enumerate(clauses, 1):
            print(f"\n   Clause {idx}/{len(clauses)}:")
            ok, out = call_granite(clause)

            if not ok:
                # Fallback to keyword risk scoring
                results.append({
                    "original": clause,
                    "simplified": "",
                    "risk": assess_risk_by_keywords(clause),
                    "reason": "Model unavailable - fallback keyword scoring"
                })

                continue

            # Ensure a valid object with required keys
            data = out if isinstance(out, dict) else {}
            data.setdefault("original", clause)
            data.setdefault("simplified", "")
            # Normalize risk
            risk_val = str(data.get("risk", "")).upper()
            if risk_val not in {"LOW", "MEDIUM", "HIGH"}:
                risk_val = assess_risk_by_keywords(clause)
            data["risk"] = risk_val
            data.setdefault("reason", data.get("explanation") or data.get("rationale") or "")

            results.append(data)
        print("\n🔍 Step 4: Enhancing risk assessment...")
        final_results = enhance_risk_assessment(results)
        print(f"✅ Analysis complete! Returning {len(final_results)} analyzed clauses\n")
        return JSONResponse(content={
            "success": True,
            "total_clauses": len(final_results),
            "clauses": final_results
        })

    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

    finally:
        # Clean temp file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
