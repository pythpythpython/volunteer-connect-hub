"""
VolunteerConnect Hub - User Profile AGI Board
==============================================

Comprehensive user profiling system that captures:
- Personal information
- Skills and expertise
- Work/education background
- Volunteer experience
- Interests and causes
- Availability and preferences
- Goals and motivations

This profile data is REQUIRED before using the platform and is used for:
- Generating personalized letters and applications
- Recommending volunteer opportunities
- Tracking volunteer journey and impact

Quality Target: 100% - Complete profile data for accurate recommendations
"""

import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ProfileSection(Enum):
    """Sections of the user profile questionnaire."""
    PERSONAL_INFO = "personal_info"
    SKILLS_EXPERTISE = "skills_expertise"
    EDUCATION_WORK = "education_work"
    VOLUNTEER_EXPERIENCE = "volunteer_experience"
    INTERESTS_CAUSES = "interests_causes"
    AVAILABILITY = "availability"
    GOALS_MOTIVATION = "goals_motivation"


class SkillLevel(Enum):
    """Skill proficiency levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class AgeGroup(Enum):
    """Age groups for appropriate opportunity matching."""
    UNDER_18 = "under_18"
    AGE_18_24 = "18_24"
    AGE_25_34 = "25_34"
    AGE_35_44 = "35_44"
    AGE_45_54 = "45_54"
    AGE_55_64 = "55_64"
    AGE_65_PLUS = "65_plus"


class VolunteerType(Enum):
    """Type of volunteer."""
    STUDENT = "student"
    PROFESSIONAL = "professional"
    RETIREE = "retiree"
    STAY_AT_HOME = "stay_at_home"
    UNEMPLOYED = "unemployed"
    OTHER = "other"


@dataclass
class Skill:
    """A user skill with proficiency level."""
    name: str
    level: str
    years_experience: int = 0
    description: str = ""


@dataclass
class Education:
    """Education history entry."""
    institution: str
    degree: str
    field_of_study: str
    graduation_year: int
    currently_enrolled: bool = False


@dataclass
class WorkExperience:
    """Work experience entry."""
    company: str
    position: str
    industry: str
    start_year: int
    end_year: Optional[int] = None
    currently_working: bool = False
    description: str = ""
    skills_used: List[str] = field(default_factory=list)


@dataclass
class VolunteerExperience:
    """Previous volunteer experience."""
    organization: str
    role: str
    cause_area: str
    start_date: str
    end_date: Optional[str] = None
    hours_contributed: float = 0
    description: str = ""
    impact_statement: str = ""
    reference_name: str = ""
    reference_contact: str = ""


@dataclass
class UserProfile:
    """Complete user profile for the volunteering platform."""
    # System fields
    user_id: str
    email: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    profile_complete: bool = False
    
    # Personal Information
    first_name: str = ""
    last_name: str = ""
    display_name: str = ""
    phone: str = ""
    location_city: str = ""
    location_state: str = ""
    location_country: str = ""
    age_group: str = ""
    volunteer_type: str = ""
    
    # Bio and Summary
    bio: str = ""
    linkedin_url: str = ""
    personal_website: str = ""
    
    # Skills and Expertise
    skills: List[Dict] = field(default_factory=list)
    languages: List[Dict] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    special_training: List[str] = field(default_factory=list)
    
    # Education
    education_history: List[Dict] = field(default_factory=list)
    current_education_status: str = ""
    
    # Work Experience
    work_history: List[Dict] = field(default_factory=list)
    current_employment_status: str = ""
    industry_expertise: List[str] = field(default_factory=list)
    
    # Volunteer Experience
    volunteer_history: List[Dict] = field(default_factory=list)
    total_volunteer_hours: float = 0
    volunteer_since_year: int = 0
    
    # Interests and Causes
    causes_interested: List[str] = field(default_factory=list)
    activities_preferred: List[str] = field(default_factory=list)
    populations_interested: List[str] = field(default_factory=list)
    
    # Availability
    availability_hours_per_week: int = 0
    availability_days: List[str] = field(default_factory=list)
    availability_times: List[str] = field(default_factory=list)
    prefers_virtual: bool = False
    prefers_in_person: bool = True
    willing_to_travel_miles: int = 10
    has_transportation: bool = True
    
    # Background Check
    willing_background_check: bool = True
    has_valid_drivers_license: bool = False
    
    # Goals and Motivation
    primary_motivation: str = ""
    goals: List[str] = field(default_factory=list)
    ideal_volunteer_role: str = ""
    what_hoping_to_gain: str = ""
    what_can_contribute: str = ""
    
    # Emergency Contact
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    emergency_contact_relationship: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create profile from dictionary."""
        return cls(**data)
    
    def calculate_completion_percentage(self) -> float:
        """Calculate profile completion percentage."""
        required_fields = {
            'first_name': 10,
            'last_name': 10,
            'email': 10,
            'location_city': 5,
            'age_group': 5,
            'volunteer_type': 5,
            'skills': 10,
            'causes_interested': 10,
            'availability_hours_per_week': 5,
            'availability_days': 5,
            'primary_motivation': 10,
            'goals': 10,
            'what_can_contribute': 5,
        }
        
        total_weight = sum(required_fields.values())
        completed_weight = 0
        
        for field_name, weight in required_fields.items():
            value = getattr(self, field_name, None)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    completed_weight += weight
                elif isinstance(value, str) and len(value) > 0:
                    completed_weight += weight
                elif isinstance(value, (int, float)) and value > 0:
                    completed_weight += weight
        
        return (completed_weight / total_weight) * 100
    
    def is_complete(self) -> bool:
        """Check if profile has minimum required fields filled."""
        return self.calculate_completion_percentage() >= 80
    
    def get_letter_context(self) -> Dict[str, Any]:
        """Get context data for letter generation."""
        return {
            'name': f"{self.first_name} {self.last_name}",
            'location': f"{self.location_city}, {self.location_state}",
            'volunteer_type': self.volunteer_type,
            'skills_summary': ', '.join([s['name'] for s in self.skills[:5]]) if self.skills else '',
            'education_summary': self._get_education_summary(),
            'work_summary': self._get_work_summary(),
            'volunteer_summary': self._get_volunteer_summary(),
            'causes': ', '.join(self.causes_interested[:3]) if self.causes_interested else '',
            'motivation': self.primary_motivation,
            'goals': ', '.join(self.goals[:3]) if self.goals else '',
            'availability': f"{self.availability_hours_per_week} hours/week",
            'what_can_contribute': self.what_can_contribute,
        }
    
    def _get_education_summary(self) -> str:
        """Get summary of education for letters."""
        if not self.education_history:
            return ""
        latest = self.education_history[0]
        return f"{latest.get('degree', '')} in {latest.get('field_of_study', '')} from {latest.get('institution', '')}"
    
    def _get_work_summary(self) -> str:
        """Get summary of work experience for letters."""
        if not self.work_history:
            return ""
        latest = self.work_history[0]
        return f"{latest.get('position', '')} at {latest.get('company', '')} ({latest.get('industry', '')})"
    
    def _get_volunteer_summary(self) -> str:
        """Get summary of volunteer experience for letters."""
        if not self.volunteer_history:
            if self.total_volunteer_hours > 0:
                return f"{self.total_volunteer_hours} hours of volunteer experience"
            return "Eager to start my volunteer journey"
        return f"{len(self.volunteer_history)} organizations, {self.total_volunteer_hours} total hours"


