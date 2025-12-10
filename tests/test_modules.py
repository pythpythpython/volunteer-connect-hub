"""
VolunteerConnect Hub - Module Tests
===================================

Comprehensive test suite for all volunteering modules.
Target: 100% quality across all tests.
"""

import pytest
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLetterWriter:
    """Tests for the AI Letter Writer module."""
    
    def test_import(self):
        """Test module can be imported."""
        from modules.letter_writer import AILetterWriter, LetterType, LetterContext
        assert AILetterWriter is not None
        assert LetterType is not None
    
    def test_generate_application_letter(self):
        """Test application letter generation."""
        from modules.letter_writer import generate_application_letter
        
        result = generate_application_letter(
            sender_name="John Doe",
            organization="Test Org",
            role="Volunteer",
            reason="I want to help"
        )
        
        assert 'subject' in result
        assert 'body' in result
        assert 'quality_score' in result
        assert result['quality_score'] > 0.8
        assert "John Doe" in result['body']
        assert "Test Org" in result['body']
    
    def test_letter_types(self):
        """Test all letter types can be generated."""
        from modules.letter_writer import generate_email
        
        letter_types = ['application', 'thank_you', 'outreach', 'follow_up']
        
        for letter_type in letter_types:
            result = generate_email(
                letter_type=letter_type,
                sender_name="Test User",
                organization="Test Org"
            )
            assert 'body' in result
            assert len(result['body']) > 50


class TestFormFiller:
    """Tests for the Smart Form Filler module."""
    
    def test_import(self):
        """Test module can be imported."""
        from modules.form_filler import SmartFormFiller, VolunteerProfile
        assert SmartFormFiller is not None
        assert VolunteerProfile is not None
    
    def test_analyze_form(self):
        """Test form analysis."""
        from modules.form_filler import SmartFormFiller
        
        filler = SmartFormFiller()
        analysis = filler.analyze_form(None, 'screenshot')
        
        assert analysis.fields is not None
        assert len(analysis.fields) > 0
        assert analysis.overall_confidence > 0
    
    def test_auto_fill(self):
        """Test auto-fill functionality."""
        from modules.form_filler import SmartFormFiller, VolunteerProfile
        
        profile = VolunteerProfile(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            phone="555-123-4567"
        )
        
        filler = SmartFormFiller()
        analysis = filler.analyze_form(None, 'screenshot')
        result = filler.auto_fill(analysis, profile)
        
        assert 'filled' in result
        assert 'fill_rate' in result
        assert result['fill_rate'] > 0


class TestHoursTracker:
    """Tests for the Hours Tracker module."""
    
    def test_import(self):
        """Test module can be imported."""
        from modules.hours_tracker import HoursTracker, HoursStatus
        assert HoursTracker is not None
        assert HoursStatus is not None
    
    def test_log_hours(self):
        """Test hours logging."""
        from modules.hours_tracker import HoursTracker
        
        tracker = HoursTracker()
        entry = tracker.log_hours(
            volunteer_id="test-001",
            organization_id="test-org",
            organization_name="Test Organization",
            date="2024-01-15",
            hours=4,
            activity_type="direct_service",
            description="Test activity"
        )
        
        assert entry.id is not None
        assert entry.hours == 4
        assert entry.organization_name == "Test Organization"
    
    def test_get_summary(self):
        """Test summary generation."""
        from modules.hours_tracker import HoursTracker
        
        tracker = HoursTracker()
        tracker.log_hours(
            volunteer_id="test-001",
            organization_id="test-org",
            organization_name="Test Organization",
            date="2024-01-15",
            hours=4,
            activity_type="direct_service",
            description="Test activity"
        )
        
        summary = tracker.get_summary("test-001")
        
        assert summary.total_hours == 4
        assert summary.entries_count == 1
    
    def test_verify_hours(self):
        """Test hours verification."""
        from modules.hours_tracker import HoursTracker, HoursStatus
        
        tracker = HoursTracker()
        entry = tracker.log_hours(
            volunteer_id="test-001",
            organization_id="test-org",
            organization_name="Test Organization",
            date="2024-01-15",
            hours=4,
            activity_type="direct_service",
            description="Test activity"
        )
        
        tracker.verify_hours(entry.id, "verifier-001", True)
        
        assert entry.status == HoursStatus.VERIFIED


