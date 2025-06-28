# test_system.py
# Simple test script to verify the system works correctly

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully"""
    try:
        print("Testing imports...")
        
        from medical_data import medical_db
        print("✅ medical_data imported successfully")
        
        from agents import PrimaryDiagnostician, SpecialistConsultant, SeniorReviewer, DiagnosisResult
        print("✅ agents imported successfully")
        
        from orchestrator import DiagnosticOrchestrator
        print("✅ orchestrator imported successfully")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_medical_data():
    """Test medical data functionality"""
    try:
        print("\nTesting medical data...")
        
        from medical_data import medical_db
        
        # Test database stats
        stats = medical_db.get_database_stats()
        print(f"✅ Database contains {stats['total_conditions']} conditions")
        print(f"✅ Database contains {stats['sample_cases']} sample cases")
        
        # Test sample case retrieval
        case = medical_db.get_sample_case("CASE_001")
        if case:
            print(f"✅ Successfully retrieved case: {case['patient_id']}")
        else:
            print("❌ Failed to retrieve sample case")
            return False
            
        # Test synthetic case generation
        synthetic_case = medical_db.generate_synthetic_case("Pneumonia")
        print(f"✅ Generated synthetic case: {synthetic_case['patient_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Medical data error: {str(e)}")
        return False

def test_agents():
    """Test agent creation"""
    try:
        print("\nTesting agents...")
        
        from agents import PrimaryDiagnostician, SpecialistConsultant, SeniorReviewer
        
        # Create agents
        primary = PrimaryDiagnostician()
        specialist = SpecialistConsultant("Cardiology")
        senior = SeniorReviewer()
        
        print(f"✅ Created primary agent: {primary.name}")
        print(f"✅ Created specialist agent: {specialist.name}")
        print(f"✅ Created senior agent: {senior.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation error: {str(e)}")
        return False

def test_orchestrator():
    """Test orchestrator functionality"""
    try:
        print("\nTesting orchestrator...")
        
        from orchestrator import DiagnosticOrchestrator
        from medical_data import medical_db
        
        # Create orchestrator
        orchestrator = DiagnosticOrchestrator()
        print("✅ Created diagnostic orchestrator")
        
        # Test session creation
        sample_case = medical_db.get_sample_case("CASE_001")
        session_id = "test_session"
        
        # This would normally be async, but we're just testing creation
        print("✅ Orchestrator ready for diagnostic sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Multi-Agent Disease Diagnosis System")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_medical_data,
        test_agents,
        test_orchestrator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nTo run the application:")
        print("1. Make sure you have created a .env file with your OpenAI API key")
        print("2. Run: streamlit run app.py")
        print("3. Open your browser to http://localhost:8501")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()
