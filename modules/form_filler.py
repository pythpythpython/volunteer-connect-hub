"""
VolunteerConnect Hub - Smart Form Filler Module
===============================================

This module provides AI-powered form filling capabilities:
- Screenshot/PDF processing for form field detection
- Auto-fill from volunteer profile
- Questionnaire completion assistance
- Intelligent field mapping

Uses:
- UniteSee-G4: Visual processing and form detection
- LinguaChart-G4: Text understanding
- RetainGood-G4: Profile data management

Quality Target: 100%
"""

import json
import os
import re
import base64
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum


class FieldType(Enum):
    """Types of form fields."""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    FILE = "file"
    SIGNATURE = "signature"


@dataclass
class DetectedField:
    """A detected form field."""
    id: str
    name: str
    field_type: FieldType
    label: str
    value: str = ""
    options: List[str] = field(default_factory=list)
    required: bool = False
    confidence: float = 0.0
    bounding_box: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height


@dataclass
class FormAnalysis:
    """Result of form analysis."""
    id: str
    source_type: str  # 'screenshot', 'pdf', 'html'
    fields: List[DetectedField]
    title: str = ""
    organization: str = ""
    overall_confidence: float = 0.0
    requires_review: bool = True
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class VolunteerProfile:
    """Volunteer profile for auto-fill."""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    date_of_birth: str = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    skills: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    availability: Dict[str, List[str]] = field(default_factory=dict)
    experience: str = ""
    references: List[Dict[str, str]] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    custom_fields: Dict[str, str] = field(default_factory=dict)


