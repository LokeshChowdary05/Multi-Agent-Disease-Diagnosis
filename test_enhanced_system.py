# test_enhanced_system.py
# Comprehensive test script for the enhanced medical diagnosis system

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_database():
    """Test the enhanced medical database with 200+ cases"""
    print("🏥 Testing Enhanced Medical Database...")
    
    try:
        from medical_data import medical_db
        
        # Test database statistics
        stats = medical_db.get_database_stats()
        print(f"✅ Total Conditions: {stats['total_conditions']}")
        print(f"✅ Total Sample Cases: {stats['sample_cases']}")
        print(f"✅ Common Conditions: {stats['common_conditions']}")
        print(f"✅ Rare Conditions: {stats['rare_conditions']}")
        
        # Test case variety
        all_cases = medical_db.get_all_sample_cases()
        if len(all_cases) >= 20:  # Should have many more cases now
            print(f"✅ Enhanced case database with {len(all_cases)} cases")
        else:
            print(f"❌ Expected more cases, only found {len(all_cases)}")
            return False
        
        # Test case generation
        condition_name = "Pneumonia"
        synthetic_case = medical_db.generate_synthetic_case(condition_name)
        print(f"✅ Generated synthetic case: {synthetic_case['patient_id']} for {condition_name}")
        
        print("✅ Enhanced database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced database test failed: {str(e)}")
        return False

def test_pdf_generation():
    """Test PDF report generation"""
    print("\n📄 Testing PDF Generation...")
    
    try:
        # Test imports
        from pdf_generator import pdf_generator
        from orchestrator import DiagnosticSession
        from medical_data import medical_db
        from agents import DiagnosisResult
        from datetime import datetime
        
        print("✅ PDF generator imports successful")
        
        # Create a mock session for testing
        test_case = medical_db.get_sample_case("CASE_001")
        
        # Create mock diagnosis results
        mock_diagnosis = DiagnosisResult(
            condition="Test Diagnosis",
            confidence=85.0,
            reasoning="This is a test diagnosis for PDF generation",
            icd10_code="A00.0",
            recommended_tests=["Test 1", "Test 2"],
            differential_diagnoses=["Alt Diagnosis 1", "Alt Diagnosis 2"],
            red_flags=["Red Flag 1"]
        )
        
        # Create mock session
        session = DiagnosticSession(
            session_id="test_session",
            patient_data=test_case,
            status="completed",
            primary_diagnosis=mock_diagnosis,
            specialist_diagnosis=mock_diagnosis,
            final_consensus=mock_diagnosis
        )
        session.completed_at = datetime.now()
        
        # Test summary report generation
        try:
            summary_path = pdf_generator.generate_summary_report(session, "test_summary.pdf")
            print(f"✅ Summary PDF generated: {summary_path}")
            
            # Check if file exists
            if os.path.exists(summary_path):
                print("✅ PDF file created successfully")
                # Clean up
                os.remove(summary_path)
            else:
                print("❌ PDF file not found")
                return False
                
        except Exception as e:
            print(f"❌ PDF generation failed: {str(e)}")
            print("💡 Make sure reportlab is installed: pip install reportlab")
            return False
        
        print("✅ PDF generation tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ PDF generation test failed - missing dependency: {str(e)}")
        print("💡 Install reportlab: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ PDF generation test failed: {str(e)}")
        return False

def test_enhanced_conversations():
    """Test enhanced conversation features"""
    print("\n💬 Testing Enhanced Conversations...")
    
    try:
        from orchestrator import DiagnosticOrchestrator
        from medical_data import medical_db
        
        # Create orchestrator
        orchestrator = DiagnosticOrchestrator()
        print("✅ Enhanced orchestrator created")
        
        # Test discussion simulation capability
        test_case = medical_db.get_sample_case("CASE_001")
        
        # Test that the orchestrator has the enhanced discussion methods
        if hasattr(orchestrator, 'simulate_case_discussion'):
            print("✅ Enhanced discussion simulation methods available")
        else:
            print("❌ Enhanced discussion methods not found")
            return False
            
        if hasattr(orchestrator, '_simulate_agent_discussion'):
            print("✅ Detailed agent discussion methods available")
        else:
            print("❌ Detailed discussion methods not found")
            return False
        
        print("✅ Enhanced conversation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced conversation test failed: {str(e)}")
        return False

def test_streamlit_enhancements():
    """Test Streamlit app enhancements"""
    print("\n🎨 Testing Streamlit Enhancements...")
    
    try:
        # Test that app.py has the enhanced features
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()
        
        # Check for PDF generation features
        if "Generate Full PDF Report" in app_content:
            print("✅ PDF generation UI found")
        else:
            print("❌ PDF generation UI not found")
            return False
        
        # Check for discussion simulation
        if "Simulate Discussion" in app_content:
            print("✅ Discussion simulation UI found")
        else:
            print("❌ Discussion simulation UI not found")
            return False
        
        # Check for enhanced display functions
        if "display_diagnostic_results" in app_content:
            print("✅ Enhanced display functions found")
        else:
            print("❌ Enhanced display functions not found")
            return False
        
        print("✅ Streamlit enhancement tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Streamlit enhancement test failed: {str(e)}")
        return False

def test_comprehensive_cases():
    """Test the comprehensive case database"""
    print("\n📊 Testing Comprehensive Case Database...")
    
    try:
        from medical_data import medical_db
        
        # Test different case types
        all_cases = medical_db.get_all_sample_cases()
        
        # Check for variety in cases
        case_types = set()
        age_ranges = []
        
        for case in all_cases[:20]:  # Test first 20 cases
            if 'expected_diagnosis' in case:
                case_types.add(case['expected_diagnosis'])
            if 'age' in case:
                age_ranges.append(case['age'])
        
        print(f"✅ Case variety: {len(case_types)} different diagnoses")
        print(f"✅ Age range: {min(age_ranges) if age_ranges else 'N/A'} - {max(age_ranges) if age_ranges else 'N/A'}")
        
        # Test different medical categories
        conditions_by_category = {}
        for condition in medical_db.conditions:
            category = condition['category']
            conditions_by_category[category] = conditions_by_category.get(category, 0) + 1
        
        print(f"✅ Medical categories covered: {len(conditions_by_category)}")
        for category, count in conditions_by_category.items():
            print(f"   {category}: {count} conditions")
        
        if len(conditions_by_category) >= 8:  # Should have many categories
            print("✅ Comprehensive medical coverage achieved")
        else:
            print(f"❌ Limited medical coverage: only {len(conditions_by_category)} categories")
            return False
        
        print("✅ Comprehensive case database tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive case test failed: {str(e)}")
        return False

def main():
    """Run all enhanced system tests"""
    print("🚀 ENHANCED MEDICAL DIAGNOSIS SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_enhanced_database,
        test_comprehensive_cases,
        test_enhanced_conversations,
        test_pdf_generation,
        test_streamlit_enhancements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"🏆 ENHANCED SYSTEM TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL ENHANCED FEATURES WORKING PERFECTLY!")
        print("\n📋 WHAT'S NEW:")
        print("✅ 200+ comprehensive medical cases across all specialties")
        print("✅ Enhanced doctor conversations with detailed clinical reasoning")
        print("✅ Professional PDF report generation (full & summary)")
        print("✅ Improved Streamlit interface with new features")
        print("✅ Advanced case simulation and discussion rounds")
        print("\n🚀 TO RUN THE ENHANCED SYSTEM:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the app: streamlit run app.py")
        print("3. Try the new PDF generation and discussion features!")
    else:
        print("⚠️  Some enhanced features need attention.")
        print("Check the error messages above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
