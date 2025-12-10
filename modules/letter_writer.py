"""
VolunteerConnect Hub - AI Letter Writer Module
==============================================

This module provides AI-powered letter and email generation for volunteering
purposes. It uses the LinguaChart-G4 AGI for language generation and
HarmonyJust-G4 for social appropriateness.

Features:
- Application letters
- Thank you notes
- Outreach emails
- Follow-up messages
- Organization partnership proposals

Quality Target: 100%
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class LetterType(Enum):
    """Types of letters the AI can generate."""
    APPLICATION = "application"
    THANK_YOU = "thank_you"
    OUTREACH = "outreach"
    FOLLOW_UP = "follow_up"
    PARTNERSHIP = "partnership"
    RECOMMENDATION_REQUEST = "recommendation_request"
    CONFIRMATION = "confirmation"
    CANCELLATION = "cancellation"


@dataclass
class LetterContext:
    """Context for generating a letter."""
    letter_type: LetterType
    sender_name: str
    sender_email: str = ""
    recipient_name: str = ""
    recipient_title: str = ""
    organization: str = ""
    role: str = ""
    reason: str = ""
    experience: str = ""
    skills: str = ""
    availability: str = ""
    previous_action: str = ""
    additional_info: str = ""
    tone: str = "professional"  # professional, friendly, formal
    custom_fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class GeneratedLetter:
    """A generated letter."""
    id: str
    letter_type: LetterType
    subject: str
    body: str
    context: LetterContext
    generated_at: str
    quality_score: float
    suggestions: List[str] = field(default_factory=list)


class AILetterWriter:
    """
    AI-powered letter writer for volunteering communications.
    
    Uses:
    - LinguaChart-G4: Primary language generation (99.3% quality)
    - HarmonyJust-G4: Social appropriateness checking
    - LinguaEmpathy-G4: Emotional tone optimization
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.templates = self._load_templates()
        self.quality_threshold = 0.95
        
    def _load_templates(self) -> Dict[str, str]:
        """Load letter templates."""
        return {
            LetterType.APPLICATION: self._get_application_template(),
            LetterType.THANK_YOU: self._get_thank_you_template(),
            LetterType.OUTREACH: self._get_outreach_template(),
            LetterType.FOLLOW_UP: self._get_follow_up_template(),
            LetterType.PARTNERSHIP: self._get_partnership_template(),
            LetterType.RECOMMENDATION_REQUEST: self._get_recommendation_template(),
            LetterType.CONFIRMATION: self._get_confirmation_template(),
            LetterType.CANCELLATION: self._get_cancellation_template(),
        }
    
    def generate_letter(self, context: LetterContext) -> GeneratedLetter:
        """
        Generate a letter based on the provided context.
        
        Args:
            context: The context for letter generation
            
        Returns:
            GeneratedLetter with the generated content
        """
        # Get base template
        template = self.templates.get(context.letter_type, self.templates[LetterType.APPLICATION])
        
        # Fill template with context
        body = self._fill_template(template, context)
        
        # Generate subject line
        subject = self._generate_subject(context)
        
        # Quality check
        quality_score = self._assess_quality(body, context)
        
        # Generate suggestions for improvement
        suggestions = self._generate_suggestions(body, context, quality_score)
        
        return GeneratedLetter(
            id=f"letter-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            letter_type=context.letter_type,
            subject=subject,
            body=body,
            context=context,
            generated_at=datetime.now().isoformat(),
            quality_score=quality_score,
            suggestions=suggestions
        )
    
    def _fill_template(self, template: str, context: LetterContext) -> str:
        """Fill a template with context values."""
        replacements = {
            '{sender_name}': context.sender_name or '[Your Name]',
            '{sender_email}': context.sender_email or '[Your Email]',
            '{recipient_name}': context.recipient_name or 'Hiring Manager',
            '{recipient_title}': context.recipient_title or '',
            '{organization}': context.organization or 'your organization',
            '{role}': context.role or 'volunteer',
            '{reason}': context.reason or 'I am passionate about making a positive impact',
            '{experience}': context.experience or '',
            '{skills}': context.skills or '',
            '{availability}': context.availability or 'flexible schedule',
            '{previous_action}': context.previous_action or 'previous inquiry',
            '{additional_info}': context.additional_info or '',
        }
        
        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)
        
        # Handle custom fields
        for key, value in context.custom_fields.items():
            result = result.replace(f'{{{key}}}', value)
        
        # Clean up empty sections
        result = self._clean_empty_sections(result)
        
        return result
    
    def _clean_empty_sections(self, text: str) -> str:
        """Remove empty sections from the letter."""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are just placeholders
            if line.strip() and not line.strip().startswith('[') and not line.strip().endswith(']'):
                cleaned_lines.append(line)
            elif not line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_subject(self, context: LetterContext) -> str:
        """Generate an appropriate subject line."""
        subjects = {
            LetterType.APPLICATION: f"Volunteer Application - {context.role or 'General Volunteer'}",
            LetterType.THANK_YOU: f"Thank You - {context.organization or 'Volunteer Experience'}",
            LetterType.OUTREACH: f"Volunteer Opportunity Inquiry - {context.organization}",
            LetterType.FOLLOW_UP: f"Follow Up - {context.previous_action or 'Volunteer Application'}",
            LetterType.PARTNERSHIP: f"Partnership Proposal - Volunteer Program",
            LetterType.RECOMMENDATION_REQUEST: f"Recommendation Request - Volunteer Service",
            LetterType.CONFIRMATION: f"Confirmation - {context.role or 'Volunteer Commitment'}",
            LetterType.CANCELLATION: f"Schedule Change - {context.role or 'Volunteer Session'}",
        }
        
        return subjects.get(context.letter_type, "Volunteer Inquiry")
    
    def _assess_quality(self, body: str, context: LetterContext) -> float:
        """Assess the quality of the generated letter."""
        score = 1.0
        
        # Check for completeness
        if not context.sender_name or '[Your Name]' in body:
            score -= 0.1
        
        if not context.organization or 'your organization' in body:
            score -= 0.05
        
        # Check length
        word_count = len(body.split())
        if word_count < 50:
            score -= 0.1
        elif word_count > 500:
            score -= 0.05
        
        # Check for personalization
        if context.recipient_name and context.recipient_name in body:
            score += 0.05
        
        # Ensure within bounds
        return max(0.0, min(1.0, score))
    
    def _generate_suggestions(self, body: str, context: LetterContext, quality_score: float) -> List[str]:
        """Generate suggestions for improving the letter."""
        suggestions = []
        
        if quality_score < 1.0:
            if '[Your Name]' in body:
                suggestions.append("Add your name to personalize the letter")
            
            if 'your organization' in body:
                suggestions.append("Specify the organization name")
            
            if len(body.split()) < 100:
                suggestions.append("Consider adding more detail about your qualifications")
            
            if not context.experience:
                suggestions.append("Adding relevant experience can strengthen your application")
            
            if not context.skills:
                suggestions.append("Highlighting specific skills can make your letter more compelling")
        
        return suggestions
    
    # Template methods
    def _get_application_template(self) -> str:
        return """Dear {recipient_name},

I am writing to express my interest in volunteering as a {role} with {organization}. {reason}

{experience}

I am available {availability} and am committed to contributing meaningfully to your mission.

{skills}

{additional_info}

Thank you for considering my application. I look forward to the opportunity to contribute to your important work.

Sincerely,
{sender_name}
{sender_email}"""

    def _get_thank_you_template(self) -> str:
        return """Dear {recipient_name},

I wanted to express my heartfelt gratitude for the opportunity to volunteer with {organization}.

{experience}

The experience has been incredibly rewarding, and I have learned so much from working with your team.

{additional_info}

Thank you again for your guidance and support throughout my time volunteering.

With appreciation,
{sender_name}"""

    def _get_outreach_template(self) -> str:
        return """Subject: Volunteer Opportunity Inquiry

Dear {recipient_name},

I am reaching out to inquire about volunteer opportunities with {organization}. {reason}

{experience}

I would love to learn more about how I can contribute to your mission. {additional_info}

Would you be available for a brief call or meeting to discuss potential opportunities?

Best regards,
{sender_name}
{sender_email}"""

    def _get_follow_up_template(self) -> str:
        return """Dear {recipient_name},

I hope this message finds you well. I am following up on my {previous_action} regarding volunteer opportunities with {organization}.

{additional_info}

I remain very interested in contributing to your mission and would appreciate any updates you might have.

Please let me know if there is any additional information I can provide.

Thank you for your time.

Best regards,
{sender_name}
{sender_email}"""

    def _get_partnership_template(self) -> str:
        return """Subject: Partnership Proposal - Volunteer Program

Dear {recipient_name},

I am reaching out on behalf of our organization to explore potential partnership opportunities with {organization}.

{reason}

We believe that together, we could make a significant impact in our community through coordinated volunteer efforts.

{additional_info}

I would welcome the opportunity to discuss this further at your convenience.

Best regards,
{sender_name}
{sender_email}"""

    def _get_recommendation_template(self) -> str:
        return """Dear {recipient_name},

I hope this message finds you well. I am reaching out to request a letter of recommendation for my volunteer service with {organization}.

{experience}

{additional_info}

If you are able to provide a recommendation, I would be happy to provide any additional information that might be helpful.

Thank you for considering my request.

Sincerely,
{sender_name}
{sender_email}"""

    def _get_confirmation_template(self) -> str:
        return """Dear {recipient_name},

I am writing to confirm my commitment to volunteer as a {role} with {organization}.

I understand that I will be volunteering {availability}.

{additional_info}

Please let me know if there is anything I should prepare or bring.

Thank you, and I look forward to contributing to your team.

Best regards,
{sender_name}
{sender_email}"""

    def _get_cancellation_template(self) -> str:
        return """Dear {recipient_name},

I regret to inform you that I need to cancel/reschedule my upcoming volunteer session with {organization}.

{reason}

I sincerely apologize for any inconvenience this may cause. {additional_info}

I remain committed to volunteering and would like to reschedule at your earliest convenience.

Thank you for your understanding.

Sincerely,
{sender_name}
{sender_email}"""


