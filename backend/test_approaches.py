"""
Test script to compare single-pass vs two-pass analysis approaches
Run this to see which approach works better for your use case
"""

# Test clauses with known risk levels
TEST_CLAUSES = [
    {
        "text": "The Company may terminate this Agreement at any time, for any reason or no reason, without prior notice and without liability to the Contractor.",
        "expected_risk": "HIGH",
        "reason": "Unilateral termination without notice"
    },
    {
        "text": "The Employee agrees to indemnify and hold harmless the Company from any and all claims, damages, losses, and expenses arising from the Employee's actions.",
        "expected_risk": "HIGH",
        "reason": "Unlimited indemnification clause"
    },
    {
        "text": "All confidential information disclosed during the term of this Agreement shall remain the property of the disclosing party and shall not be disclosed to third parties.",
        "expected_risk": "MEDIUM",
        "reason": "Standard confidentiality obligation"
    },
    {
        "text": "Either party may terminate this Agreement upon thirty (30) days written notice to the other party.",
        "expected_risk": "LOW",
        "reason": "Mutual termination with notice period"
    },
    {
        "text": "This Agreement shall become effective on the date first written above and shall continue until terminated in accordance with its terms.",
        "expected_risk": "LOW",
        "reason": "Standard effective date clause"
    }
]

def test_single_pass():
    """Test the current single-pass approach"""
    print("\n" + "="*80)
    print("TESTING SINGLE-PASS APPROACH (granite_api.py)")
    print("="*80)
    
    try:
        from granite_api import call_granite
        
        results = []
        for i, test in enumerate(TEST_CLAUSES, 1):
            print(f"\n--- Test Case {i}/{len(TEST_CLAUSES)} ---")
            print(f"Clause: {test['text'][:80]}...")
            print(f"Expected Risk: {test['expected_risk']}")
            
            success, result = call_granite(test['text'])
            
            if success:
                actual_risk = result.get('risk', 'UNKNOWN')
                match = "✅ CORRECT" if actual_risk == test['expected_risk'] else "❌ WRONG"
                
                print(f"Actual Risk: {actual_risk} {match}")
                print(f"Simplified: {result.get('simplified', 'N/A')[:100]}...")
                print(f"Reason: {result.get('reason', 'N/A')[:100]}...")
                
                results.append({
                    "test": i,
                    "expected": test['expected_risk'],
                    "actual": actual_risk,
                    "correct": actual_risk == test['expected_risk']
                })
            else:
                print("❌ Analysis failed")
                results.append({
                    "test": i,
                    "expected": test['expected_risk'],
                    "actual": "FAILED",
                    "correct": False
                })
        
        # Summary
        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print(f"SINGLE-PASS RESULTS: {correct}/{total} correct ({accuracy:.1f}% accuracy)")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing single-pass: {e}")
        return []

def test_two_pass():
    """Test the two-pass approach"""
    print("\n" + "="*80)
    print("TESTING TWO-PASS APPROACH (granite_api_advanced.py)")
    print("="*80)
    
    try:
        from granite_api_advanced import call_granite
        
        results = []
        for i, test in enumerate(TEST_CLAUSES, 1):
            print(f"\n--- Test Case {i}/{len(TEST_CLAUSES)} ---")
            print(f"Clause: {test['text'][:80]}...")
            print(f"Expected Risk: {test['expected_risk']}")
            
            success, result = call_granite(test['text'])
            
            if success:
                actual_risk = result.get('risk', 'UNKNOWN')
                match = "✅ CORRECT" if actual_risk == test['expected_risk'] else "❌ WRONG"
                
                print(f"Actual Risk: {actual_risk} {match}")
                print(f"Simplified: {result.get('simplified', 'N/A')[:100]}...")
                print(f"Reason: {result.get('reason', 'N/A')[:100]}...")
                
                results.append({
                    "test": i,
                    "expected": test['expected_risk'],
                    "actual": actual_risk,
                    "correct": actual_risk == test['expected_risk']
                })
            else:
                print("❌ Analysis failed")
                results.append({
                    "test": i,
                    "expected": test['expected_risk'],
                    "actual": "FAILED",
                    "correct": False
                })
        
        # Summary
        correct = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = (correct / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print(f"TWO-PASS RESULTS: {correct}/{total} correct ({accuracy:.1f}% accuracy)")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing two-pass: {e}")
        return []

if __name__ == "__main__":
    print("\n" + "🔬 CLAUSEWISE PROMPT ENGINEERING TEST SUITE" + "\n")
    print("This will test both approaches on 5 sample clauses")
    print("Expected processing time: 5-10 minutes total\n")
    
    input("Press Enter to start testing...")
    
    # Test current approach (single-pass)
    single_results = test_single_pass()
    
    print("\n\n" + "⏸️  PAUSE" + "\n")
    print("To test the two-pass approach:")
    print("1. Backup: copy granite_api.py granite_api_single.py")
    print("2. Switch: copy granite_api_advanced.py granite_api.py")
    print("3. Run this script again")
    print("\nOr press Enter to skip two-pass testing...")
    
    input()
    
    # Optionally test two-pass if available
    try:
        two_results = test_two_pass()
        
        # Comparison
        if single_results and two_results:
            print("\n" + "="*80)
            print("📊 COMPARISON")
            print("="*80)
            
            single_correct = sum(1 for r in single_results if r['correct'])
            two_correct = sum(1 for r in two_results if r['correct'])
            
            print(f"Single-Pass: {single_correct}/5 correct")
            print(f"Two-Pass:    {two_correct}/5 correct")
            
            if two_correct > single_correct:
                print("\n✅ Two-Pass approach is more accurate")
            elif single_correct > two_correct:
                print("\n✅ Single-Pass approach is more accurate")
            else:
                print("\n🤝 Both approaches have equal accuracy")
                
    except ImportError:
        print("Two-pass approach not available (granite_api_advanced.py not active)")
    
    print("\n✅ Testing complete!")
