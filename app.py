# app.py
# Streamlit application for visualizing the multi-agent clinical diagnosis process.
# Features real-time conversation display, agent avatars, and confidence visualizations.

import streamlit as st
import asyncio
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import time
from typing import Dict, Any

# Import our modules
from orchestrator import DiagnosticOrchestrator
from medical_data import medical_db
from agents import DiagnosisResult

# Function definitions (must be defined before they are called)
def simulate_diagnostic_process(case_data, specialty, progress_bar, status_text, container):
    """Simulate the diagnostic process for demo purposes"""
    
    import time
    from agents import DiagnosisResult, ConversationMessage
    from orchestrator import DiagnosticSession
    
    # Create mock session
    session = DiagnosticSession(
        session_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        patient_data=case_data,
        status="in_progress"
    )
    
    # Display system message
    display_agent_message(container, "System", "Diagnostic System", 
                         "🏥 **Starting multi-agent diagnostic consultation...**\n\nThree physicians will now review this case:", "system")
    time.sleep(1)
    
    # Step 1: Primary Assessment with conversation
    progress_bar.progress(0.1)
    status_text.text("🩺 Primary Care Physician analyzing case...")
    
    # Primary physician introduction
    display_agent_message(container, "Dr. Sarah Primary", "Primary Care Physician", 
                         f"🩺 **Good morning, colleagues. I'm reviewing this case of a {case_data['age']}-year-old {case_data['sex'].lower()} patient.**\n\n**Chief Complaint:** {case_data['chief_complaint']}\n\n**Initial Assessment:** Let me analyze the presenting symptoms...", "primary")
    time.sleep(2)
    
    # Adapt diagnosis based on case
    symptoms_str = str(case_data.get('symptoms', [])).lower()
    if "chest pain" in symptoms_str:
        condition = "Acute Coronary Syndrome"
        reasoning = "Based on the presenting symptoms of chest pain, associated symptoms, and patient demographics, I'm highly concerned about acute coronary syndrome. The clinical presentation fits a typical cardiac event pattern."
        icd10 = "I24.9"
        tests = ["12-lead ECG", "Troponin levels", "Complete metabolic panel", "Chest X-ray"]
        differentials = ["Myocardial Infarction", "Unstable Angina", "Pulmonary Embolism", "Aortic Dissection"]
        red_flags = ["Time-sensitive condition", "Risk of sudden cardiac death"]
    elif "abdominal pain" in symptoms_str:
        condition = "Acute Abdominal Pain - Surgical Concern"
        reasoning = "The presentation of acute abdominal pain, especially in the context described, raises concern for a surgical abdomen. The location, quality, and associated symptoms guide my differential."
        icd10 = "R10.9"
        tests = ["Complete blood count", "Comprehensive metabolic panel", "Lipase", "CT abdomen/pelvis", "Urinalysis"]
        differentials = ["Appendicitis", "Cholecystitis", "Pancreatitis", "Bowel obstruction"]
        red_flags = ["Peritoneal signs", "Hemodynamic instability"]
    else:
        condition = case_data.get('expected_diagnosis', 'Clinical Assessment Required')
        reasoning = f"Based on the presenting symptoms of {', '.join(case_data.get('symptoms', []))}, I need to consider several diagnostic possibilities. The patient's age, sex, and symptom pattern will guide my assessment."
        icd10 = case_data.get('expected_icd10', 'TBD')
        tests = ["Basic metabolic panel", "Complete blood count", "Appropriate imaging"]
        differentials = ["Multiple possibilities under consideration"]
        red_flags = ["Monitoring for clinical deterioration"]
    
    primary_diagnosis = DiagnosisResult(
        condition=condition,
        confidence=75.0,
        reasoning=reasoning,
        icd10_code=icd10,
        recommended_tests=tests,
        differential_diagnoses=differentials,
        red_flags=red_flags
    )
    
    session.primary_diagnosis = primary_diagnosis
    display_agent_message(container, "Dr. Sarah Primary", "Primary Care Physician", 
                         create_diagnosis_summary(primary_diagnosis), "primary")
    
    # Step 2: Specialist Consultation with conversation
    progress_bar.progress(0.4)
    status_text.text(f"🔬 {specialty} Specialist reviewing case...")
    time.sleep(1)
    
    # Specialist introduction and discussion
    display_agent_message(container, f"Dr. Michael {specialty.split()[0]}", f"{specialty} Specialist", 
                         f"🔬 **Thank you, Dr. Primary. As a {specialty.lower()} specialist, let me provide my perspective on this case.**\n\n**Specialist Review:** I've reviewed the primary assessment and agree with the general approach. Let me focus on the specialized aspects...", "specialist")
    time.sleep(2)
    
    # Enhanced specialist diagnosis
    specialist_reasoning = f"From a {specialty.lower()} perspective, this case presents several important considerations. I concur with Dr. Primary's initial assessment but would like to refine the diagnosis and management approach based on my specialized expertise."
    
    specialist_diagnosis = DiagnosisResult(
        condition=f"Refined {specialty} Assessment: {condition}",
        confidence=85.0,
        reasoning=specialist_reasoning,
        icd10_code=icd10,
        recommended_tests=tests + [f"Specialized {specialty.lower()} workup"],
        differential_diagnoses=differentials,
        red_flags=red_flags + ["Specialist monitoring required"]
    )
    
    session.specialist_diagnosis = specialist_diagnosis
    display_agent_message(container, f"Dr. Michael {specialty.split()[0]}", f"{specialty} Specialist",
                         create_diagnosis_summary(specialist_diagnosis), "specialist")
    
    # Interdisciplinary discussion
    progress_bar.progress(0.6)
    status_text.text("💬 Physicians discussing case...")
    time.sleep(1)
    
    display_agent_message(container, "Dr. Sarah Primary", "Primary Care Physician", 
                         f"**Discussion with Specialist:** Dr. {specialty.split()[0]}, I appreciate your input. Do you agree with the urgency level I've assigned? Should we consider any additional immediate interventions?", "primary")
    time.sleep(1)
    
    display_agent_message(container, f"Dr. Michael {specialty.split()[0]}", f"{specialty} Specialist", 
                         f"**Response:** Absolutely, Dr. Primary. The urgency is appropriate. I would add that from a {specialty.lower()} standpoint, we should also consider [specific specialist considerations]. The diagnostic workup you've outlined is comprehensive.", "specialist")
    time.sleep(1)
    
    # Step 3: Senior Review with conversation
    progress_bar.progress(0.8)
    status_text.text("👨‍⚕️ Senior Attending reviewing assessments...")
    time.sleep(1)
    
    display_agent_message(container, "Dr. Robert Senior", "Senior Attending Physician", 
                         "👨‍⚕️ **Excellent work, colleagues. As the senior attending, let me provide the final synthesis and consensus.**\n\n**Senior Review:** I've carefully reviewed both assessments and the clinical discussion. Here's my final consensus...", "senior")
    time.sleep(2)
    
    final_consensus = DiagnosisResult(
        condition=f"Final Consensus: {condition}",
        confidence=90.0,
        reasoning=f"After thorough review by our multidisciplinary team, we have reached consensus on this case. Both Dr. Primary and Dr. {specialty.split()[0]} have provided excellent assessments. The clinical picture is consistent with our final diagnosis, and the management plan is appropriate and comprehensive.",
        icd10_code=icd10,
        recommended_tests=["Proceed with recommended workup", "Serial monitoring", "Multidisciplinary follow-up"],
        differential_diagnoses=["Consensus reached on primary diagnosis"],
        red_flags=["Continue vigilant monitoring", "Escalate if clinical change"]
    )
    
    session.final_consensus = final_consensus
    display_agent_message(container, "Dr. Robert Senior", "Senior Attending Physician",
                         create_diagnosis_summary(final_consensus), "senior")
    
    # Closing discussion
    time.sleep(1)
    display_agent_message(container, "Dr. Robert Senior", "Senior Attending Physician", 
                         "**Closing Remarks:** This case demonstrates excellent collaborative medicine. Our patient will receive optimal care through this multidisciplinary approach. Please proceed with the agreed-upon management plan.", "senior")
    
    # Complete
    progress_bar.progress(1.0)
    status_text.text("✅ Diagnostic consultation completed!")
    session.status = "completed"
    session.completed_at = datetime.now()
    
    return session

