# agents.py
# This module contains the AI agents responsible for medical diagnosis.
# Each agent has specialized roles and clinical reasoning capabilities.

import openai
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiagnosisResult(BaseModel):
    """Structured diagnosis result with confidence scoring"""
    condition: str
    confidence: float
    reasoning: str
    icd10_code: Optional[str] = None
    recommended_tests: List[str] = []
    differential_diagnoses: List[str] = []
    red_flags: List[str] = []

class ConversationMessage(BaseModel):
    """Message structure for agent conversations"""
    agent_name: str
    agent_role: str
    content: str
    timestamp: datetime
    message_type: str  # 'analysis', 'question', 'response', 'consensus'
    confidence: Optional[float] = None

class BaseAgent:
    """
    Base class for all medical diagnostic agents.
    Implements core OpenAI API interaction and safety guardrails.
    """
    
    def __init__(self, name: str, role: str, specialty: str = None):
        self.name = name
        self.role = role
        self.specialty = specialty
        self.conversation_history = []
        self.safety_prompts = self._load_safety_guardrails()
        
    def _load_safety_guardrails(self) -> List[str]:
        """Load clinical safety prompts to prevent hallucination"""
        return [
            "Always acknowledge uncertainty when evidence is insufficient.",
            "Prioritize patient safety over diagnostic certainty.",
            "Flag any life-threatening conditions immediately.",
            "Base diagnoses only on provided symptoms and clinical evidence.",
            "Recommend appropriate diagnostic tests when needed.",
            "Consider differential diagnoses systematically."
        ]
    
    def _create_system_prompt(self) -> str:
        """Create role-specific system prompt with medical constraints"""
        base_prompt = f"""
You are {self.name}, a {self.role} with expertise in {self.specialty or 'general medicine'}.

Clinical Guidelines:
{chr(10).join(f'- {guideline}' for guideline in self.safety_prompts)}

Your responses must:
1. Follow evidence-based medicine principles
2. Use structured clinical reasoning (SOAP format when applicable)
3. Provide confidence scores (0-100%) for diagnoses
4. Include ICD-10 codes when confident in diagnosis
5. Recommend appropriate next steps or consultations

Always format your response as valid JSON with the following structure:
{{
    "primary_diagnosis": "condition name",
    "confidence": confidence_percentage,
    "reasoning": "detailed clinical reasoning",
    "differential_diagnoses": ["alternative1", "alternative2"],
    "recommended_tests": ["test1", "test2"],
    "red_flags": ["concern1", "concern2"],
    "icd10_code": "code if confident",
    "next_steps": "recommendations"
}}
        """
        return base_prompt
    
    async def analyze_case(self, patient_data: Dict[str, Any], context: str = "") -> DiagnosisResult:
        """
        Analyze patient case using OpenAI API with clinical reasoning
        
        Args:
            patient_data: Dictionary containing patient symptoms and history
            context: Additional context from other agents
            
        Returns:
            DiagnosisResult: Structured diagnosis with reasoning
        """
        try:
            prompt = self._create_clinical_prompt(patient_data, context)
            
            # For newer OpenAI library versions
            import openai
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self._create_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for medical accuracy
                max_tokens=1500
            )
            
            # Parse response and validate
            result = self._parse_diagnosis_response(response.choices[0].message.content)
            
            # Log interaction
            self._log_interaction(patient_data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name} analysis: {str(e)}")
            return self._create_error_response(str(e))
    
    def _create_clinical_prompt(self, patient_data: Dict[str, Any], context: str) -> str:
        """Create structured clinical prompt from patient data"""
        prompt = f"""
Patient Case Analysis Required:

CHIEF COMPLAINT: {patient_data.get('chief_complaint', 'Not specified')}

PRESENT ILLNESS:
- Age: {patient_data.get('age', 'Not specified')}
- Sex: {patient_data.get('sex', 'Not specified')}
- Symptoms: {', '.join(patient_data.get('symptoms', []))}
- Duration: {patient_data.get('duration', 'Not specified')}
- Severity: {patient_data.get('severity', 'Not specified')}

PAST MEDICAL HISTORY: {patient_data.get('past_medical_history', 'Not specified')}
MEDICATIONS: {patient_data.get('medications', 'None listed')}
ALLERGIES: {patient_data.get('allergies', 'NKDA')}
FAMILY HISTORY: {patient_data.get('family_history', 'Not specified')}
SOCIAL HISTORY: {patient_data.get('social_history', 'Not specified')}

VITAL SIGNS: {patient_data.get('vital_signs', 'Not provided')}
PHYSICAL EXAM: {patient_data.get('physical_exam', 'Not provided')}

ADDITIONAL CONTEXT FROM OTHER CLINICIANS:
{context if context else 'None provided'}

Please provide your clinical assessment following the JSON format specified in your instructions.
        """
        return prompt
    
    def _parse_diagnosis_response(self, response_text: str) -> DiagnosisResult:
        """Parse and validate OpenAI response into structured format"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
            else:
                # Fallback parsing if JSON format is not followed
                json_data = self._extract_diagnosis_from_text(response_text)
            
            return DiagnosisResult(
                condition=json_data.get('primary_diagnosis', 'Unable to determine'),
                confidence=float(json_data.get('confidence', 0)),
                reasoning=json_data.get('reasoning', 'No reasoning provided'),
                icd10_code=json_data.get('icd10_code'),
                recommended_tests=json_data.get('recommended_tests', []),
                differential_diagnoses=json_data.get('differential_diagnoses', []),
                red_flags=json_data.get('red_flags', [])
            )
            
        except Exception as e:
            logger.error(f"Error parsing diagnosis response: {str(e)}")
            return DiagnosisResult(
                condition="Parsing Error",
                confidence=0.0,
                reasoning=f"Error parsing response: {str(e)}"
            )
    
    def _extract_diagnosis_from_text(self, text: str) -> Dict[str, Any]:
        """Fallback method to extract diagnosis from unstructured text"""
        # Simple keyword-based extraction for fallback
        return {
            'primary_diagnosis': 'Unable to parse structured diagnosis',
            'confidence': 50,
            'reasoning': text[:500],  # First 500 chars as reasoning
            'differential_diagnoses': [],
            'recommended_tests': [],
            'red_flags': []
        }
    
    def _create_error_response(self, error_message: str) -> DiagnosisResult:
        """Create error response in case of API failure"""
        return DiagnosisResult(
            condition="System Error",
            confidence=0.0,
            reasoning=f"Unable to complete diagnosis due to error: {error_message}",
            red_flags=["System error - manual review required"]
        )
    
    def _log_interaction(self, patient_data: Dict[str, Any], result: DiagnosisResult):
        """Log diagnostic interaction for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'role': self.role,
            'patient_id': patient_data.get('patient_id', 'unknown'),
            'diagnosis': result.condition,
            'confidence': result.confidence
        }
        logger.info(f"Diagnostic interaction: {json.dumps(log_entry)}")

