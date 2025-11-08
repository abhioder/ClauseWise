import re
from typing import Dict, List

# Keyword-based risk indicators
HIGH_RISK_KEYWORDS = [
    'indemnify', 'indemnification', 'hold harmless',
    'unlimited liability', 'sole discretion', 'unilateral',
    'irrevocable', 'perpetual', 'exclusive rights',
    'waive', 'waiver', 'non-compete', 'non-solicitation'
]

MEDIUM_RISK_KEYWORDS = [
    'termination', 'breach', 'default', 'remedy',
    'arbitration', 'jurisdiction', 'governing law',
    'confidential', 'proprietary', 'intellectual property'
]

def assess_risk_by_keywords(clause_text: str) -> str:
    """
    Fallback keyword-based risk assessment.
    Returns: 'HIGH', 'MEDIUM', or 'LOW'
    """
    
    clause_lower = clause_text.lower()
    
    # Check for high-risk keywords
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in clause_lower:
            return 'HIGH'
    
    # Check for medium-risk keywords
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in clause_lower:
            return 'MEDIUM'
    
    return 'LOW'

def enhance_risk_assessment(results: List[Dict]) -> List[Dict]:
    """
    Hybrid approach: Use model risk but validate with keywords.
    If model says LOW but keywords suggest HIGH, upgrade to MEDIUM.
    """
    
    enhanced = []
    
    for result in results:
        model_risk = result['risk']
        keyword_risk = assess_risk_by_keywords(result['original'])
        
        # If there's a major discrepancy, take the higher risk
        if model_risk == 'LOW' and keyword_risk == 'HIGH':
            final_risk = 'MEDIUM'  # Conservative upgrade
            result['reason'] += ' (Keyword-flagged)'
        else:
            final_risk = model_risk
        
        enhanced.append({
            **result,
            'risk': final_risk
        })
    
    return enhanced