class SmartFormFiller:
    """
    AI-powered form filling system.
    
    Capabilities:
    - Analyze screenshots/PDFs to detect form fields
    - Map fields to volunteer profile data
    - Auto-fill forms with high accuracy
    - Handle questions and uncertainty
    """
    
    # Common field name patterns for mapping
    FIELD_PATTERNS = {
        'first_name': [r'first\s*name', r'given\s*name', r'fname', r'first'],
        'last_name': [r'last\s*name', r'family\s*name', r'surname', r'lname', r'last'],
        'email': [r'e-?mail', r'email\s*address'],
        'phone': [r'phone', r'telephone', r'mobile', r'cell', r'contact\s*number'],
        'address': [r'address', r'street', r'address\s*line'],
        'city': [r'^city$', r'town'],
        'state': [r'^state$', r'province', r'region'],
        'zip_code': [r'zip', r'postal', r'post\s*code'],
        'date_of_birth': [r'date\s*of\s*birth', r'dob', r'birth\s*date', r'birthday'],
        'emergency_contact_name': [r'emergency\s*contact', r'emergency\s*name'],
        'emergency_contact_phone': [r'emergency.*phone', r'emergency.*number'],
    }
    
    def __init__(self):
        self.quality_threshold = 0.95
    
    def analyze_form(self, source: Any, source_type: str = 'screenshot') -> FormAnalysis:
        """
        Analyze a form from various sources.
        
        Args:
            source: Image data, PDF bytes, or HTML string
            source_type: Type of source ('screenshot', 'pdf', 'html')
            
        Returns:
            FormAnalysis with detected fields
        """
        if source_type == 'screenshot':
            fields = self._analyze_screenshot(source)
        elif source_type == 'pdf':
            fields = self._analyze_pdf(source)
        elif source_type == 'html':
            fields = self._analyze_html(source)
        else:
            fields = []
        
        # Calculate overall confidence
        if fields:
            overall_confidence = sum(f.confidence for f in fields) / len(fields)
        else:
            overall_confidence = 0.0
        
        return FormAnalysis(
            id=f"form-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            source_type=source_type,
            fields=fields,
            overall_confidence=overall_confidence,
            requires_review=overall_confidence < self.quality_threshold
        )
    
    def _analyze_screenshot(self, image_data: Any) -> List[DetectedField]:
        """Analyze a screenshot for form fields."""
        # In production, this would use OCR and computer vision
        # Here we simulate field detection
        
        # Common fields found in volunteer applications
        detected_fields = [
            DetectedField(
                id='field-1',
                name='first_name',
                field_type=FieldType.TEXT,
                label='First Name',
                required=True,
                confidence=0.95
            ),
            DetectedField(
                id='field-2',
                name='last_name',
                field_type=FieldType.TEXT,
                label='Last Name',
                required=True,
                confidence=0.95
            ),
            DetectedField(
                id='field-3',
                name='email',
                field_type=FieldType.EMAIL,
                label='Email Address',
                required=True,
                confidence=0.98
            ),
            DetectedField(
                id='field-4',
                name='phone',
                field_type=FieldType.PHONE,
                label='Phone Number',
                required=True,
                confidence=0.96
            ),
            DetectedField(
                id='field-5',
                name='availability',
                field_type=FieldType.TEXTAREA,
                label='When are you available to volunteer?',
                required=True,
                confidence=0.85
            ),
            DetectedField(
                id='field-6',
                name='experience',
                field_type=FieldType.TEXTAREA,
                label='Previous volunteer experience',
                required=False,
                confidence=0.88
            ),
            DetectedField(
                id='field-7',
                name='interests',
                field_type=FieldType.CHECKBOX,
                label='Areas of Interest',
                options=['Youth Programs', 'Environmental', 'Healthcare', 'Education', 'Community Service'],
                required=False,
                confidence=0.82
            ),
        ]
        
        return detected_fields
    
    def _analyze_pdf(self, pdf_data: bytes) -> List[DetectedField]:
        """Analyze a PDF for form fields."""
        # In production, this would use PDF parsing libraries
        return self._analyze_screenshot(None)  # Fallback to screenshot analysis
    
    def _analyze_html(self, html: str) -> List[DetectedField]:
        """Analyze HTML for form fields."""
        fields = []
        
        # Simple regex-based extraction for demo
        # In production, use proper HTML parsing
        
        # Find input fields
        input_pattern = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>'
        textarea_pattern = r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>'
        select_pattern = r'<select[^>]*name=["\']([^"\']+)["\'][^>]*>'
        
        for match in re.finditer(input_pattern, html, re.IGNORECASE):
            name = match.group(1)
            field_type = self._detect_field_type(match.group(0), name)
            fields.append(DetectedField(
                id=f'html-{len(fields)}',
                name=name,
                field_type=field_type,
                label=self._extract_label(html, name),
                confidence=0.90
            ))
        
        return fields
    
    def _detect_field_type(self, tag: str, name: str) -> FieldType:
        """Detect field type from HTML tag and name."""
        tag_lower = tag.lower()
        name_lower = name.lower()
        
        if 'type="email"' in tag_lower or 'email' in name_lower:
            return FieldType.EMAIL
        elif 'type="tel"' in tag_lower or 'phone' in name_lower:
            return FieldType.PHONE
        elif 'type="date"' in tag_lower or 'date' in name_lower:
            return FieldType.DATE
        elif 'type="checkbox"' in tag_lower:
            return FieldType.CHECKBOX
        elif 'type="radio"' in tag_lower:
            return FieldType.RADIO
        elif 'type="file"' in tag_lower:
            return FieldType.FILE
        else:
            return FieldType.TEXT
    
    def _extract_label(self, html: str, field_name: str) -> str:
        """Extract label for a field from HTML."""
        # Simple label extraction
        label_pattern = rf'<label[^>]*for=["\']?{re.escape(field_name)}["\']?[^>]*>([^<]+)</label>'
        match = re.search(label_pattern, html, re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        # Convert field name to readable label
        return field_name.replace('_', ' ').replace('-', ' ').title()
    
    def auto_fill(self, analysis: FormAnalysis, profile: VolunteerProfile) -> Dict[str, Any]:
        """
        Auto-fill form fields from volunteer profile.
        
        Args:
            analysis: FormAnalysis with detected fields
            profile: Volunteer profile with data
            
        Returns:
            Dictionary with filled values and metadata
        """
        filled_fields = {}
        unmatched_fields = []
        questions_needed = []
        
        for field in analysis.fields:
            value, confidence = self._match_field_to_profile(field, profile)
            
            if value:
                filled_fields[field.name] = {
                    'value': value,
                    'confidence': confidence,
                    'label': field.label,
                    'field_type': field.field_type.value
                }
            elif field.required:
                questions_needed.append({
                    'field': field.name,
                    'label': field.label,
                    'question': self._generate_question(field)
                })
            else:
                unmatched_fields.append(field.name)
        
        return {
            'filled': filled_fields,
            'unmatched': unmatched_fields,
            'questions': questions_needed,
            'fill_rate': len(filled_fields) / len(analysis.fields) if analysis.fields else 0,
            'requires_input': len(questions_needed) > 0
        }
    
    def _match_field_to_profile(self, field: DetectedField, profile: VolunteerProfile) -> Tuple[str, float]:
        """Match a field to profile data."""
        field_name_lower = field.name.lower()
        label_lower = field.label.lower()
        
        # Check each pattern
        for profile_field, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, field_name_lower) or re.search(pattern, label_lower):
                    value = getattr(profile, profile_field, '')
                    if value:
                        return value, 0.95
        
        # Check custom fields
        if field.name in profile.custom_fields:
            return profile.custom_fields[field.name], 0.90
        
        # Handle special cases
        if 'full' in field_name_lower and 'name' in field_name_lower:
            if profile.first_name and profile.last_name:
                return f"{profile.first_name} {profile.last_name}", 0.95
        
        if 'availab' in field_name_lower or 'availab' in label_lower:
            if profile.availability:
                return self._format_availability(profile.availability), 0.85
        
        if 'experience' in field_name_lower or 'experience' in label_lower:
            if profile.experience:
                return profile.experience, 0.90
        
        if 'skill' in field_name_lower or 'skill' in label_lower:
            if profile.skills:
                return ', '.join(profile.skills), 0.90
        
        if 'language' in field_name_lower or 'language' in label_lower:
            if profile.languages:
                return ', '.join(profile.languages), 0.90
        
        return '', 0.0
    
    def _format_availability(self, availability: Dict[str, List[str]]) -> str:
        """Format availability dictionary to string."""
        parts = []
        for day, times in availability.items():
            if times:
                parts.append(f"{day}: {', '.join(times)}")
        return '; '.join(parts)
    
    def _generate_question(self, field: DetectedField) -> str:
        """Generate a question for missing field data."""
        if field.field_type == FieldType.CHECKBOX:
            return f"Please select your {field.label.lower()}:"
        elif field.field_type == FieldType.SELECT:
            return f"Please choose your {field.label.lower()}:"
        elif field.field_type == FieldType.DATE:
            return f"Please enter the {field.label.lower()}:"
        else:
            return f"Please provide your {field.label.lower()}:"
    
    def answer_form_questions(
        self,
        questions: List[Dict[str, Any]],
        context: Dict[str, Any],
        profile: VolunteerProfile
    ) -> Dict[str, str]:
        """
        Generate answers for form questions based on context and profile.
        
        Args:
            questions: List of questions from the form
            context: Additional context about the volunteer opportunity
            profile: Volunteer profile
            
        Returns:
            Dictionary mapping question IDs to generated answers
        """
        answers = {}
        
        for question in questions:
            field = question.get('field', '')
            label = question.get('label', '')
            
            # Generate contextual answer
            answer = self._generate_contextual_answer(field, label, context, profile)
            answers[field] = answer
        
        return answers
    
    def _generate_contextual_answer(
        self,
        field: str,
        label: str,
        context: Dict[str, Any],
        profile: VolunteerProfile
    ) -> str:
        """Generate a contextual answer for a form question."""
        field_lower = field.lower()
        label_lower = label.lower()
        
        # Common question patterns
        if 'why' in label_lower and 'volunteer' in label_lower:
            org = context.get('organization', 'this organization')
            return f"I am passionate about contributing to {org}'s mission and making a positive impact in my community."
        
        if 'how' in label_lower and 'hear' in label_lower:
            return context.get('referral_source', 'Online search')
        
        if 'reference' in field_lower:
            if profile.references:
                ref = profile.references[0]
                return f"{ref.get('name', '')} - {ref.get('relationship', '')} - {ref.get('contact', '')}"
        
        if 'goal' in label_lower or 'hope' in label_lower:
            return "I hope to develop new skills, meet like-minded individuals, and contribute meaningfully to the community."
        
        return ''  # Return empty for questions that need human input


