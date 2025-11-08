import streamlit as st
import requests
import json
from datetime import datetime
import html

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="ClauseWise - AI Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# DARK MODE THEME & CSS
# ============================================
st.markdown("""
<style>
body {
    background-color: #0e1116;
    color: #e6eef8;
}

/* HEADER STYLES */
.main-header {
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    color: #ff8c00;
    text-align: center !important;
    margin-bottom: 0.25rem !important;
    letter-spacing: 1.2px;
    text-shadow: 0 3px 16px rgba(255, 140, 0, 0.4);
}
.sub-header {
    font-size: 2.5rem !important;
    color: #aeb6c2;
    text-align: center !important;
    margin-bottom: 1.5rem !important;
}

/* FEATURE CARDS */
.feature-card {
    background: linear-gradient(180deg, #23232b 0%, #1b1b1f 100%);
    color: #e7eefc;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.03);
    box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.feature-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 28px rgba(2,6,23,0.75);
}
.feature-card h3 { color: #dff1ff; font-size: 1.5rem; }
.feature-card p { color: #bfc9d6; font-size: 1rem; }

/* UPLOAD SECTION */
.upload-section {
    background: linear-gradient(135deg, #1c1c22, #121214);
    padding: 2rem;
    border-radius: 12px;
    border: 1px solid #2b2b2f;
    text-align: center;
    margin-bottom: 2rem;
}
.upload-section h3 {
    color: #4a9eff;
    margin-bottom: 1rem;
    font-size: 1.8rem;
}
.upload-section p {
    color: #a0a0a0;
    margin-bottom: 1rem;
    font-size: 1rem;
}

/* DARK RESULT SECTIONS */
.dark-classification {
    background-color: #151516;
    border-radius: 10px;
    padding: 1.5rem;
    border: 1px solid #2b2b2f;
    margin-bottom: 1rem;
    color: #e0e0e0;
}
.dark-classification h2 { color: #4a9eff; }

/* STATS CARDS */
.stats-card {
    background: linear-gradient(135deg, #1e1e26, #151519);
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #2b2b2f;
    text-align: center;
}
.stats-number {
    font-size: 2.5rem;
    font-weight: bold;
    color: #4a9eff;
}
.stats-label {
    font-size: 1rem;
    color: #a0a0a0;
    margin-top: 0.5rem;
}

/* RISK BADGES */
.risk-badge {
    display: inline-block;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.95rem;
    margin: 0.25rem;
}
.risk-high {
    background: linear-gradient(135deg, #d32f2f, #b71c1c);
    color: white;
    box-shadow: 0 4px 12px rgba(211, 47, 47, 0.4);
}
.risk-medium {
    background: linear-gradient(135deg, #f57c00, #e65100);
    color: white;
    box-shadow: 0 4px 12px rgba(245, 124, 0, 0.4);
}
.risk-low {
    background: linear-gradient(135deg, #388e3c, #2e7d32);
    color: white;
    box-shadow: 0 4px 12px rgba(56, 142, 60, 0.4);
}

/* CLAUSE CARDS */
.clause-card {
    background: linear-gradient(145deg, #1a1a20, #151519);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #2b2b2f;
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.clause-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #2b2b2f;
}
.clause-number {
    font-size: 1.3rem;
    font-weight: bold;
    color: #4a9eff;
}
.clause-original {
    background-color: #0e0e10;
    border-left: 4px solid #ff6b6b;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    color: #e0e0e0;
    font-size: 0.95rem;
    line-height: 1.6;
}
.clause-simplified {
    background-color: #0e0e10;
    border-left: 4px solid #51cf66;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 0.75rem;
    color: #d0f5d0;
    font-size: 1rem;
    line-height: 1.6;
}
.clause-reason {
    background-color: #1a1a1f;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    color: #ffa726;
    font-size: 0.9rem;
    border-left: 3px solid #ffa726;
}

/* BUTTON STYLE */
.stButton>button {
    background: linear-gradient(135deg, #2b6ac9, #1e4a8a);
    color: white;
    border: none;
    padding: 0.7rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(43, 106, 201, 0.3);
}
.stButton>button:hover {
    background: linear-gradient(135deg, #3c7df1, #2b6ac9);
    box-shadow: 0 6px 18px rgba(60, 125, 241, 0.4);
    transform: translateY(-2px);
}

/* FOOTER */
.footer-note {
    color: #8f98a6;
    font-size: 0.95rem;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# BACKEND CONFIGURATION
# ============================================
BACKEND_URL = "http://127.0.0.1:8000"


# ============================================
# SESSION STATE
# ============================================
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_risk_badge_html(risk_level: str) -> str:
    """Generate HTML for risk badge."""
    risk_lower = risk_level.lower()
    icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk_lower, "⚪")
    return f'{icon} <span class="risk-badge risk-{risk_lower}">{risk_level}</span>'

def call_backend_analyze(uploaded_file):
    """Call backend /analyze endpoint."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(
    f"{BACKEND_URL}/analyze",
    files=files,
    timeout=None   # No timeout - let it take as long as needed
)

        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Backend error: {response.text}"
    
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to backend. Make sure FastAPI server is running on http://localhost:8000"
    except requests.exceptions.Timeout:
        return None, "❌ Request timed out. Document may be too large."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