class PrimaryDiagnostician(BaseAgent):
    """
    Primary care physician agent for initial assessment.
    Focuses on common conditions and appropriate referrals.
    """
    
    def __init__(self):
        super().__init__(
            name="Dr. Primary",
            role="Primary Care Physician",
            specialty="Family Medicine"
        )
    
    def _create_system_prompt(self) -> str:
        base_prompt = super()._create_system_prompt()
        primary_care_addition = """

As a Primary Care Physician, your focus is on:
1. Common medical conditions and their presentations
2. Appropriate screening and preventive care
3. When to refer to specialists
4. Cost-effective diagnostic approaches
5. Patient education and counseling

Consider the most common diagnoses first (horses, not zebras) unless red flags suggest otherwise.
        """
        return base_prompt + primary_care_addition

class SpecialistConsultant(BaseAgent):
    """
    Specialist consultant agent for complex cases.
    Provides expert opinion in specific medical domains.
    """
    
    def __init__(self, specialty: str = "Internal Medicine"):
        super().__init__(
            name=f"Dr. {specialty.replace(' ', '')}",
            role="Specialist Consultant",
            specialty=specialty
        )
    
    def _create_system_prompt(self) -> str:
        base_prompt = super()._create_system_prompt()
        specialist_addition = f"""

As a {self.specialty} Specialist, your expertise includes:
1. Complex and rare conditions in your specialty
2. Advanced diagnostic procedures and interpretation
3. Specialized treatment protocols
4. Latest research and clinical guidelines in your field
5. Subspecialty referrals when needed

Consider both common and uncommon conditions within your specialty.
Provide detailed rationale for advanced testing or procedures.
        """
        return base_prompt + specialist_addition

class SeniorReviewer(BaseAgent):
    """
    Senior attending physician for case review and consensus.
    Synthesizes input from other agents and provides final assessment.
    """
    
    def __init__(self):
        super().__init__(
            name="Dr. Senior",
            role="Senior Attending Physician",
            specialty="Internal Medicine"
        )
    
    def _create_system_prompt(self) -> str:
        base_prompt = super()._create_system_prompt()
        reviewer_addition = """

As a Senior Attending Physician, your role is to:
1. Review and synthesize input from other physicians
2. Identify potential gaps in reasoning or missed diagnoses
3. Provide teaching points and clinical pearls
4. Ensure patient safety and quality of care
5. Make final diagnostic recommendations

Consider all perspectives presented and weigh the evidence carefully.
Provide clear reasoning for your final assessment.
Highlight any areas where additional information would be helpful.
        """
        return base_prompt + reviewer_addition
    
    async def synthesize_consensus(self, 
                                 patient_data: Dict[str, Any], 
                                 primary_diagnosis: DiagnosisResult,
                                 specialist_diagnosis: DiagnosisResult) -> DiagnosisResult:
        """
        Synthesize multiple diagnostic opinions into consensus
        
        Args:
            patient_data: Original patient data
            primary_diagnosis: Primary care assessment
            specialist_diagnosis: Specialist assessment
            
        Returns:
            DiagnosisResult: Synthesized consensus diagnosis
        """
        
        # Create context with other agents' assessments
        context = f"""
PRIMARY CARE ASSESSMENT:
Diagnosis: {primary_diagnosis.condition} (Confidence: {primary_diagnosis.confidence}%)
Reasoning: {primary_diagnosis.reasoning}
Differential: {', '.join(primary_diagnosis.differential_diagnoses)}
Recommended Tests: {', '.join(primary_diagnosis.recommended_tests)}
Red Flags: {', '.join(primary_diagnosis.red_flags)}

SPECIALIST ASSESSMENT:
Diagnosis: {specialist_diagnosis.condition} (Confidence: {specialist_diagnosis.confidence}%)
Reasoning: {specialist_diagnosis.reasoning}
Differential: {', '.join(specialist_diagnosis.differential_diagnoses)}
Recommended Tests: {', '.join(specialist_diagnosis.recommended_tests)}
Red Flags: {', '.join(specialist_diagnosis.red_flags)}

Please provide your synthesis and final diagnostic recommendation.
        """
        
        return await self.analyze_case(patient_data, context)
