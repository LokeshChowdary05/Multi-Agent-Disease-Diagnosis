#!/usr/bin/env python3
"""
Debug script to test the simulate discussion functionality specifically
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from medical_data import medical_db
from orchestrator import DiagnosticOrchestrator, DiagnosticSession
from agents import DiagnosisResult

async def test_simulate_discussion_directly():
    """Test simulate discussion functionality directly"""
    print("🔧 Testing Simulate Discussion Functionality Directly...")
    
    try:
        # Create orchestrator
        orchestrator = DiagnosticOrchestrator()
        
        # Get a sample case
        sample_case = medical_db.get_sample_case("CASE_001")
        print(f"✅ Got sample case: {sample_case['patient_id']}")
        
        # Create session just like the app does
        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = DiagnosticSession(
            session_id=session_id,
            patient_data=sample_case,
            status="completed"
        )
        
        # Add mock diagnoses (simulating completed diagnostic process)
        session.primary_diagnosis = DiagnosisResult(
            condition="Myocardial Infarction",
            confidence=75.0,
            reasoning="Based on chest pain and risk factors",
            icd10_code="I21.9",
            recommended_tests=["ECG", "Troponin"],
            differential_diagnoses=["Unstable Angina", "Aortic Dissection"],
            red_flags=["Time-sensitive condition"]
        )
        
        session.specialist_diagnosis = DiagnosisResult(
            condition="ST-Elevation Myocardial Infarction",
            confidence=85.0,
            reasoning="Cardiology assessment confirms STEMI",
            icd10_code="I21.02",
            recommended_tests=["Cardiac catheterization", "Echo"],
            differential_diagnoses=["NSTEMI"],
            red_flags=["Urgent intervention needed"]
        )
        
        session.final_consensus = DiagnosisResult(
            condition="ST-Elevation Myocardial Infarction",
            confidence=90.0,
            reasoning="Team consensus on STEMI diagnosis",
            icd10_code="I21.02",
            recommended_tests=["Immediate PCI"],
            differential_diagnoses=["Confirmed diagnosis"],
            red_flags=["Critical timing"]
        )
        
        session.completed_at = datetime.now()
        
        print(f"✅ Created session: {session.session_id}")
        print(f"   Status: {session.status}")
        print(f"   Has primary diagnosis: {session.primary_diagnosis is not None}")
        print(f"   Has specialist diagnosis: {session.specialist_diagnosis is not None}")
        print(f"   Has final consensus: {session.final_consensus is not None}")
        
        # Add to orchestrator like the app does
        orchestrator.active_sessions[session.session_id] = session
        print(f"✅ Added session to orchestrator")
        print(f"   Session in active_sessions: {session.session_id in orchestrator.active_sessions}")
        
        # Test the get_session method
        retrieved_session = orchestrator.get_session(session.session_id)
        print(f"✅ Retrieved session: {retrieved_session is not None}")
        print(f"   Retrieved session status: {retrieved_session.status if retrieved_session else 'None'}")
        
        # Now test simulate_case_discussion
        print(f"🎯 Testing simulate_case_discussion...")
        
        conversation_count_before = len(session.conversations)
        print(f"   Conversations before: {conversation_count_before}")
        
        # This is the exact call from the app
        updated_session = await orchestrator.simulate_case_discussion(session.session_id, discussion_rounds=1)
        
        conversation_count_after = len(updated_session.conversations)
        print(f"   Conversations after: {conversation_count_after}")
        print(f"   New conversations added: {conversation_count_after - conversation_count_before}")
        
        # Show some conversation details
        if updated_session.conversations:
            print(f"\\n📝 Sample conversations added:")
            for i, conv in enumerate(updated_session.conversations[-3:]):  # Show last 3
                print(f"   {i+1}. [{conv.agent_role}] {conv.agent_name}: {conv.content[:100]}...")
        
        print(f"\\n✅ Simulate discussion test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Simulate discussion test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_simulate_discussion_with_invalid_session():
    """Test what happens with invalid session"""
    print(f"\\n🔧 Testing with invalid session...")
    
    try:
        orchestrator = DiagnosticOrchestrator()
        
        # Try with non-existent session
        await orchestrator.simulate_case_discussion("invalid_session_123", discussion_rounds=1)
        print(f"❌ Should have failed but didn't!")
        return False
        
    except ValueError as e:
        print(f"✅ Correctly caught ValueError: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def run_debug_tests():
    """Run debug tests"""
    print("🚀 Running Simulate Discussion Debug Tests...\\n")
    
    test1_result = await test_simulate_discussion_directly()
    test2_result = await test_simulate_discussion_with_invalid_session()
    
    print(f"\\n📊 DEBUG TEST RESULTS:")
    print(f"Direct simulation test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Invalid session test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print(f"\\n🎉 ALL DEBUG TESTS PASSED!")
        print(f"\\n💡 The simulate_case_discussion function is working correctly.")
        print(f"   If the Streamlit button isn't working, the issue is likely:")
        print(f"   1. Session state management in Streamlit")
        print(f"   2. Async execution in Streamlit context")
        print(f"   3. Error handling/display in the UI")
        print(f"\\n🔧 Check the Streamlit console for error messages when clicking the button.")
    else:
        print(f"\\n❌ Some tests failed - there may be an issue with the function itself.")
    
    return test1_result and test2_result

if __name__ == "__main__":
    success = asyncio.run(run_debug_tests())
    sys.exit(0 if success else 1)