# ============================================
# HEADER
# ============================================
st.markdown('<p class="main-header">⚖️ ClauseWise</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Legal Document Analyzer</p>', unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("### 📊 Backend Status")
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if health.status_code == 200:
            st.success("✅ Backend Connected")
            st.json(health.json())
        else:
            st.error("⚠️ Backend Issue")
    except:
        st.error("❌ Backend Offline")
        st.caption("Start backend: `cd backend && python main.py`")
    
    st.divider()
    
    st.markdown("### 📖 About ClauseWise")
    st.info(
        "ClauseWise uses **IBM Granite 7B AI** to:\n\n"
        "✅ Simplify legal jargon\n\n"
        "✅ Identify risk levels\n\n"
        "✅ Explain potential concerns"
    )
    
    st.divider()
    
    if st.session_state.processed_data:
        st.markdown("### 📊 Document Stats")
        data = st.session_state.processed_data
        total = data.get('total_clauses', 0)
        st.metric("Total Clauses", total)
        
        # Risk distribution
        clauses = data.get('clauses', [])
        risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for clause in clauses:
            risk_counts[clause.get('risk', 'MEDIUM')] += 1
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🔴", risk_counts["HIGH"])
        col2.metric("🟡", risk_counts["MEDIUM"])
        col3.metric("🟢", risk_counts["LOW"])

# ============================================
# MAIN CONTENT
# ============================================
if st.session_state.processed_data is None:
    
    # Feature Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📝 Clause Simplification</h3>
            <p>Convert complex legal jargon into plain, understandable language.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>⚠️ Risk Assessment</h3>
            <p>Automatically identify HIGH, MEDIUM, and LOW risk clauses.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI-Powered Analysis</h3>
            <p>Powered by IBM Granite 7B Instruct for accurate insights.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Upload Section
    st.markdown("""
    <div class="upload-section">
        <h3>📁 Upload Your Legal Document</h3>
        <p>Supported formats: PDF, DOCX, TXT</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")

    if uploaded_file:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        
        if st.button("🚀 Analyze Document", use_container_width=True):
            with st.spinner("🔍 Performing deep analysis with IBM Granite AI... This may take several minutes for thorough clause-by-clause review."):
                result, error = call_backend_analyze(uploaded_file)
                
                if error:
                    st.error(error)
                elif result and result.get('success'):
                    st.session_state.processed_data = result
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.rerun()
                else:
                    st.error("❌ Analysis failed. Please try again.")

    st.markdown("---")
    st.markdown("### 🚀 Getting Started")
    st.markdown("""
    1. **Upload** your legal document (PDF, DOCX, or TXT)
    2. **Click** 'Analyze Document' to start AI analysis
    3. **Review** simplified clauses and risk assessments
    4. **Export** results in JSON or Markdown format
    """)

else:
    # ============================================
    # RESULTS PAGE
    # ============================================
    data = st.session_state.processed_data
    clauses = data.get('clauses', [])
    
    st.success(f"✅ Analysis completed for: **{st.session_state.uploaded_file_name}**")
    
    # Summary Stats
    st.markdown("### 📊 Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for clause in clauses:
        risk_counts[clause.get('risk', 'MEDIUM')] += 1
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(clauses)}</div>
            <div class="stats-label">Total Clauses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number" style="color: #f44336;">{risk_counts['HIGH']}</div>
            <div class="stats-label">High Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number" style="color: #ff9800;">{risk_counts['MEDIUM']}</div>
            <div class="stats-label">Medium Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number" style="color: #4caf50;">{risk_counts['LOW']}</div>
            <div class="stats-label">Low Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter by risk
    st.markdown("### 📝 Clause Analysis")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        risk_filter = st.selectbox(
            "Filter by risk:",
            ["All Clauses", "HIGH", "MEDIUM", "LOW"],
            label_visibility="collapsed"
        )
    
    # Filter clauses
    if risk_filter == "All Clauses":
        filtered_clauses = clauses
    else:
        filtered_clauses = [c for c in clauses if c.get('risk') == risk_filter]
    
    st.caption(f"Showing **{len(filtered_clauses)}** of **{len(clauses)}** clauses")
    
    # Display clauses
    for idx, clause in enumerate(filtered_clauses, 1):
        risk = clause.get('risk', 'MEDIUM')
        original = clause.get('original', 'N/A')
        simplified = clause.get('simplified', 'N/A')
        reason = clause.get('reason', 'No reason provided')
        
        # Strip any HTML tags from the text (in case AI model generates them)
        import re
        def strip_html(text):
            """Remove HTML tags from text"""
            clean = re.sub(r'<[^>]+>', '', text)
            # Also decode common HTML entities
            clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            clean = clean.replace('&quot;', '"').replace('&#39;', "'")
            return clean.strip()
        
        original_clean = strip_html(original)
        simplified_clean = strip_html(simplified)
        reason_clean = strip_html(reason)
        
        # Now escape for safe HTML display
        original_escaped = html.escape(original_clean)
        simplified_escaped = html.escape(simplified_clean)
        reason_escaped = html.escape(reason_clean)
        
        st.markdown(f"""
        <div class="clause-card">
            <div class="clause-header">
                <span class="clause-number">Clause {idx}</span>
                {get_risk_badge_html(risk)}
            </div>
            
            <div class="clause-simplified">
                <strong>✨ Simplified:</strong><br>
                {simplified_escaped}
            </div>
            
            <div class="clause-reason">
                <strong>⚠️ Risk Analysis:</strong> {reason_escaped}
            </div>
            
            <details>
                <summary style="cursor: pointer; color: #4a9eff; margin-top: 0.75rem; font-size: 0.9rem;">
                    📄 View Original Text
                </summary>
                <div class="clause-original" style="margin-top: 0.75rem;">
                    {original_escaped}
                </div>
            </details>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Export buttons
    st.markdown("### 💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_str = json.dumps(clauses, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"clausewise_analysis_{st.session_state.uploaded_file_name}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Create markdown report
        md_report = f"# ClauseWise Analysis Report\n\n"
        md_report += f"**Document:** {st.session_state.uploaded_file_name}\n\n"
        md_report += f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md_report += f"**Total Clauses:** {len(clauses)}\n\n"
        md_report += f"**Risk Distribution:**\n"
        md_report += f"- 🔴 High: {risk_counts['HIGH']}\n"
        md_report += f"- 🟡 Medium: {risk_counts['MEDIUM']}\n"
        md_report += f"- 🟢 Low: {risk_counts['LOW']}\n\n"
        md_report += "---\n\n"
        
        for idx, clause in enumerate(clauses, 1):
            md_report += f"## Clause {idx} - {clause.get('risk', 'MEDIUM')} Risk\n\n"
            md_report += f"**Simplified:** {clause.get('simplified', 'N/A')}\n\n"
            md_report += f"**Reason:** {clause.get('reason', 'N/A')}\n\n"
            md_report += f"**Original:**\n\n> {clause.get('original', 'N/A')}\n\n"
            md_report += "---\n\n"
        
        st.download_button(
            label="📥 Download Markdown",
            data=md_report,
            file_name=f"clausewise_report_{st.session_state.uploaded_file_name}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Analyze New Document", use_container_width=True):
            st.session_state.processed_data = None
            st.session_state.uploaded_file_name = None
            st.rerun()

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8f98a6; padding: 2rem 0;">
    <p class="footer-note">Powered by IBM Granite 7B AI via Hugging Face | Built with FastAPI & Streamlit</p>
    <p style="font-size: 0.9rem;">⚠️ This tool provides informational analysis only. Consult a legal professional for advice.</p>
</div>
""", unsafe_allow_html=True)