def run_real_diagnostic_process(case_data, specialty, progress_bar, status_text, container):
    """Run the actual diagnostic process with OpenAI API"""
    
    # This would require OpenAI API key to be set
    st.warning("Real API mode requires OpenAI API key. Using demo mode instead.")
    return simulate_diagnostic_process(case_data, specialty, progress_bar, status_text, container)

def create_diagnosis_summary(diagnosis: DiagnosisResult) -> str:
    """Create a formatted summary of a diagnosis"""
    
    confidence_class = "confidence-high" if diagnosis.confidence >= 80 else "confidence-medium" if diagnosis.confidence >= 60 else "confidence-low"
    
    return f"""
**Diagnosis:** {diagnosis.condition}

<span class="{confidence_class}">**Confidence Level:** {diagnosis.confidence}%</span>

**Clinical Reasoning:**
{diagnosis.reasoning}

**Recommended Tests:**
{', '.join(diagnosis.recommended_tests) if diagnosis.recommended_tests else 'None specified'}

**Differential Diagnoses:**
{', '.join(diagnosis.differential_diagnoses) if diagnosis.differential_diagnoses else 'None specified'}

**Red Flags:**
{', '.join(diagnosis.red_flags) if diagnosis.red_flags else 'None identified'}

**ICD-10 Code:** {diagnosis.icd10_code if diagnosis.icd10_code else 'Not specified'}
    """

