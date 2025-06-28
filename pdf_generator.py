# pdf_generator.py
# This module generates comprehensive PDF reports for medical diagnoses.

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os
from typing import Dict, Any, List
from orchestrator import DiagnosticSession

class MedicalReportGenerator:
    """
    Generates comprehensive PDF reports for medical diagnostic sessions.
    Includes patient information, agent conversations, and final diagnosis.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the medical report"""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # Agent name style
        self.styles.add(ParagraphStyle(
            name='AgentName',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=5,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        ))
        
        # Diagnosis style
        self.styles.add(ParagraphStyle(
            name='DiagnosisStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=10,
            backColor=colors.lightblue,
            borderColor=colors.blue,
            borderWidth=1,
            borderPadding=10
        ))
        
        # Confidence style
        self.styles.add(ParagraphStyle(
            name='ConfidenceStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.darkred,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, session: DiagnosticSession, output_path: str = None) -> str:
        """
        Generate a comprehensive PDF report for a diagnostic session
        
        Args:
            session: Diagnostic session containing all data
            output_path: Optional path for the PDF file
            
        Returns:
            str: Path to the generated PDF file
        """
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"medical_report_{session.session_id}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        
        # Add header
        self._add_header(story, session)
        
        # Add patient information
        self._add_patient_information(story, session)
        
        # Add diagnostic summary
        self._add_diagnostic_summary(story, session)
        
        # Add detailed conversation
        self._add_conversation_log(story, session)
        
        # Add final recommendations
        self._add_recommendations(story, session)
        
        # Add footer
        self._add_footer(story, session)
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _add_header(self, story: List, session: DiagnosticSession):
        """Add report header"""
        
        # Main title
        title = Paragraph("MULTI-AGENT MEDICAL DIAGNOSIS REPORT", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        metadata_data = [
            ['Report Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
            ['Session ID:', session.session_id],
            ['Diagnostic Status:', session.status.upper()],
            ['Total Duration:', self._format_duration(session)]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metadata_table)
        story.append(Spacer(1, 30))
    
    def _add_patient_information(self, story: List, session: DiagnosticSession):
        """Add patient information section"""
        
        story.append(Paragraph("PATIENT INFORMATION", self.styles['CustomSubtitle']))
        
        patient_data = session.patient_data
        
        # Basic demographics
        demo_data = [
            ['Patient ID:', patient_data.get('patient_id', 'N/A')],
            ['Age:', str(patient_data.get('age', 'N/A'))],
            ['Sex:', patient_data.get('sex', 'N/A')],
            ['Chief Complaint:', patient_data.get('chief_complaint', 'N/A')]
        ]
        
        demo_table = Table(demo_data, colWidths=[2*inch, 4*inch])
        demo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(demo_table)
        story.append(Spacer(1, 20))
        
        # Clinical presentation
        presentation_data = [
            ['Symptoms:', ', '.join(patient_data.get('symptoms', []))],
            ['Duration:', patient_data.get('duration', 'N/A')],
            ['Severity:', patient_data.get('severity', 'N/A')],
            ['Vital Signs:', patient_data.get('vital_signs', 'N/A')]
        ]
        
        presentation_table = Table(presentation_data, colWidths=[2*inch, 4*inch])
        presentation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(presentation_table)
        story.append(Spacer(1, 20))
        
        # Medical history
        history_data = [
            ['Past Medical History:', patient_data.get('past_medical_history', 'N/A')],
            ['Current Medications:', patient_data.get('medications', 'N/A')],
            ['Allergies:', patient_data.get('allergies', 'N/A')],
            ['Family History:', patient_data.get('family_history', 'N/A')],
            ['Social History:', patient_data.get('social_history', 'N/A')]
        ]
        
        history_table = Table(history_data, colWidths=[2*inch, 4*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightyellow),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(history_table)
        story.append(Spacer(1, 30))
    
    def _add_diagnostic_summary(self, story: List, session: DiagnosticSession):
        """Add diagnostic summary section"""
        
        story.append(Paragraph("DIAGNOSTIC SUMMARY", self.styles['CustomSubtitle']))
        
        # Create summary table
        summary_data = [['Agent', 'Diagnosis', 'Confidence', 'ICD-10']]
        
        if session.primary_diagnosis:
            summary_data.append([
                'Primary Care',
                session.primary_diagnosis.condition,
                f"{session.primary_diagnosis.confidence}%",
                session.primary_diagnosis.icd10_code or 'N/A'
            ])
        
        if session.specialist_diagnosis:
            summary_data.append([
                'Specialist',
                session.specialist_diagnosis.condition,
                f"{session.specialist_diagnosis.confidence}%",
                session.specialist_diagnosis.icd10_code or 'N/A'
            ])
        
        if session.final_consensus:
            summary_data.append([
                'Final Consensus',
                session.final_consensus.condition,
                f"{session.final_consensus.confidence}%",
                session.final_consensus.icd10_code or 'N/A'
            ])
        
        summary_table = Table(summary_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen)  # Highlight final consensus
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Final diagnosis details
        if session.final_consensus:
            story.append(Paragraph("FINAL DIAGNOSIS DETAILS", self.styles['Heading3']))
            
            diagnosis_text = f"""
            <b>Primary Diagnosis:</b> {session.final_consensus.condition}<br/>
            <b>Confidence Level:</b> {session.final_consensus.confidence}%<br/>
            <b>ICD-10 Code:</b> {session.final_consensus.icd10_code or 'Not specified'}<br/><br/>
            
            <b>Clinical Reasoning:</b><br/>
            {session.final_consensus.reasoning}<br/><br/>
            
            <b>Recommended Tests:</b><br/>
            {', '.join(session.final_consensus.recommended_tests) if session.final_consensus.recommended_tests else 'None specified'}<br/><br/>
            
            <b>Differential Diagnoses:</b><br/>
            {', '.join(session.final_consensus.differential_diagnoses) if session.final_consensus.differential_diagnoses else 'None specified'}<br/><br/>
            
            <b>Red Flags/Critical Considerations:</b><br/>
            {', '.join(session.final_consensus.red_flags) if session.final_consensus.red_flags else 'None identified'}
            """
            
            story.append(Paragraph(diagnosis_text, self.styles['DiagnosisStyle']))
            story.append(Spacer(1, 30))
    
    def _add_conversation_log(self, story: List, session: DiagnosticSession):
        """Add detailed conversation log"""
        
        story.append(Paragraph("CLINICAL CONVERSATION LOG", self.styles['CustomSubtitle']))
        
        for i, message in enumerate(session.conversations):
            # Agent header
            agent_header = f"{message.agent_name} ({message.agent_role})"
            timestamp = message.timestamp.strftime("%H:%M:%S")
            header_text = f"<b>{agent_header}</b> - {timestamp}"
            
            if message.confidence:
                header_text += f" - Confidence: {message.confidence}%"
            
            story.append(Paragraph(header_text, self.styles['AgentName']))
            
            # Message content
            content = message.content.replace('\n', '<br/>')
            story.append(Paragraph(content, self.styles['Normal']))
            story.append(Spacer(1, 15))
            
            # Page break every 5 messages to avoid overcrowding
            if (i + 1) % 8 == 0 and i < len(session.conversations) - 1:
                story.append(PageBreak())
        
        story.append(Spacer(1, 30))
    
    def _add_recommendations(self, story: List, session: DiagnosticSession):
        """Add final recommendations section"""
        
        story.append(Paragraph("CLINICAL RECOMMENDATIONS", self.styles['CustomSubtitle']))
        
        if session.final_consensus:
            recommendations = []
            
            # Testing recommendations
            if session.final_consensus.recommended_tests:
                recommendations.append("Recommended Diagnostic Tests:")
                for test in session.final_consensus.recommended_tests:
                    recommendations.append(f"• {test}")
                recommendations.append("")
            
            # Follow-up care
            recommendations.extend([
                "Follow-up Care:",
                "• Regular monitoring as clinically indicated",
                "• Patient education regarding diagnosis and treatment",
                "• Return if symptoms worsen or new symptoms develop",
                ""
            ])
            
            # Safety considerations
            if session.final_consensus.red_flags:
                recommendations.append("Critical Safety Considerations:")
                for flag in session.final_consensus.red_flags:
                    recommendations.append(f"• Monitor for {flag}")
                recommendations.append("")
            
            # General recommendations
            recommendations.extend([
                "General Recommendations:",
                "• Ensure appropriate specialist follow-up if indicated",
                "• Review and optimize current medications",
                "• Lifestyle modifications as appropriate for condition",
                "• Emergency precautions and when to seek immediate care"
            ])
            
            for rec in recommendations:
                if rec.startswith("•"):
                    story.append(Paragraph(rec, self.styles['Normal']))
                elif rec == "":
                    story.append(Spacer(1, 10))
                else:
                    story.append(Paragraph(f"<b>{rec}</b>", self.styles['Heading4']))
    
    def _add_footer(self, story: List, session: DiagnosticSession):
        """Add report footer"""
        
        story.append(Spacer(1, 30))
        
        disclaimer_text = """
        <b>IMPORTANT DISCLAIMER:</b><br/><br/>
        
        This report was generated by an AI-powered multi-agent diagnostic system for educational 
        and research purposes only. This system is NOT intended for actual patient care decisions 
        and should NOT replace professional medical judgment.<br/><br/>
        
        <b>Key Points:</b><br/>
        • All diagnostic recommendations must be validated by qualified healthcare professionals<br/>
        • This system is designed for educational demonstration of multi-agent AI reasoning<br/>
        • Clinical decisions should always be based on complete patient evaluation by licensed physicians<br/>
        • No patient care decisions should be made solely based on this report<br/><br/>
        
        <b>For Research and Educational Use Only</b><br/>
        Multi-Agent Disease Diagnosis System v1.0<br/>
        Report Generated: {}<br/>
        Session ID: {}
        """.format(datetime.now().strftime("%B %d, %Y at %I:%M %p"), session.session_id)
        
        story.append(Paragraph(disclaimer_text, self.styles['Normal']))
    
    def _format_duration(self, session: DiagnosticSession) -> str:
        """Format session duration"""
        
        if session.completed_at and session.created_at:
            duration = session.completed_at - session.created_at
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}m {seconds}s"
        return "In Progress"
    
    def generate_summary_report(self, session: DiagnosticSession, output_path: str = None) -> str:
        """
        Generate a shorter summary report
        
        Args:
            session: Diagnostic session
            output_path: Optional output path
            
        Returns:
            str: Path to generated PDF
        """
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"medical_summary_{session.session_id}_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Add header
        self._add_header(story, session)
        
        # Add patient info
        self._add_patient_information(story, session)
        
        # Add diagnostic summary only
        self._add_diagnostic_summary(story, session)
        
        # Add recommendations
        self._add_recommendations(story, session)
        
        # Add footer
        self._add_footer(story, session)
        
        doc.build(story)
        
        return output_path

# Global instance for easy access
pdf_generator = MedicalReportGenerator()
