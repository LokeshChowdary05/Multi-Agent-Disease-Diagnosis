#!/usr/bin/env python3
"""
Quick test to verify the simulate discussion functionality in the app context
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

def test_app_scenario():
    """Test the exact scenario that happens in the app"""
    print("🧪 Testing Simulate Discussion Button Scenario...")
    
    try:
        # Create orchestrator (like in app.py)
        orchestrator = DiagnosticOrchestrator()
        
        # Get a sample case (like when user selects a case)
        selected_case = medical_db.get_sample_case("CASE_001")
        print(f"✅ Selected case: {selected_case['patient_id']}")
        
        # Simulate completed diagnostic session (like after running diagnosis)
        session = DiagnosticSession(
            session_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            patient_data=selected_case,
            status="completed"
        )
        
        # Add all three diagnoses (like after completing diagnostic process)
        session.primary_diagnosis = DiagnosisResult(
            condition="Myocardial Infarction",
            confidence=75.0,
            reasoning="Primary assessment based on symptoms",
            icd10_code="I21.9",
            recommended_tests=["ECG", "Troponin"],
            differential_diagnoses=["Unstable Angina"],
            red_flags=["Time-sensitive"]
        )
        
        session.specialist_diagnosis = DiagnosisResult(
            condition="ST-Elevation Myocardial Infarction",
            confidence=85.0,
            reasoning="Cardiology specialist assessment",
            icd10_code="I21.02",
            recommended_tests=["Cardiac catheterization"],
            differential_diagnoses=["NSTEMI"],
            red_flags=["Urgent intervention"]
        )
        
        session.final_consensus = DiagnosisResult(
            condition="ST-Elevation Myocardial Infarction",
            confidence=90.0,
            reasoning="Final consensus diagnosis",
            icd10_code="I21.02",
            recommended_tests=["Immediate PCI"],
            differential_diagnoses=["Confirmed"],
            red_flags=["Critical timing"]
        )
        
        session.completed_at = datetime.now()
        
        print(f"✅ Created completed session with all diagnoses")
        print(f"   Session ID: {session.session_id}")
        print(f"   Status: {session.status}")
        print(f"   Primary: {session.primary_diagnosis.condition}")
        print(f"   Specialist: {session.specialist_diagnosis.condition}")
        print(f"   Consensus: {session.final_consensus.condition}")
        
        # Add to orchestrator (like in the app)
        orchestrator.active_sessions[session.session_id] = session
        print(f"✅ Added session to orchestrator")
        
        # Verify session is accessible
        test_session = orchestrator.get_session(session.session_id)
        print(f"✅ Session retrievable: {test_session is not None}")
        print(f"   Retrieved status: {test_session.status}")
        
        # Now simulate clicking the "Simulate Discussion" button
        print(f"\\n🎯 Simulating button click...")
        
        # Validation checks (like in the app)
        if not session:
            print("❌ Validation failed: No session")
            return False
            
        if session.status != "completed":
            print(f"❌ Validation failed: Status is {session.status}, not completed")
            return False
            
        if not (session.primary_diagnosis and session.specialist_diagnosis and session.final_consensus):
            print("❌ Validation failed: Missing diagnoses")
            return False
            
        print("✅ All validations passed")
        
        # Ensure session is in orchestrator (like in the app)
        if session.session_id not in orchestrator.active_sessions:
            orchestrator.active_sessions[session.session_id] = session
            print("📝 Added session to orchestrator")
            
        # Verify session is accessible
        test_session = orchestrator.get_session(session.session_id)
        if not test_session:
            print("❌ Failed to register session in orchestrator")
            return False
            
        print("✅ Session verified in orchestrator")
        
        # Store conversation count before
        conversation_count_before = len(session.conversations)
        print(f"   Conversations before: {conversation_count_before}")
        
        # Run the simulation (like in the app with asyncio handling)
        async def run_simulation():
            return await orchestrator.simulate_case_discussion(session.session_id, discussion_rounds=2)
        
        # Create event loop (like in the app)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the simulation
        updated_session = loop.run_until_complete(run_simulation())
        
        # Verify results
        conversation_count_after = len(updated_session.conversations)
        new_conversations = conversation_count_after - conversation_count_before
        
        print(f"✅ Simulation completed successfully!")
        print(f"   Conversations after: {conversation_count_after}")
        print(f"   New conversations: {new_conversations}")
        
        # Show sample conversations
        if updated_session.conversations:
            print(f"\\n📝 Sample new conversations:")
            for i, conv in enumerate(updated_session.conversations[-min(3, new_conversations):]):
                print(f"   {i+1}. [{conv.agent_role}] {conv.agent_name}: {conv.content[:100]}...")
        
        print(f"\\n🎉 TEST PASSED - Simulate Discussion button scenario works correctly!")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_scenario()
    if success:
        print(f"\\n✅ The Simulate Discussion button should now work properly in the Streamlit app!")
        print(f"   Run: streamlit run app.py")
    else:
        print(f"\\n❌ There are still issues with the simulate discussion functionality.")
    
    sys.exit(0 if success else 1)
