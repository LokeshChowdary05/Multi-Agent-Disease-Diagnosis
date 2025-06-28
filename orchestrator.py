# orchestrator.py
# This module orchestrates the multi-agent diagnostic process.
# It manages the flow between agents and tracks the conversation.

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from agents import PrimaryDiagnostician, SpecialistConsultant, SeniorReviewer, DiagnosisResult, ConversationMessage
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiagnosticSession(BaseModel):
    """Tracks a complete diagnostic session"""
    session_id: str
    patient_data: Dict[str, Any]
    conversations: List[ConversationMessage] = []
    primary_diagnosis: Optional[DiagnosisResult] = None
    specialist_diagnosis: Optional[DiagnosisResult] = None
    final_consensus: Optional[DiagnosisResult] = None
    status: str = "initialized"  # initialized, in_progress, completed, error
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None

class DiagnosticOrchestrator:
    """
    Orchestrates the multi-agent diagnostic process.
    Manages agent interactions, conversation flow, and consensus building.
    """
    
    def __init__(self):
        self.primary_agent = PrimaryDiagnostician()
        self.specialist_agent = SpecialistConsultant("Internal Medicine")
        self.senior_reviewer = SeniorReviewer()
        self.active_sessions: Dict[str, DiagnosticSession] = {}
        
    async def start_diagnostic_session(self, 
                                     patient_data: Dict[str, Any], 
                                     session_id: str = None,
                                     specialist_type: str = "Internal Medicine") -> str:
        """
        Start a new diagnostic session
        
        Args:
            patient_data: Patient symptoms and medical history
            session_id: Optional session identifier
            specialist_type: Type of specialist to consult
            
        Returns:
            str: Session ID for tracking
        """
        
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create specialist with requested specialty
        self.specialist_agent = SpecialistConsultant(specialist_type)
        
        # Initialize session
        session = DiagnosticSession(
            session_id=session_id,
            patient_data=patient_data,
            status="initialized"
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Started diagnostic session {session_id}")
        return session_id
    
    async def run_diagnostic_process(self, session_id: str) -> DiagnosticSession:
        """
        Run the complete diagnostic process for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            DiagnosticSession: Completed session with all diagnoses
        """
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session.status = "in_progress"
        
        try:
            # Step 1: Primary care assessment
            await self._add_conversation_message(
                session, 
                "System", 
                "System", 
                "🏥 Starting diagnostic consultation...", 
                "system"
            )
            
            primary_result = await self._run_primary_assessment(session)
            session.primary_diagnosis = primary_result
            
            # Step 2: Specialist consultation
            specialist_result = await self._run_specialist_consultation(session)
            session.specialist_diagnosis = specialist_result
            
            # Step 3: Senior review and consensus
            final_result = await self._run_senior_review(session)
            session.final_consensus = final_result
            
            # Mark session as completed
            session.status = "completed"
            session.completed_at = datetime.now()
            
            await self._add_conversation_message(
                session,
                "System",
                "System", 
                "✅ Diagnostic consultation completed successfully!",
                "system"
            )
            
            logger.info(f"Completed diagnostic session {session_id}")
            return session
            
        except Exception as e:
            session.status = "error"
            logger.error(f"Error in diagnostic session {session_id}: {str(e)}")
            
            await self._add_conversation_message(
                session,
                "System",
                "System",
                f"❌ Error in diagnostic process: {str(e)}",
                "system"
            )
            
            raise e
    
    async def _run_primary_assessment(self, session: DiagnosticSession) -> DiagnosisResult:
        """Run primary care physician assessment"""
        
        await self._add_conversation_message(
            session,
            self.primary_agent.name,
            self.primary_agent.role,
            "🔍 Analyzing patient presentation and symptoms...",
            "analysis"
        )
        
        # Get primary diagnosis
        result = await self.primary_agent.analyze_case(session.patient_data)
        
        # Add detailed conversation message
        analysis_message = f"""
**Primary Assessment Complete**

**Suspected Diagnosis:** {result.condition}
**Confidence Level:** {result.confidence}%

**Clinical Reasoning:**
{result.reasoning}

**Differential Diagnoses:**
{', '.join(result.differential_diagnoses) if result.differential_diagnoses else 'None specified'}

**Recommended Tests:**
{', '.join(result.recommended_tests) if result.recommended_tests else 'None specified'}

**Red Flags Identified:**
{', '.join(result.red_flags) if result.red_flags else 'None identified'}
        """
        
        await self._add_conversation_message(
            session,
            self.primary_agent.name,
            self.primary_agent.role,
            analysis_message,
            "analysis",
            result.confidence
        )
        
        return result
    
    async def _run_specialist_consultation(self, session: DiagnosticSession) -> DiagnosisResult:
        """Run specialist consultation"""
        
        await self._add_conversation_message(
            session,
            self.specialist_agent.name,
            self.specialist_agent.role,
            f"🔬 Providing {self.specialist_agent.specialty} specialist opinion...",
            "analysis"
        )
        
        # Create context from primary assessment
        primary_context = f"""
The primary care physician has assessed this case and provided the following:

Diagnosis: {session.primary_diagnosis.condition} (Confidence: {session.primary_diagnosis.confidence}%)
Reasoning: {session.primary_diagnosis.reasoning}
Differential Diagnoses: {', '.join(session.primary_diagnosis.differential_diagnoses)}
Recommended Tests: {', '.join(session.primary_diagnosis.recommended_tests)}
Red Flags: {', '.join(session.primary_diagnosis.red_flags)}

Please provide your specialist perspective on this case.
        """
        
        # Get specialist diagnosis
        result = await self.specialist_agent.analyze_case(session.patient_data, primary_context)
        
        # Add detailed conversation message
        analysis_message = f"""
**Specialist Consultation Complete**

**Specialist Diagnosis:** {result.condition}
**Confidence Level:** {result.confidence}%

**Specialist Reasoning:**
{result.reasoning}

**Additional Differential Diagnoses:**
{', '.join(result.differential_diagnoses) if result.differential_diagnoses else 'None specified'}

**Specialized Testing Recommendations:**
{', '.join(result.recommended_tests) if result.recommended_tests else 'None specified'}

**Clinical Concerns:**
{', '.join(result.red_flags) if result.red_flags else 'None identified'}
        """
        
        await self._add_conversation_message(
            session,
            self.specialist_agent.name,
            self.specialist_agent.role,
            analysis_message,
            "analysis",
            result.confidence
        )
        
        return result
    
    async def _run_senior_review(self, session: DiagnosticSession) -> DiagnosisResult:
        """Run senior physician review and consensus"""
        
        await self._add_conversation_message(
            session,
            self.senior_reviewer.name,
            self.senior_reviewer.role,
            "👨‍⚕️ Reviewing assessments and synthesizing consensus...",
            "consensus"
        )
        
        # Get consensus diagnosis
        result = await self.senior_reviewer.synthesize_consensus(
            session.patient_data,
            session.primary_diagnosis,
            session.specialist_diagnosis
        )
        
        # Add detailed conversation message
        consensus_message = f"""
**Senior Review and Final Consensus**

**Final Diagnosis:** {result.condition}
**Overall Confidence:** {result.confidence}%

**Synthesis and Clinical Decision:**
{result.reasoning}

**Comprehensive Differential Diagnosis:**
{', '.join(result.differential_diagnoses) if result.differential_diagnoses else 'None specified'}

**Final Testing Recommendations:**
{', '.join(result.recommended_tests) if result.recommended_tests else 'None specified'}

**Critical Safety Considerations:**
{', '.join(result.red_flags) if result.red_flags else 'None identified'}

**ICD-10 Code:** {result.icd10_code if result.icd10_code else 'Not specified'}
        """
        
        await self._add_conversation_message(
            session,
            self.senior_reviewer.name,
            self.senior_reviewer.role,
            consensus_message,
            "consensus",
            result.confidence
        )
        
        return result
    
    async def _add_conversation_message(self, 
                                     session: DiagnosticSession,
                                     agent_name: str,
                                     agent_role: str,
                                     content: str,
                                     message_type: str,
                                     confidence: Optional[float] = None):
        """Add a message to the conversation history"""
        
        message = ConversationMessage(
            agent_name=agent_name,
            agent_role=agent_role,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type,
            confidence=confidence
        )
        
        session.conversations.append(message)
        logger.info(f"Added conversation message from {agent_name}: {message_type}")
    
    def get_session(self, session_id: str) -> Optional[DiagnosticSession]:
        """Get session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> List[DiagnosticSession]:
        """Get all active sessions"""
        return list(self.active_sessions.values())
    
    async def generate_diagnostic_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive diagnostic summary
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict containing diagnostic summary
        """
        
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        summary = {
            "session_id": session_id,
            "patient_info": {
                "age": session.patient_data.get("age", "Not specified"),
                "sex": session.patient_data.get("sex", "Not specified"),
                "chief_complaint": session.patient_data.get("chief_complaint", "Not specified")
            },
            "diagnostic_timeline": [
                {
                    "agent": msg.agent_name,
                    "role": msg.agent_role,
                    "timestamp": msg.timestamp,
                    "type": msg.message_type,
                    "confidence": msg.confidence
                } for msg in session.conversations
            ],
            "diagnoses": {
                "primary_care": {
                    "condition": session.primary_diagnosis.condition if session.primary_diagnosis else None,
                    "confidence": session.primary_diagnosis.confidence if session.primary_diagnosis else None
                },
                "specialist": {
                    "condition": session.specialist_diagnosis.condition if session.specialist_diagnosis else None,
                    "confidence": session.specialist_diagnosis.confidence if session.specialist_diagnosis else None
                },
                "final_consensus": {
                    "condition": session.final_consensus.condition if session.final_consensus else None,
                    "confidence": session.final_consensus.confidence if session.final_consensus else None,
                    "icd10_code": session.final_consensus.icd10_code if session.final_consensus else None
                }
            },
            "status": session.status,
            "duration": (session.completed_at - session.created_at).total_seconds() if session.completed_at else None
        }
        
        return summary
    
    async def simulate_case_discussion(self, session_id: str, discussion_rounds: int = 2) -> DiagnosticSession:
        """
        Simulate additional discussion rounds between agents
        
        Args:
            session_id: Session identifier
            discussion_rounds: Number of additional discussion rounds
            
        Returns:
            Updated session with additional discussions
        """
        
        session = self.get_session(session_id)
        if not session or session.status != "completed":
            raise ValueError(f"Invalid session {session_id} for discussion simulation")
        
        await self._add_conversation_message(
            session,
            "System",
            "System",
            f"🗣️ Initiating {discussion_rounds} rounds of case discussion...",
            "system"
        )
        
        for round_num in range(1, discussion_rounds + 1):
            await self._add_conversation_message(
                session,
                "Moderator",
                "Clinical Moderator",
                f"**Discussion Round {round_num}**\n\nLet's review the case and discuss any concerns or alternative perspectives...",
                "discussion"
            )
            
            # Simulate questions and responses
            await self._simulate_agent_discussion(session, round_num)
        
        return session
    
    async def _simulate_agent_discussion(self, session: DiagnosticSession, round_num: int):
        """Simulate detailed clinical discussion between agents"""
        
        # Get case details for context
        patient_data = session.patient_data
        primary_dx = session.primary_diagnosis
        specialist_dx = session.specialist_diagnosis
        
        # Primary agent initiates discussion with specific clinical concerns
        primary_questions = [
            f"Dr. {self.specialist_agent.specialty.replace(' ', '')}, I'm concerned about the differential diagnosis. Given the patient's {patient_data.get('chief_complaint', 'presentation')}, should we consider {', '.join(primary_dx.differential_diagnoses[:2]) if primary_dx.differential_diagnoses else 'alternative diagnoses'}?",
            f"The patient's {', '.join(patient_data.get('symptoms', [])[:2])} could also suggest other conditions. What's your take on the urgency of further testing?",
            f"I notice the confidence levels differ between our assessments. Can you help me understand the key differentiating factors you're considering?"
        ]
        
        primary_question = primary_questions[min(round_num - 1, len(primary_questions) - 1)]
        await self._add_conversation_message(
            session,
            self.primary_agent.name,
            self.primary_agent.role,
            primary_question,
            "question"
        )
        
        # Specialist provides detailed clinical reasoning
        specialist_responses = [
            f"Good point, Dr. Primary. In my {self.specialist_agent.specialty} practice, the constellation of symptoms - particularly {', '.join(patient_data.get('symptoms', [])[:2])} - is most consistent with {specialist_dx.condition}. The {', '.join(specialist_dx.red_flags[:1]) if specialist_dx.red_flags else 'clinical presentation'} supports this diagnosis. However, I agree we should monitor for {', '.join(specialist_dx.differential_diagnoses[:1]) if specialist_dx.differential_diagnoses else 'other possibilities'}.",
            f"From a {self.specialist_agent.specialty.lower()} perspective, the {', '.join(specialist_dx.recommended_tests[:2]) if specialist_dx.recommended_tests else 'diagnostic workup'} will be crucial. The patient's age ({patient_data.get('age', 'unknown')}) and clinical presentation suggest we need to be thorough but also consider the most likely diagnosis.",
            f"The key differentiating factors I'm considering are: 1) The temporal pattern of symptoms, 2) The patient's risk factors including {patient_data.get('past_medical_history', 'medical history')}, and 3) The physical examination findings. This supports my confidence level of {specialist_dx.confidence}%."
        ]
        
        specialist_response = specialist_responses[min(round_num - 1, len(specialist_responses) - 1)]
        await self._add_conversation_message(
            session,
            self.specialist_agent.name,
            self.specialist_agent.role,
            specialist_response,
            "response"
        )
        
        # Senior reviewer synthesizes and provides teaching points
        senior_guidance_options = [
            f"Excellent discussion, colleagues. This case illustrates the importance of collaborative decision-making. Dr. Primary's concern about differential diagnosis is well-founded - we must always consider 'cannot miss' diagnoses. Dr. {self.specialist_agent.specialty.replace(' ', '')}'s expertise in {specialist_dx.condition} is valuable. I recommend we proceed with {', '.join(specialist_dx.recommended_tests[:1]) if specialist_dx.recommended_tests else 'the proposed workup'} while monitoring for {', '.join(primary_dx.red_flags[:1]) if primary_dx.red_flags else 'red flags'}.",
            f"This case demonstrates good clinical reasoning from both perspectives. The patient's presentation of {patient_data.get('chief_complaint', 'symptoms')} requires us to balance common diagnoses with serious conditions. Given the {patient_data.get('severity', 'clinical')} nature and {patient_data.get('duration', 'timeline')}, I support the {self.specialist_agent.specialty.lower()} assessment while keeping primary care concerns in mind.",
            f"From a patient safety standpoint, both assessments show appropriate clinical vigilance. The convergence on {specialist_dx.condition} with high confidence is reassuring. Key teaching points: 1) Always consider the clinical context, 2) Use evidence-based guidelines, 3) Maintain appropriate index of suspicion for serious conditions. The multidisciplinary approach here exemplifies best practice."
        ]
        
        senior_guidance = senior_guidance_options[min(round_num - 1, len(senior_guidance_options) - 1)]
        await self._add_conversation_message(
            session,
            self.senior_reviewer.name,
            self.senior_reviewer.role,
            senior_guidance,
            "consensus"
        )
        
        # Add follow-up questions and clarifications
        if round_num == 1:
            # Primary asks for clarification
            followup_question = f"Thank you for that insight. Should we consider any additional risk stratification given the patient's {patient_data.get('family_history', 'family history')} and {patient_data.get('social_history', 'social factors')}?"
            await self._add_conversation_message(
                session,
                self.primary_agent.name,
                self.primary_agent.role,
                followup_question,
                "question"
            )
            
            # Specialist responds with risk assessment
            risk_response = f"Absolutely. The family history and social factors are important. In this case, the {patient_data.get('past_medical_history', 'medical background')} increases the likelihood of {specialist_dx.condition}. We should also consider patient education about {', '.join(specialist_dx.red_flags[:1]) if specialist_dx.red_flags else 'warning signs'} and ensure appropriate follow-up."
            await self._add_conversation_message(
                session,
                self.specialist_agent.name,
                self.specialist_agent.role,
                risk_response,
                "response"
            )