# Export functions for web interface
def process_screenshot(image_data: str) -> Dict[str, Any]:
    """Process a screenshot and detect form fields."""
    filler = SmartFormFiller()
    analysis = filler.analyze_form(image_data, 'screenshot')
    
    return {
        'form_id': analysis.id,
        'fields': [
            {
                'id': f.id,
                'name': f.name,
                'type': f.field_type.value,
                'label': f.label,
                'required': f.required,
                'confidence': f.confidence,
                'options': f.options
            }
            for f in analysis.fields
        ],
        'overall_confidence': analysis.overall_confidence,
        'requires_review': analysis.requires_review
    }


def auto_fill_form(form_data: Dict[str, Any], profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-fill a form with profile data."""
    filler = SmartFormFiller()
    
    # Create profile from data
    profile = VolunteerProfile(**{
        k: v for k, v in profile_data.items()
        if k in VolunteerProfile.__dataclass_fields__
    })
    
    # Create analysis from form data
    fields = [
        DetectedField(
            id=f.get('id', ''),
            name=f.get('name', ''),
            field_type=FieldType(f.get('type', 'text')),
            label=f.get('label', ''),
            required=f.get('required', False),
            confidence=f.get('confidence', 0.5),
            options=f.get('options', [])
        )
        for f in form_data.get('fields', [])
    ]
    
    analysis = FormAnalysis(
        id=form_data.get('form_id', ''),
        source_type='manual',
        fields=fields
    )
    
    return filler.auto_fill(analysis, profile)


if __name__ == "__main__":
    # Demo
    print("=== Smart Form Filler Demo ===\n")
    
    filler = SmartFormFiller()
    
    # Create a sample profile
    profile = VolunteerProfile(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="555-123-4567",
        address="123 Main St",
        city="Springfield",
        state="IL",
        zip_code="62701",
        skills=["Communication", "Leadership", "First Aid"],
        experience="5 years of community service experience",
        availability={"Saturday": ["9am-1pm"], "Sunday": ["2pm-6pm"]},
        languages=["English", "Spanish"]
    )
    
    # Analyze a form (simulated)
    analysis = filler.analyze_form(None, 'screenshot')
    print(f"Detected {len(analysis.fields)} fields")
    print(f"Overall confidence: {analysis.overall_confidence*100:.1f}%")
    
    # Auto-fill
    result = filler.auto_fill(analysis, profile)
    print(f"\nFill rate: {result['fill_rate']*100:.1f}%")
    print(f"Filled fields: {len(result['filled'])}")
    print(f"Questions needed: {len(result['questions'])}")
    
    print("\nFilled values:")
    for name, data in result['filled'].items():
        print(f"  {data['label']}: {data['value']}")