class UserProfileAGI:
    """
    User Profile AGI Board - Manages comprehensive user profiling.
    
    Responsibilities:
    1. Generate and validate questionnaire responses
    2. Calculate profile completeness
    3. Extract context for letter generation
    4. Provide recommendations based on profile
    
    Quality Target: 100% - Complete, accurate user profiles
    """
    
    QUESTIONNAIRE_SECTIONS = [
        {
            "id": "personal_info",
            "title": "Personal Information",
            "description": "Basic information about yourself",
            "required": True,
            "questions": [
                {"id": "first_name", "type": "text", "label": "First Name", "required": True},
                {"id": "last_name", "type": "text", "label": "Last Name", "required": True},
                {"id": "display_name", "type": "text", "label": "Display Name (how you want to be called)", "required": False},
                {"id": "phone", "type": "tel", "label": "Phone Number", "required": False},
                {"id": "location_city", "type": "text", "label": "City", "required": True},
                {"id": "location_state", "type": "text", "label": "State/Province", "required": True},
                {"id": "location_country", "type": "text", "label": "Country", "required": True, "default": "United States"},
                {"id": "age_group", "type": "select", "label": "Age Group", "required": True, "options": [
                    {"value": "under_18", "label": "Under 18"},
                    {"value": "18_24", "label": "18-24"},
                    {"value": "25_34", "label": "25-34"},
                    {"value": "35_44", "label": "35-44"},
                    {"value": "45_54", "label": "45-54"},
                    {"value": "55_64", "label": "55-64"},
                    {"value": "65_plus", "label": "65+"},
                ]},
                {"id": "volunteer_type", "type": "select", "label": "I am a...", "required": True, "options": [
                    {"value": "student", "label": "Student"},
                    {"value": "professional", "label": "Working Professional"},
                    {"value": "retiree", "label": "Retiree"},
                    {"value": "stay_at_home", "label": "Stay-at-Home Parent/Caregiver"},
                    {"value": "unemployed", "label": "Currently Unemployed"},
                    {"value": "other", "label": "Other"},
                ]},
            ]
        },
        {
            "id": "skills_expertise",
            "title": "Skills & Expertise",
            "description": "What skills and abilities can you contribute?",
            "required": True,
            "questions": [
                {"id": "skills", "type": "skill_list", "label": "Your Skills", "required": True, 
                 "help": "Add skills you have that could be valuable for volunteering",
                 "suggested": [
                    "Communication", "Teaching/Tutoring", "Writing", "Public Speaking",
                    "Project Management", "Event Planning", "Social Media", "Marketing",
                    "Graphic Design", "Web Development", "Data Analysis", "Research",
                    "First Aid/CPR", "Counseling", "Translation", "Photography",
                    "Cooking/Food Service", "Carpentry", "Gardening", "Driving",
                    "Fundraising", "Grant Writing", "Accounting", "Legal",
                    "Healthcare", "Childcare", "Elder Care", "Animal Care",
                 ]},
                {"id": "languages", "type": "language_list", "label": "Languages You Speak", "required": False},
                {"id": "certifications", "type": "tag_list", "label": "Certifications", "required": False,
                 "help": "e.g., CPR, Teaching Certificate, PMP, etc."},
                {"id": "special_training", "type": "tag_list", "label": "Special Training", "required": False,
                 "help": "e.g., Crisis intervention, Disaster response, etc."},
            ]
        },
        {
            "id": "education_work",
            "title": "Education & Work Background",
            "description": "Your educational and professional background",
            "required": False,
            "questions": [
                {"id": "current_education_status", "type": "select", "label": "Education Status", "required": False, "options": [
                    {"value": "high_school", "label": "High School Student"},
                    {"value": "high_school_grad", "label": "High School Graduate"},
                    {"value": "college", "label": "College/University Student"},
                    {"value": "college_grad", "label": "College Graduate"},
                    {"value": "graduate_school", "label": "Graduate Student"},
                    {"value": "graduate_degree", "label": "Graduate Degree Holder"},
                    {"value": "other", "label": "Other"},
                ]},
                {"id": "education_history", "type": "education_list", "label": "Education History", "required": False},
                {"id": "current_employment_status", "type": "select", "label": "Employment Status", "required": False, "options": [
                    {"value": "employed_full", "label": "Employed Full-Time"},
                    {"value": "employed_part", "label": "Employed Part-Time"},
                    {"value": "self_employed", "label": "Self-Employed"},
                    {"value": "unemployed", "label": "Unemployed"},
                    {"value": "retired", "label": "Retired"},
                    {"value": "student", "label": "Student"},
                ]},
                {"id": "work_history", "type": "work_list", "label": "Work Experience", "required": False},
                {"id": "industry_expertise", "type": "tag_list", "label": "Industry Expertise", "required": False,
                 "help": "Industries you have experience in"},
            ]
        },
        {
            "id": "volunteer_experience",
            "title": "Volunteer Experience",
            "description": "Tell us about your previous volunteer work",
            "required": False,
            "questions": [
                {"id": "volunteer_since_year", "type": "number", "label": "Year you started volunteering", "required": False,
                 "help": "Leave blank if you're new to volunteering"},
                {"id": "total_volunteer_hours", "type": "number", "label": "Estimated total volunteer hours", "required": False},
                {"id": "volunteer_history", "type": "volunteer_list", "label": "Previous Volunteer Roles", "required": False},
            ]
        },
        {
            "id": "interests_causes",
            "title": "Interests & Causes",
            "description": "What causes are you passionate about?",
            "required": True,
            "questions": [
                {"id": "causes_interested", "type": "checkbox_list", "label": "Causes I Care About", "required": True,
                 "min_selections": 1, "options": [
                    {"value": "education", "label": "Education & Literacy"},
                    {"value": "environment", "label": "Environment & Conservation"},
                    {"value": "health", "label": "Health & Wellness"},
                    {"value": "hunger", "label": "Hunger & Food Security"},
                    {"value": "housing", "label": "Housing & Homelessness"},
                    {"value": "animals", "label": "Animal Welfare"},
                    {"value": "arts", "label": "Arts & Culture"},
                    {"value": "seniors", "label": "Senior Services"},
                    {"value": "youth", "label": "Youth Development"},
                    {"value": "veterans", "label": "Veterans & Military"},
                    {"value": "disaster", "label": "Disaster Relief"},
                    {"value": "community", "label": "Community Development"},
                    {"value": "civic", "label": "Civic Engagement"},
                    {"value": "immigrants", "label": "Immigrant & Refugee Services"},
                    {"value": "disability", "label": "Disability Services"},
                    {"value": "mental_health", "label": "Mental Health"},
                    {"value": "poverty", "label": "Poverty Alleviation"},
                    {"value": "justice", "label": "Social Justice"},
                    {"value": "faith", "label": "Faith-Based Service"},
                    {"value": "international", "label": "International Development"},
                ]},
                {"id": "activities_preferred", "type": "checkbox_list", "label": "Activities I Enjoy", "required": False, "options": [
                    {"value": "direct_service", "label": "Direct Service (working with people)"},
                    {"value": "administrative", "label": "Administrative/Office Work"},
                    {"value": "physical", "label": "Physical Labor (building, cleaning)"},
                    {"value": "teaching", "label": "Teaching/Mentoring"},
                    {"value": "fundraising", "label": "Fundraising/Events"},
                    {"value": "advocacy", "label": "Advocacy/Awareness"},
                    {"value": "tech", "label": "Technology/Digital"},
                    {"value": "creative", "label": "Creative/Artistic"},
                    {"value": "leadership", "label": "Leadership/Board Service"},
                    {"value": "research", "label": "Research/Analysis"},
                ]},
                {"id": "populations_interested", "type": "checkbox_list", "label": "Populations I Want to Help", "required": False, "options": [
                    {"value": "children", "label": "Children (0-12)"},
                    {"value": "teens", "label": "Teenagers (13-18)"},
                    {"value": "young_adults", "label": "Young Adults (18-25)"},
                    {"value": "adults", "label": "Adults"},
                    {"value": "seniors", "label": "Seniors (65+)"},
                    {"value": "families", "label": "Families"},
                    {"value": "homeless", "label": "People Experiencing Homelessness"},
                    {"value": "disabled", "label": "People with Disabilities"},
                    {"value": "immigrants", "label": "Immigrants/Refugees"},
                    {"value": "veterans", "label": "Veterans"},
                    {"value": "animals", "label": "Animals"},
                    {"value": "general", "label": "General Community"},
                ]},
            ]
        },
        {
            "id": "availability",
            "title": "Availability",
            "description": "When and how can you volunteer?",
            "required": True,
            "questions": [
                {"id": "availability_hours_per_week", "type": "select", "label": "Hours available per week", "required": True, "options": [
                    {"value": "1", "label": "1-2 hours"},
                    {"value": "3", "label": "3-5 hours"},
                    {"value": "6", "label": "6-10 hours"},
                    {"value": "11", "label": "11-20 hours"},
                    {"value": "20", "label": "20+ hours"},
                ]},
                {"id": "availability_days", "type": "checkbox_list", "label": "Days Available", "required": True, "options": [
                    {"value": "monday", "label": "Monday"},
                    {"value": "tuesday", "label": "Tuesday"},
                    {"value": "wednesday", "label": "Wednesday"},
                    {"value": "thursday", "label": "Thursday"},
                    {"value": "friday", "label": "Friday"},
                    {"value": "saturday", "label": "Saturday"},
                    {"value": "sunday", "label": "Sunday"},
                ]},
                {"id": "availability_times", "type": "checkbox_list", "label": "Times Available", "required": False, "options": [
                    {"value": "morning", "label": "Morning (6am-12pm)"},
                    {"value": "afternoon", "label": "Afternoon (12pm-5pm)"},
                    {"value": "evening", "label": "Evening (5pm-9pm)"},
                    {"value": "night", "label": "Night (after 9pm)"},
                ]},
                {"id": "prefers_virtual", "type": "checkbox", "label": "I'm interested in virtual/remote volunteering", "required": False},
                {"id": "prefers_in_person", "type": "checkbox", "label": "I'm interested in in-person volunteering", "required": False, "default": True},
                {"id": "willing_to_travel_miles", "type": "select", "label": "Willing to travel (miles)", "required": False, "options": [
                    {"value": "5", "label": "Up to 5 miles"},
                    {"value": "10", "label": "Up to 10 miles"},
                    {"value": "25", "label": "Up to 25 miles"},
                    {"value": "50", "label": "Up to 50 miles"},
                    {"value": "100", "label": "Any distance"},
                ]},
                {"id": "has_transportation", "type": "checkbox", "label": "I have reliable transportation", "required": False},
                {"id": "willing_background_check", "type": "checkbox", "label": "I'm willing to undergo a background check if required", "required": False},
                {"id": "has_valid_drivers_license", "type": "checkbox", "label": "I have a valid driver's license", "required": False},
            ]
        },
        {
            "id": "goals_motivation",
            "title": "Goals & Motivation",
            "description": "Help us understand what drives you",
            "required": True,
            "questions": [
                {"id": "primary_motivation", "type": "select", "label": "Primary motivation for volunteering", "required": True, "options": [
                    {"value": "give_back", "label": "Want to give back to my community"},
                    {"value": "skills", "label": "Want to develop new skills"},
                    {"value": "career", "label": "Career exploration/development"},
                    {"value": "social", "label": "Meet new people/social connection"},
                    {"value": "requirement", "label": "School/work requirement"},
                    {"value": "passion", "label": "Passionate about a specific cause"},
                    {"value": "religious", "label": "Religious/spiritual calling"},
                    {"value": "family", "label": "Family tradition/activity"},
                    {"value": "other", "label": "Other"},
                ]},
                {"id": "goals", "type": "checkbox_list", "label": "What do you hope to achieve?", "required": True, "min_selections": 1, "options": [
                    {"value": "make_difference", "label": "Make a meaningful difference"},
                    {"value": "learn_skills", "label": "Learn new skills"},
                    {"value": "build_resume", "label": "Build my resume/portfolio"},
                    {"value": "network", "label": "Network with professionals"},
                    {"value": "explore_careers", "label": "Explore career options"},
                    {"value": "meet_people", "label": "Meet like-minded people"},
                    {"value": "stay_active", "label": "Stay active and engaged"},
                    {"value": "family_time", "label": "Quality time with family"},
                    {"value": "leadership", "label": "Develop leadership skills"},
                    {"value": "give_back", "label": "Give back for help I received"},
                ]},
                {"id": "ideal_volunteer_role", "type": "textarea", "label": "Describe your ideal volunteer role", "required": False,
                 "help": "What would your perfect volunteering experience look like?"},
                {"id": "what_hoping_to_gain", "type": "textarea", "label": "What are you hoping to gain from volunteering?", "required": False},
                {"id": "what_can_contribute", "type": "textarea", "label": "What unique value can you contribute?", "required": True,
                 "help": "Think about your unique combination of skills, experience, and perspective"},
            ]
        },
        {
            "id": "emergency_contact",
            "title": "Emergency Contact",
            "description": "In case of emergency during volunteering",
            "required": False,
            "questions": [
                {"id": "emergency_contact_name", "type": "text", "label": "Emergency Contact Name", "required": False},
                {"id": "emergency_contact_phone", "type": "tel", "label": "Emergency Contact Phone", "required": False},
                {"id": "emergency_contact_relationship", "type": "text", "label": "Relationship", "required": False},
            ]
        },
    ]
    
    def __init__(self):
        self.questionnaire = self.QUESTIONNAIRE_SECTIONS
    
    def get_questionnaire(self) -> List[Dict]:
        """Get the full questionnaire structure."""
        return self.questionnaire
    
    def get_section(self, section_id: str) -> Optional[Dict]:
        """Get a specific section of the questionnaire."""
        for section in self.questionnaire:
            if section['id'] == section_id:
                return section
        return None
    
    def validate_section(self, section_id: str, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Validate responses for a section."""
        section = self.get_section(section_id)
        if not section:
            return {"valid": False, "errors": ["Invalid section"]}
        
        errors = []
        for question in section['questions']:
            if question.get('required', False):
                value = responses.get(question['id'])
                if not value or (isinstance(value, list) and len(value) == 0):
                    errors.append(f"{question['label']} is required")
                
                # Check minimum selections for checkbox lists
                min_sel = question.get('min_selections', 0)
                if min_sel > 0 and isinstance(value, list) and len(value) < min_sel:
                    errors.append(f"{question['label']} requires at least {min_sel} selection(s)")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def validate_profile(self, profile: UserProfile) -> Dict[str, Any]:
        """Validate entire profile for completeness."""
        completion = profile.calculate_completion_percentage()
        is_complete = completion >= 80
        
        missing = []
        if not profile.first_name:
            missing.append("First name")
        if not profile.last_name:
            missing.append("Last name")
        if not profile.location_city:
            missing.append("City")
        if not profile.age_group:
            missing.append("Age group")
        if not profile.skills:
            missing.append("Skills")
        if not profile.causes_interested:
            missing.append("Causes of interest")
        if not profile.primary_motivation:
            missing.append("Primary motivation")
        if not profile.goals:
            missing.append("Goals")
        if not profile.what_can_contribute:
            missing.append("What you can contribute")
        
        return {
            "is_complete": is_complete,
            "completion_percentage": completion,
            "missing_fields": missing,
            "can_use_platform": is_complete,
        }
    
    def generate_letter_context(self, profile: UserProfile, opportunity: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive context for letter generation."""
        context = profile.get_letter_context()
        
        # Add opportunity-specific context if provided
        if opportunity:
            context['opportunity_name'] = opportunity.get('title', '')
            context['organization'] = opportunity.get('organization', '')
            context['opportunity_description'] = opportunity.get('description', '')
        
        # Generate narrative summaries
        context['skills_narrative'] = self._generate_skills_narrative(profile)
        context['experience_narrative'] = self._generate_experience_narrative(profile)
        context['motivation_narrative'] = self._generate_motivation_narrative(profile)
        
        return context
    
    def _generate_skills_narrative(self, profile: UserProfile) -> str:
        """Generate a narrative about user's skills."""
        if not profile.skills:
            return "I am eager to learn and develop new skills through volunteering."
        
        top_skills = [s['name'] for s in profile.skills[:3]]
        return f"I bring skills in {', '.join(top_skills)}, which I believe would be valuable for this role."
    
    def _generate_experience_narrative(self, profile: UserProfile) -> str:
        """Generate a narrative about user's experience."""
        parts = []
        
        if profile.work_history:
            latest = profile.work_history[0]
            parts.append(f"As a {latest.get('position', 'professional')} in {latest.get('industry', 'my field')}")
        
        if profile.volunteer_history:
            parts.append(f"with {len(profile.volunteer_history)} previous volunteer experiences totaling {profile.total_volunteer_hours} hours")
        elif profile.total_volunteer_hours > 0:
            parts.append(f"with {profile.total_volunteer_hours} hours of volunteer experience")
        
        if profile.education_history:
            latest = profile.education_history[0]
            parts.append(f"and a background in {latest.get('field_of_study', 'my studies')}")
        
        if parts:
            return ', '.join(parts) + ", I am well-prepared to contribute meaningfully."
        
        return "While I may be new to volunteering, I am enthusiastic and committed to making a difference."
    
    def _generate_motivation_narrative(self, profile: UserProfile) -> str:
        """Generate a narrative about user's motivation."""
        motivation_map = {
            "give_back": "I am deeply motivated to give back to my community",
            "skills": "I am excited to develop new skills while making a positive impact",
            "career": "I see volunteering as an opportunity to grow professionally while serving others",
            "social": "I am looking forward to connecting with like-minded individuals",
            "passion": "I am passionate about this cause and want to contribute meaningfully",
            "religious": "My faith inspires me to serve others",
            "family": "I value the tradition of service in my family",
        }
        
        base = motivation_map.get(profile.primary_motivation, "I am motivated to volunteer")
        
        if profile.goals:
            goals_text = " and ".join(profile.goals[:2])
            return f"{base}. Through this experience, I hope to {goals_text}."
        
        return f"{base}."
    
    def get_recommendations_criteria(self, profile: UserProfile) -> Dict[str, Any]:
        """Get criteria for opportunity recommendations based on profile."""
        return {
            "causes": profile.causes_interested,
            "activities": profile.activities_preferred,
            "populations": profile.populations_interested,
            "skills": [s['name'] for s in profile.skills] if profile.skills else [],
            "hours_available": profile.availability_hours_per_week,
            "days_available": profile.availability_days,
            "virtual_ok": profile.prefers_virtual,
            "in_person_ok": profile.prefers_in_person,
            "max_distance_miles": profile.willing_to_travel_miles,
            "location": {
                "city": profile.location_city,
                "state": profile.location_state,
                "country": profile.location_country,
            },
            "background_check_ok": profile.willing_background_check,
        }


def export_questionnaire_json() -> str:
    """Export questionnaire structure as JSON for frontend use."""
    agi = UserProfileAGI()
    return json.dumps(agi.get_questionnaire(), indent=2)


if __name__ == "__main__":
    # Print questionnaire structure
    print("User Profile Questionnaire Structure")
    print("=" * 50)
    
    agi = UserProfileAGI()
    for section in agi.get_questionnaire():
        print(f"\n{section['title']}")
        print(f"  Required: {section['required']}")
        print(f"  Questions: {len(section['questions'])}")
        for q in section['questions']:
            req = "*" if q.get('required') else ""
            print(f"    - {q['label']}{req} ({q['type']})")