def display_agent_message(container, agent_name, agent_role, content, agent_type):
    """Display an agent message with appropriate styling"""
    
    with container:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Agent avatar/icon based on type
        avatar = {
            "primary": "🩺",
            "specialist": "🔬", 
            "senior": "👨‍⚕️",
            "system": "🤖"
        }.get(agent_type, "👤")
        
        st.markdown(f"""
        <div class="agent-{agent_type}">
        <strong>{avatar} {agent_name} ({agent_role}) - {timestamp}</strong><br>
        {content}
        </div>
        """, unsafe_allow_html=True)

def display_diagnostic_results(session):
    """Display comprehensive diagnostic results"""
    
    st.header("📊 Diagnostic Results Summary")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Final Confidence",
            f"{session.final_consensus.confidence}%" if session.final_consensus else "N/A",
            delta=None
        )
    
    with col2:
        st.metric(
            "Primary Confidence", 
            f"{session.primary_diagnosis.confidence}%" if session.primary_diagnosis else "N/A"
        )
    
    with col3:
        st.metric(
            "Specialist Confidence",
            f"{session.specialist_diagnosis.confidence}%" if session.specialist_diagnosis else "N/A"
        )
    
    with col4:
        duration = "N/A"
        if session.completed_at and session.created_at:
            duration = f"{(session.completed_at - session.created_at).total_seconds():.1f}s"
        st.metric("Duration", duration)
    
    # Confidence visualization
    if session.primary_diagnosis and session.specialist_diagnosis and session.final_consensus:
        
        st.subheader("📈 Confidence Progression")
        
        confidence_data = {
            'Agent': ['Primary Care', 'Specialist', 'Final Consensus'],
            'Confidence': [
                session.primary_diagnosis.confidence,
                session.specialist_diagnosis.confidence, 
                session.final_consensus.confidence
            ],
            'Diagnosis': [
                session.primary_diagnosis.condition,
                session.specialist_diagnosis.condition,
                session.final_consensus.condition
            ]
        }
        
        fig = px.bar(
            confidence_data, 
            x='Agent', 
            y='Confidence',
            title='Diagnostic Confidence by Agent',
            color='Confidence',
            color_continuous_scale='RdYlGn',
            range_color=[0, 100]
        )
        
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Final diagnosis details
    if session.final_consensus:
        st.subheader("🎯 Final Consensus Diagnosis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Condition:** {session.final_consensus.condition}")
            st.write(f"**ICD-10 Code:** {session.final_consensus.icd10_code}")
            st.write(f"**Confidence:** {session.final_consensus.confidence}%")
        
        with col2:
            st.write("**Recommended Tests:**")
            for test in session.final_consensus.recommended_tests:
                st.write(f"- {test}")
    
    # Diagnostic comparison table
    st.subheader("🔍 Diagnostic Comparison")
    
    comparison_data = []
    
    if session.primary_diagnosis:
        comparison_data.append({
            'Agent': 'Primary Care',
            'Diagnosis': session.primary_diagnosis.condition,
            'Confidence': f"{session.primary_diagnosis.confidence}%",
            'ICD-10': session.primary_diagnosis.icd10_code or 'N/A'
        })
    
    if session.specialist_diagnosis:
        comparison_data.append({
            'Agent': 'Specialist',
            'Diagnosis': session.specialist_diagnosis.condition,
            'Confidence': f"{session.specialist_diagnosis.confidence}%",
            'ICD-10': session.specialist_diagnosis.icd10_code or 'N/A'
        })
    
    if session.final_consensus:
        comparison_data.append({
            'Agent': 'Final Consensus',
            'Diagnosis': session.final_consensus.condition,
            'Confidence': f"{session.final_consensus.confidence}%",
            'ICD-10': session.final_consensus.icd10_code or 'N/A'
        })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
    
    # Download report options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate Full PDF Report", type="secondary"):
            try:
                from pdf_generator import pdf_generator
                
                # Generate comprehensive PDF report
                with st.spinner("Generating comprehensive PDF report..."):
                    pdf_path = pdf_generator.generate_report(session)
                
                # Provide download link
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="💾 Download Full Report",
                        data=pdf_file.read(),
                        file_name=f"medical_report_{session.session_id}.pdf",
                        mime="application/pdf"
                    )
                
                st.success(f"Full PDF report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.info("Make sure reportlab is installed: pip install reportlab")
    
    with col2:
        if st.button("📄 Generate Summary Report", type="secondary"):
            try:
                from pdf_generator import pdf_generator
                
                # Generate summary PDF report
                with st.spinner("Generating summary PDF report..."):
                    pdf_path = pdf_generator.generate_summary_report(session)
                
                # Provide download link
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="💾 Download Summary",
                        data=pdf_file.read(),
                        file_name=f"medical_summary_{session.session_id}.pdf",
                        mime="application/pdf"
                    )
                
                st.success(f"Summary PDF report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.info("Make sure reportlab is installed: pip install reportlab")
    
    with col3:
        if st.button("🗺️ Simulate Discussion", type="secondary"):
            try:
                # Debug information
                st.info(f"🔍 Starting discussion simulation for session: {session.session_id}")
                
                # Get current orchestrator instance
                orchestrator = st.session_state.orchestrator
                
                # Validate session requirements
                if not session:
                    st.error("❌ No session available for discussion simulation")
                    st.stop()
                
                if session.status != "completed":
                    st.error(f"❌ Session must be completed to simulate discussion. Current status: {session.status}")
                    st.stop()
                
                if not (session.primary_diagnosis and session.specialist_diagnosis and session.final_consensus):
                    st.error("❌ Session must have all three diagnoses (primary, specialist, consensus) to simulate discussion")
                    st.stop()
                
                # Ensure session is in orchestrator's active sessions
                if session.session_id not in orchestrator.active_sessions:
                    st.info(f"📝 Adding session to orchestrator for discussion simulation...")
                    orchestrator.active_sessions[session.session_id] = session
                
                # Verify session is now accessible
                test_session = orchestrator.get_session(session.session_id)
                if not test_session:
                    st.error(f"❌ Failed to register session in orchestrator")
                    st.stop()
                
                st.info(f"✅ Session verified in orchestrator. Proceeding with simulation...")
                
                # Store conversation count before
                conversation_count_before = len(session.conversations)
                
                # Simulate additional discussion rounds
                with st.spinner("🗣️ Simulating clinical discussion between doctors..."):
                    import asyncio
                    
                    # Create a new event loop if needed (Streamlit compatibility)
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Run the simulation
                    updated_session = loop.run_until_complete(
                        orchestrator.simulate_case_discussion(session.session_id, discussion_rounds=2)
                    )
                
                # Verify new conversations were added
                conversation_count_after = len(updated_session.conversations)
                new_conversations = conversation_count_after - conversation_count_before
                
                # Update session state
                st.session_state.current_session = updated_session
                
                # Success messages
                st.success(f"🎉 Clinical discussion simulation completed!")
                st.info(f"📊 Added {new_conversations} new conversation messages")
                st.info("📜 Scroll up to see the additional conversation rounds between doctors")
                
                # Show a preview of new conversations
                if updated_session.conversations:
                    with st.expander("👁️ Preview of New Discussions"):
                        # Show last few conversations
                        recent_conversations = updated_session.conversations[-min(3, new_conversations):]
                        for conv in recent_conversations:
                            st.write(f"**{conv.agent_role}**: {conv.content[:150]}...")
                
                # Auto-refresh to show new content
                st.rerun()
                
            except ValueError as ve:
                st.error(f"❌ Validation Error: {str(ve)}")
                st.error("This usually means the session is not in the correct state for discussion simulation.")
                
            except asyncio.TimeoutError:
                st.error("⏰ Discussion simulation timed out. Please try again.")
                
            except ImportError as ie:
                st.error(f"❌ Import Error: {str(ie)}")
                st.error("Please ensure all required modules are properly installed.")
                
            except Exception as e:
                st.error(f"❌ Unexpected error during discussion simulation: {str(e)}")
                
                # Debug information
                with st.expander("🔧 Debug Information"):
                    st.write(f"**Session ID:** {session.session_id if session else 'None'}")
                    st.write(f"**Session Status:** {session.status if session else 'None'}")
                    st.write(f"**Orchestrator Available:** {'Yes' if 'orchestrator' in st.session_state else 'No'}")
                    if 'orchestrator' in st.session_state:
                        st.write(f"**Available Sessions:** {list(st.session_state.orchestrator.active_sessions.keys())}")
                    st.write(f"**Error Type:** {type(e).__name__}")
                    
                    # Full traceback for debugging
                    import traceback
                    st.code(traceback.format_exc())

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Agent Disease Diagnosis System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.agent-primary {
    background-color: #e3f2fd;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #2196f3;
}
.agent-specialist {
    background-color: #f3e5f5;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #9c27b0;
}
.agent-senior {
    background-color: #e8f5e8;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #4caf50;
}
.agent-system {
    background-color: #fff3e0;
    padding: 10px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 5px solid #ff9800;
}
.confidence-high {
    color: #4caf50;
    font-weight: bold;
}
.confidence-medium {
    color: #ff9800;
    font-weight: bold;
}
.confidence-low {
    color: #f44336;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = DiagnosticOrchestrator()
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# Main title and description
st.title("🏥 Multi-Agent Disease Diagnosis System")
st.markdown("""
**Welcome to the Multi-Agent Disease Diagnosis System**

This system demonstrates advanced AI-driven clinical reasoning through collaborative diagnosis. 
Watch as specialized medical AI agents work together to analyze patient cases:

- 🩺 **Primary Care Physician**: Initial assessment and common diagnosis focus
- 🔬 **Specialist Consultant**: Expert opinion and complex condition analysis  
- 👨‍⚕️ **Senior Attending**: Final review and consensus building

The system provides transparent insights into the diagnostic reasoning process, 
including confidence levels, differential diagnoses, and clinical decision-making.
""")

# Sidebar configuration
st.sidebar.header("🎛️ Control Panel")

# Display database statistics
db_stats = medical_db.get_database_stats()
with st.sidebar.expander("📊 Database Information"):
    st.write(f"**Total Conditions:** {db_stats['total_conditions']}")
    st.write(f"**Sample Cases:** {db_stats['sample_cases']}")
    st.write(f"**Common Conditions:** {db_stats['common_conditions']}")
    st.write(f"**Rare Conditions:** {db_stats['rare_conditions']}")
    
    st.write("**Categories:**")
    for category, count in db_stats['categories'].items():
        st.write(f"- {category}: {count}")

# Case selection
st.sidebar.subheader("📋 Case Selection")
case_selection_mode = st.sidebar.radio(
    "Select Mode:",
    ["Predefined Cases", "Generate Synthetic Case", "Custom Case Entry"]
)

selected_case = None

if case_selection_mode == "Predefined Cases":
    case_ids = [case['patient_id'] for case in medical_db.get_all_sample_cases()]
    selected_case_id = st.sidebar.selectbox("Select Sample Case:", options=["Select..."]+case_ids)
    
    if selected_case_id != "Select...":
        selected_case = medical_db.get_sample_case(selected_case_id)
        
        # Display case preview
        with st.sidebar.expander("👁️ Case Preview"):
            st.write(f"**Age:** {selected_case['age']}")
            st.write(f"**Sex:** {selected_case['sex']}")
            st.write(f"**Chief Complaint:** {selected_case['chief_complaint']}")
            st.write(f"**Expected Diagnosis:** {selected_case['expected_diagnosis']}")

elif case_selection_mode == "Generate Synthetic Case":
    condition_names = [c['name'] for c in medical_db.conditions]
    selected_condition = st.sidebar.selectbox("Select Condition:", options=["Select..."]+condition_names)
    
    if selected_condition != "Select...":
        if st.sidebar.button("🎲 Generate Synthetic Case"):
            generated_case = medical_db.generate_synthetic_case(selected_condition)
            st.session_state.synthetic_case = generated_case
            st.sidebar.success(f"Generated case for {selected_condition}")
        
        # Check if we have a generated case in session state
        if 'synthetic_case' in st.session_state:
            selected_case = st.session_state.synthetic_case
            
            # Display generated case preview
            with st.sidebar.expander("👁️ Generated Case Preview"):
                st.write(f"**Patient ID:** {selected_case['patient_id']}")
                st.write(f"**Age:** {selected_case['age']}")
                st.write(f"**Sex:** {selected_case['sex']}")
                st.write(f"**Chief Complaint:** {selected_case['chief_complaint']}")
                st.write(f"**Symptoms:** {', '.join(selected_case['symptoms'])}")

elif case_selection_mode == "Custom Case Entry":
    st.sidebar.write("Enter custom patient information:")
    custom_age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=45)
    custom_sex = st.sidebar.selectbox("Sex", ["Male", "Female", "Other"])
    custom_complaint = st.sidebar.text_area("Chief Complaint")
    custom_symptoms = st.sidebar.text_area("Symptoms (comma-separated)")
    custom_history = st.sidebar.text_area("Past Medical History (optional)")
    
    if st.sidebar.button("✅ Create Custom Case"):
        if custom_complaint and custom_symptoms:
            custom_case = {
                "patient_id": f"CUSTOM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "age": custom_age,
                "sex": custom_sex,
                "chief_complaint": custom_complaint,
                "symptoms": [s.strip() for s in custom_symptoms.split(',')],
                "duration": "Variable",
                "severity": "To be assessed",
                "past_medical_history": custom_history if custom_history else "Not specified",
                "medications": "Not specified",
                "allergies": "Not specified",
                "family_history": "Not specified",
                "social_history": "Not specified",
                "vital_signs": "To be obtained",
                "physical_exam": "To be performed"
            }
            st.session_state.custom_case = custom_case
            st.sidebar.success("Custom case created!")
        else:
            st.sidebar.error("Please fill in chief complaint and symptoms")
    
    # Check if we have a custom case in session state
    if 'custom_case' in st.session_state:
        selected_case = st.session_state.custom_case
        
        # Display custom case preview
        with st.sidebar.expander("👁️ Custom Case Preview"):
            st.write(f"**Patient ID:** {selected_case['patient_id']}")
            st.write(f"**Age:** {selected_case['age']}")
            st.write(f"**Sex:** {selected_case['sex']}")
            st.write(f"**Chief Complaint:** {selected_case['chief_complaint']}")
            st.write(f"**Symptoms:** {', '.join(selected_case['symptoms'])}")

# Specialist selection
specialty_options = [
    "Internal Medicine", "Cardiology", "Neurology", "Gastroenterology",
    "Pulmonology", "Endocrinology", "Infectious Disease", "Rheumatology"
]
selected_specialty = st.sidebar.selectbox("Select Specialist Type:", specialty_options)

# Demo mode toggle
st.session_state.demo_mode = st.sidebar.checkbox(
    "🎬 Demo Mode (Simulated API responses)", 
    value=st.session_state.demo_mode,
    help="Enable demo mode to simulate diagnostic process without OpenAI API calls"
)

# Main action button
start_diagnosis = st.sidebar.button(
    "🚀 Start Diagnostic Session",
    type="primary",
    help="Begin the multi-agent diagnostic process"
)

# Check for valid case selection
has_valid_case = (
    (case_selection_mode == "Predefined Cases" and selected_case is not None) or
    (case_selection_mode == "Generate Synthetic Case" and 'synthetic_case' in st.session_state) or
    (case_selection_mode == "Custom Case Entry" and 'custom_case' in st.session_state)
)

# Set selected_case if not already set
if case_selection_mode == "Generate Synthetic Case" and 'synthetic_case' in st.session_state:
    selected_case = st.session_state.synthetic_case
elif case_selection_mode == "Custom Case Entry" and 'custom_case' in st.session_state:
    selected_case = st.session_state.custom_case

# Main content area
if has_valid_case and start_diagnosis:
    
    # Store case in session state
    st.session_state.current_case = selected_case
    
    # Display patient information
    st.header("📋 Patient Case Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Demographics")
        st.write(f"**Patient ID:** {selected_case['patient_id']}")
        st.write(f"**Age:** {selected_case['age']}")
        st.write(f"**Sex:** {selected_case['sex']}")
    
    with col2:
        st.subheader("Presentation")
        st.write(f"**Chief Complaint:** {selected_case['chief_complaint']}")
        st.write(f"**Symptoms:** {', '.join(selected_case.get('symptoms', []))}")
        st.write(f"**Duration:** {selected_case.get('duration', 'Not specified')}")
    
    with col3:
        st.subheader("History")
        st.write(f"**Past Medical History:** {selected_case.get('past_medical_history', 'Not specified')}")
        st.write(f"**Medications:** {selected_case.get('medications', 'Not specified')}")
        st.write(f"**Allergies:** {selected_case.get('allergies', 'Not specified')}")
    
    # Start diagnostic process
    st.header("🧠 Diagnostic Reasoning Process")
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Container for real-time conversation
    conversation_container = st.container()
    
    try:
        if st.session_state.demo_mode:
            # Demo mode - simulate the process
            session = simulate_diagnostic_process(selected_case, selected_specialty, 
                                                progress_bar, status_text, conversation_container)
        else:
            # Real mode - use OpenAI API
            session = run_real_diagnostic_process(selected_case, selected_specialty,
                                                progress_bar, status_text, conversation_container)
        
        # Store completed session in session state and orchestrator
        st.session_state.current_session = session
        
        # Store session in orchestrator for discussion simulation
        if session.session_id not in st.session_state.orchestrator.active_sessions:
            st.session_state.orchestrator.active_sessions[session.session_id] = session
        
        # Display final results
        display_diagnostic_results(session)
        
    except Exception as e:
        st.error(f"An error occurred during diagnosis: {str(e)}")
        st.write("Please check your OpenAI API key and try again.")

elif not has_valid_case and start_diagnosis:
    if case_selection_mode == "Predefined Cases":
        st.warning("Please select a predefined case before starting the diagnostic session.")
    elif case_selection_mode == "Generate Synthetic Case":
        st.warning("Please generate a synthetic case before starting the diagnostic session.")
    elif case_selection_mode == "Custom Case Entry":
        st.warning("Please create a custom case before starting the diagnostic session.")

# Display previous session if available
if st.session_state.current_session and not start_diagnosis:
    st.header("📊 Previous Diagnostic Session Results")
    display_diagnostic_results(st.session_state.current_session)

# Footer
st.markdown("---")
st.markdown("""
**Multi-Agent Disease Diagnosis System** | Developed for clinical education and AI research

⚠️ **Important:** This system is for educational and research purposes only. 
All diagnoses should be validated by qualified medical professionals.
""")