class TestCalendarIntegration:
    """Tests for the Calendar Integration module."""
    
    def test_import(self):
        """Test module can be imported."""
        from modules.calendar_integration import CalendarManager, CalendarEvent
        assert CalendarManager is not None
        assert CalendarEvent is not None
    
    def test_create_event(self):
        """Test event creation."""
        from modules.calendar_integration import CalendarManager
        
        manager = CalendarManager()
        event = manager.create_event(
            title="Test Event",
            start="2024-02-15T09:00:00",
            end="2024-02-15T13:00:00",
            description="Test description",
            location="Test Location"
        )
        
        assert event.id is not None
        assert event.title == "Test Event"
    
    def test_generate_ical(self):
        """Test iCal generation."""
        from modules.calendar_integration import CalendarManager
        
        manager = CalendarManager()
        manager.create_event(
            title="Test Event",
            start="2024-02-15T09:00:00",
            end="2024-02-15T13:00:00"
        )
        
        ical = manager.generate_ical()
        
        assert "BEGIN:VCALENDAR" in ical
        assert "BEGIN:VEVENT" in ical
        assert "Test Event" in ical
    
    def test_google_calendar_url(self):
        """Test Google Calendar URL generation."""
        from modules.calendar_integration import CalendarManager
        
        manager = CalendarManager()
        event = manager.create_event(
            title="Test Event",
            start="2024-02-15T09:00:00",
            end="2024-02-15T13:00:00"
        )
        
        url = manager.generate_google_calendar_url(event)
        
        assert "calendar.google.com" in url
        assert "Test" in url


class TestAGISelection:
    """Tests for AGI Selection system."""
    
    def test_import(self):
        """Test AGI selection module can be imported."""
        from agi_boards.volunteering_agi_selection import (
            VolunteeringAGISelector, AGI_DOMAINS
        )
        assert VolunteeringAGISelector is not None
        assert AGI_DOMAINS is not None
    
    def test_domain_definitions(self):
        """Test all required domains are defined."""
        from agi_boards.volunteering_agi_selection import AGI_DOMAINS
        
        required_domains = [
            'volunteer_planning',
            'volunteer_outreach',
            'volunteer_vetting',
            'volunteer_coordination',
            'volunteer_organizing',
            'volunteer_archiving',
            'ai_communication',
            'calendar_integration'
        ]
        
        for domain in required_domains:
            assert domain in AGI_DOMAINS
            assert 'description' in AGI_DOMAINS[domain]
            assert 'required_skills' in AGI_DOMAINS[domain]
            assert 'tests' in AGI_DOMAINS[domain]


class TestQualityTargets:
    """Tests for quality target achievement."""
    
    def test_letter_writer_quality(self):
        """Test letter writer meets quality targets."""
        from modules.letter_writer import generate_application_letter
        
        # Generate multiple letters and check average quality
        scores = []
        for _ in range(10):
            result = generate_application_letter(
                sender_name="Test User",
                organization="Test Org",
                role="Volunteer"
            )
            scores.append(result['quality_score'])
        
        avg_score = sum(scores) / len(scores)
        assert avg_score >= 0.85, f"Average quality {avg_score} below target"
    
    def test_form_filler_quality(self):
        """Test form filler meets quality targets."""
        from modules.form_filler import SmartFormFiller, VolunteerProfile
        
        profile = VolunteerProfile(
            first_name="Test",
            last_name="User",
            email="test@example.com"
        )
        
        filler = SmartFormFiller()
        analysis = filler.analyze_form(None, 'screenshot')
        
        assert analysis.overall_confidence >= 0.80


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