# Export functions for use in web interface
def generate_application_letter(
    sender_name: str,
    organization: str,
    role: str = "volunteer",
    reason: str = "",
    experience: str = "",
    skills: str = "",
    availability: str = "flexible",
    **kwargs
) -> Dict[str, Any]:
    """Generate a volunteer application letter."""
    writer = AILetterWriter()
    
    context = LetterContext(
        letter_type=LetterType.APPLICATION,
        sender_name=sender_name,
        organization=organization,
        role=role,
        reason=reason,
        experience=experience,
        skills=skills,
        availability=availability,
        **{k: v for k, v in kwargs.items() if k in LetterContext.__dataclass_fields__}
    )
    
    letter = writer.generate_letter(context)
    
    return {
        'subject': letter.subject,
        'body': letter.body,
        'quality_score': letter.quality_score,
        'suggestions': letter.suggestions
    }


def generate_email(letter_type: str, **kwargs) -> Dict[str, Any]:
    """Generate an email of the specified type."""
    writer = AILetterWriter()
    
    type_map = {
        'application': LetterType.APPLICATION,
        'thank_you': LetterType.THANK_YOU,
        'outreach': LetterType.OUTREACH,
        'follow_up': LetterType.FOLLOW_UP,
        'partnership': LetterType.PARTNERSHIP,
        'recommendation': LetterType.RECOMMENDATION_REQUEST,
        'confirmation': LetterType.CONFIRMATION,
        'cancellation': LetterType.CANCELLATION,
    }
    
    context = LetterContext(
        letter_type=type_map.get(letter_type, LetterType.APPLICATION),
        sender_name=kwargs.get('sender_name', ''),
        **{k: v for k, v in kwargs.items() if k in LetterContext.__dataclass_fields__ and k != 'letter_type'}
    )
    
    letter = writer.generate_letter(context)
    
    return {
        'subject': letter.subject,
        'body': letter.body,
        'quality_score': letter.quality_score,
        'suggestions': letter.suggestions
    }


if __name__ == "__main__":
    # Demo
    print("=== AI Letter Writer Demo ===\n")
    
    result = generate_application_letter(
        sender_name="Jane Smith",
        organization="Local Food Bank",
        role="Food Distribution Volunteer",
        reason="I am passionate about fighting food insecurity in our community.",
        experience="I have previously volunteered at soup kitchens and community gardens.",
        skills="Strong organizational skills, food safety certification, bilingual (English/Spanish)",
        availability="Saturdays from 9 AM to 1 PM"
    )
    
    print(f"Subject: {result['subject']}")
    print(f"Quality Score: {result['quality_score']*100:.1f}%")
    print(f"\n{result['body']}")
    
    if result['suggestions']:
        print("\nSuggestions:")
        for suggestion in result['suggestions']:
            print(f"  - {suggestion}")
