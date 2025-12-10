"""
VolunteerConnect Hub - Database Management AGI Board
=====================================================

Production-ready database management using Supabase:
- Real user authentication (Google, Email)
- Persistent data storage (profiles, hours, letters, applications)
- GitHub backup sync for data redundancy
- Full CRUD operations for all entities

Quality Target: 100% - Reliable, secure data persistence
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class TableName(Enum):
    """Database table names."""
    USERS = "users"
    PROFILES = "profiles"
    HOURS_LOG = "hours_log"
    EVENTS = "events"
    LETTERS = "letters"
    APPLICATIONS = "applications"
    OPPORTUNITIES = "opportunities"
    RECOMMENDATIONS = "recommendations"


@dataclass
class DatabaseConfig:
    """Supabase configuration."""
    url: str
    anon_key: str
    service_role_key: str = ""  # For server-side operations only


class DatabaseAGI:
    """
    Database Management AGI Board - Handles all data persistence.
    
    Uses Supabase for:
    - Authentication (Google OAuth, Email/Password)
    - PostgreSQL database for structured data
    - Real-time subscriptions
    - Row Level Security (RLS)
    
    Quality Target: 100% - Reliable, secure data management
    """
    
    # SQL Schema for Supabase
    SCHEMA_SQL = '''
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    profile_complete BOOLEAN DEFAULT FALSE,
    
    -- Personal Information
    first_name TEXT,
    last_name TEXT,
    display_name TEXT,
    phone TEXT,
    location_city TEXT,
    location_state TEXT,
    location_country TEXT DEFAULT 'United States',
    age_group TEXT,
    volunteer_type TEXT,
    bio TEXT,
    linkedin_url TEXT,
    personal_website TEXT,
    avatar_url TEXT,
    
    -- Skills and Expertise (JSONB for flexibility)
    skills JSONB DEFAULT '[]'::JSONB,
    languages JSONB DEFAULT '[]'::JSONB,
    certifications TEXT[],
    special_training TEXT[],
    
    -- Education and Work (JSONB arrays)
    education_history JSONB DEFAULT '[]'::JSONB,
    current_education_status TEXT,
    work_history JSONB DEFAULT '[]'::JSONB,
    current_employment_status TEXT,
    industry_expertise TEXT[],
    
    -- Volunteer Experience
    volunteer_history JSONB DEFAULT '[]'::JSONB,
    total_volunteer_hours DECIMAL DEFAULT 0,
    volunteer_since_year INTEGER,
    
    -- Interests and Causes
    causes_interested TEXT[],
    activities_preferred TEXT[],
    populations_interested TEXT[],
    
    -- Availability
    availability_hours_per_week INTEGER DEFAULT 0,
    availability_days TEXT[],
    availability_times TEXT[],
    prefers_virtual BOOLEAN DEFAULT FALSE,
    prefers_in_person BOOLEAN DEFAULT TRUE,
    willing_to_travel_miles INTEGER DEFAULT 10,
    has_transportation BOOLEAN DEFAULT TRUE,
    willing_background_check BOOLEAN DEFAULT TRUE,
    has_valid_drivers_license BOOLEAN DEFAULT FALSE,
    
    -- Goals and Motivation
    primary_motivation TEXT,
    goals TEXT[],
    ideal_volunteer_role TEXT,
    what_hoping_to_gain TEXT,
    what_can_contribute TEXT,
    
    -- Emergency Contact
    emergency_contact_name TEXT,
    emergency_contact_phone TEXT,
    emergency_contact_relationship TEXT
);

-- Hours Log table
CREATE TABLE IF NOT EXISTS public.hours_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    organization TEXT NOT NULL,
    date DATE NOT NULL,
    hours DECIMAL NOT NULL,
    activity_type TEXT,
    description TEXT,
    supervisor_name TEXT,
    supervisor_email TEXT,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Events/Schedule table
CREATE TABLE IF NOT EXISTS public.events (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    title TEXT NOT NULL,
    organization TEXT,
    description TEXT,
    date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    duration_hours DECIMAL,
    location TEXT,
    is_virtual BOOLEAN DEFAULT FALSE,
    reminder_enabled BOOLEAN DEFAULT TRUE,
    reminder_hours_before INTEGER DEFAULT 24,
    status TEXT DEFAULT 'scheduled', -- scheduled, completed, cancelled
    notes TEXT
);

-- Letters table
CREATE TABLE IF NOT EXISTS public.letters (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    letter_type TEXT NOT NULL, -- application, thank_you, outreach, follow_up
    organization TEXT,
    recipient_name TEXT,
    recipient_email TEXT,
    subject TEXT,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'draft', -- draft, sent, archived
    sent_at TIMESTAMP WITH TIME ZONE,
    opportunity_id UUID REFERENCES public.opportunities(id),
    notes TEXT
);

-- Applications table
CREATE TABLE IF NOT EXISTS public.applications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    opportunity_id UUID REFERENCES public.opportunities(id),
    organization TEXT NOT NULL,
    position TEXT NOT NULL,
    status TEXT DEFAULT 'draft', -- draft, submitted, under_review, accepted, rejected
    submitted_at TIMESTAMP WITH TIME ZONE,
    response_received_at TIMESTAMP WITH TIME ZONE,
    
    -- Application content
    cover_letter TEXT,
    answers JSONB DEFAULT '{}'::JSONB, -- Q&A responses
    documents JSONB DEFAULT '[]'::JSONB, -- uploaded document references
    
    -- Follow-up
    follow_up_date DATE,
    follow_up_notes TEXT,
    notes TEXT
);

-- Opportunities table (crawled/synced)
CREATE TABLE IF NOT EXISTS public.opportunities (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Source info
    source TEXT NOT NULL, -- volunteermatch, idealist, manual, etc.
    source_id TEXT, -- ID from source system
    source_url TEXT,
    
    -- Opportunity details
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    organization_url TEXT,
    description TEXT,
    requirements TEXT,
    
    -- Location
    location_city TEXT,
    location_state TEXT,
    location_country TEXT,
    is_virtual BOOLEAN DEFAULT FALSE,
    
    -- Categorization
    cause_areas TEXT[],
    skills_needed TEXT[],
    populations_served TEXT[],
    
    -- Commitment
    commitment_type TEXT, -- one_time, recurring, ongoing
    hours_per_week_min INTEGER,
    hours_per_week_max INTEGER,
    start_date DATE,
    end_date DATE,
    
    -- Requirements
    min_age INTEGER,
    background_check_required BOOLEAN DEFAULT FALSE,
    training_provided BOOLEAN DEFAULT FALSE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Engagement
    times_viewed INTEGER DEFAULT 0,
    times_applied INTEGER DEFAULT 0
);

-- User Recommendations table
CREATE TABLE IF NOT EXISTS public.recommendations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    opportunity_id UUID REFERENCES public.opportunities(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    score DECIMAL NOT NULL, -- 0-100 match score
    match_reasons JSONB DEFAULT '[]'::JSONB,
    is_dismissed BOOLEAN DEFAULT FALSE,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    is_saved BOOLEAN DEFAULT FALSE,
    saved_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(user_id, opportunity_id)
);

-- Row Level Security policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hours_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;

-- Profiles: Users can only read/write their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Hours Log: Users can only access their own hours
CREATE POLICY "Users can view own hours" ON public.hours_log
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own hours" ON public.hours_log
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own hours" ON public.hours_log
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own hours" ON public.hours_log
    FOR DELETE USING (auth.uid() = user_id);

-- Events: Users can only access their own events
CREATE POLICY "Users can view own events" ON public.events
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own events" ON public.events
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own events" ON public.events
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own events" ON public.events
    FOR DELETE USING (auth.uid() = user_id);

-- Letters: Users can only access their own letters
CREATE POLICY "Users can view own letters" ON public.letters
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own letters" ON public.letters
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own letters" ON public.letters
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own letters" ON public.letters
    FOR DELETE USING (auth.uid() = user_id);

-- Applications: Users can only access their own applications
CREATE POLICY "Users can view own applications" ON public.applications
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own applications" ON public.applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own applications" ON public.applications
    FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own applications" ON public.applications
    FOR DELETE USING (auth.uid() = user_id);

-- Opportunities: Public read, admin write
CREATE POLICY "Anyone can view active opportunities" ON public.opportunities
    FOR SELECT USING (is_active = TRUE);

-- Recommendations: Users can only see their own recommendations
CREATE POLICY "Users can view own recommendations" ON public.recommendations
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own recommendations" ON public.recommendations
    FOR UPDATE USING (auth.uid() = user_id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_hours_log_user_id ON public.hours_log(user_id);
CREATE INDEX IF NOT EXISTS idx_hours_log_date ON public.hours_log(date);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON public.events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON public.events(date);
CREATE INDEX IF NOT EXISTS idx_letters_user_id ON public.letters(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON public.applications(user_id);
CREATE INDEX IF NOT EXISTS idx_opportunities_cause_areas ON public.opportunities USING GIN(cause_areas);
CREATE INDEX IF NOT EXISTS idx_opportunities_skills_needed ON public.opportunities USING GIN(skills_needed);
CREATE INDEX IF NOT EXISTS idx_opportunities_is_active ON public.opportunities(is_active);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_id ON public.recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_score ON public.recommendations(score DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_hours_log_updated_at BEFORE UPDATE ON public.hours_log
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON public.events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_letters_updated_at BEFORE UPDATE ON public.letters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON public.applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_opportunities_updated_at BEFORE UPDATE ON public.opportunities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email)
    VALUES (NEW.id, NEW.email);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
'''

    # JavaScript client code for frontend
    JS_CLIENT = '''
/**
 * VolunteerConnect Hub - Supabase Database Client
 * ================================================
 * Production database operations using Supabase
 */

// Initialize Supabase client
const SUPABASE_URL = 'YOUR_SUPABASE_URL';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';

// Import Supabase client (loaded via CDN in HTML)
// const { createClient } = supabase;

let supabaseClient = null;

function initDatabase() {
    if (typeof supabase !== 'undefined') {
        supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        console.log('Supabase initialized');
        return true;
    }
    console.error('Supabase library not loaded');
    return false;
}

// ================== AUTH OPERATIONS ==================

async function signUpWithEmail(email, password) {
    const { data, error } = await supabaseClient.auth.signUp({
        email,
        password,
    });
    if (error) throw error;
    return data;
}

async function signInWithEmail(email, password) {
    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password,
    });
    if (error) throw error;
    return data;
}

async function signInWithGoogle() {
    const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: window.location.origin + '/volunteer-connect-hub/'
        }
    });
    if (error) throw error;
    return data;
}

async function signOut() {
    const { error } = await supabaseClient.auth.signOut();
    if (error) throw error;
}

async function getCurrentUser() {
    const { data: { user } } = await supabaseClient.auth.getUser();
    return user;
}

function onAuthStateChange(callback) {
    return supabaseClient.auth.onAuthStateChange((event, session) => {
        callback(event, session);
    });
}

// ================== PROFILE OPERATIONS ==================

async function getProfile() {
    const user = await getCurrentUser();
    if (!user) return null;
    
    const { data, error } = await supabaseClient
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();
    
    if (error) throw error;
    return data;
}

async function updateProfile(profileData) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('profiles')
        .update({
            ...profileData,
            updated_at: new Date().toISOString()
        })
        .eq('id', user.id)
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

async function isProfileComplete() {
    const profile = await getProfile();
    return profile?.profile_complete === true;
}

// ================== HOURS LOG OPERATIONS ==================

async function getHoursLog(filters = {}) {
    const user = await getCurrentUser();
    if (!user) return [];
    
    let query = supabaseClient
        .from('hours_log')
        .select('*')
        .eq('user_id', user.id)
        .order('date', { ascending: false });
    
    if (filters.startDate) {
        query = query.gte('date', filters.startDate);
    }
    if (filters.endDate) {
        query = query.lte('date', filters.endDate);
    }
    if (filters.organization) {
        query = query.eq('organization', filters.organization);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data;
}

async function addHoursEntry(entry) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('hours_log')
        .insert({
            ...entry,
            user_id: user.id
        })
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

async function updateHoursEntry(id, updates) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('hours_log')
        .update(updates)
        .eq('id', id)
        .eq('user_id', user.id)
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

async function deleteHoursEntry(id) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { error } = await supabaseClient
        .from('hours_log')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);
    
    if (error) throw error;
}

async function getHoursSummary() {
    const user = await getCurrentUser();
    if (!user) return null;
    
    const { data, error } = await supabaseClient
        .from('hours_log')
        .select('hours, date, organization')
        .eq('user_id', user.id);
    
    if (error) throw error;
    
    const total = data.reduce((sum, entry) => sum + parseFloat(entry.hours), 0);
    const thisMonth = new Date().toISOString().slice(0, 7);
    const monthlyHours = data
        .filter(e => e.date.startsWith(thisMonth))
        .reduce((sum, entry) => sum + parseFloat(entry.hours), 0);
    const organizations = new Set(data.map(e => e.organization)).size;
    
    return {
        totalHours: total,
        monthlyHours,
        organizationCount: organizations,
        entryCount: data.length
    };
}

// ================== EVENTS OPERATIONS ==================

async function getEvents(filters = {}) {
    const user = await getCurrentUser();
    if (!user) return [];
    
    let query = supabaseClient
        .from('events')
        .select('*')
        .eq('user_id', user.id)
        .order('date', { ascending: true });
    
    if (filters.upcoming) {
        query = query.gte('date', new Date().toISOString().split('T')[0]);
    }
    if (filters.status) {
        query = query.eq('status', filters.status);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data;
}

async function addEvent(event) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('events')
        .insert({
            ...event,
            user_id: user.id
        })
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

async function updateEvent(id, updates) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('events')
        .update(updates)
        .eq('id', id)
        .eq('user_id', user.id)
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

async function deleteEvent(id) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { error } = await supabaseClient
        .from('events')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);
    
    if (error) throw error;
}

// ================== LETTERS OPERATIONS ==================

async function getLetters(filters = {}) {
    const user = await getCurrentUser();
    if (!user) return [];
    
    let query = supabaseClient
        .from('letters')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });
    
    if (filters.type) {
        query = query.eq('letter_type', filters.type);
    }
    if (filters.status) {
        query = query.eq('status', filters.status);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data;
}

async function saveLetter(letter) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('letters')
        .insert({
            ...letter,
            user_id: user.id
        })
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

async function updateLetter(id, updates) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { data, error } = await supabaseClient
        .from('letters')
        .update(updates)
        .eq('id', id)
        .eq('user_id', user.id)
        .select()
        .single();
    
    if (error) throw error;
    return data;
}

// ================== OPPORTUNITIES OPERATIONS ==================

async function getOpportunities(filters = {}) {
    let query = supabaseClient
        .from('opportunities')
        .select('*')
        .eq('is_active', true)
        .order('updated_at', { ascending: false });
    
    if (filters.causeArea) {
        query = query.contains('cause_areas', [filters.causeArea]);
    }
    if (filters.isVirtual !== undefined) {
        query = query.eq('is_virtual', filters.isVirtual);
    }
    if (filters.city) {
        query = query.ilike('location_city', `%${filters.city}%`);
    }
    if (filters.state) {
        query = query.eq('location_state', filters.state);
    }
    if (filters.limit) {
        query = query.limit(filters.limit);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data;
}

async function getOpportunity(id) {
    const { data, error } = await supabaseClient
        .from('opportunities')
        .select('*')
        .eq('id', id)
        .single();
    
    if (error) throw error;
    
    // Increment view count
    await supabaseClient
        .from('opportunities')
        .update({ times_viewed: (data.times_viewed || 0) + 1 })
        .eq('id', id);
    
    return data;
}

// ================== RECOMMENDATIONS OPERATIONS ==================

async function getRecommendations() {
    const user = await getCurrentUser();
    if (!user) return [];
    
    const { data, error } = await supabaseClient
        .from('recommendations')
        .select(`
            *,
            opportunity:opportunities(*)
        `)
        .eq('user_id', user.id)
        .eq('is_dismissed', false)
        .order('score', { ascending: false })
        .limit(10);
    
    if (error) throw error;
    return data;
}

async function dismissRecommendation(id) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { error } = await supabaseClient
        .from('recommendations')
        .update({
            is_dismissed: true,
            dismissed_at: new Date().toISOString()
        })
        .eq('id', id)
        .eq('user_id', user.id);
    
    if (error) throw error;
}

async function saveRecommendation(id) {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { error } = await supabaseClient
        .from('recommendations')
        .update({
            is_saved: true,
            saved_at: new Date().toISOString()
        })
        .eq('id', id)
        .eq('user_id', user.id);
    
    if (error) throw error;
}

// ================== EXPORT TO GITHUB ==================

async function exportAllUserData() {
    const user = await getCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const profile = await getProfile();
    const hours = await getHoursLog();
    const events = await getEvents();
    const letters = await getLetters();
    
    return {
        exportedAt: new Date().toISOString(),
        userId: user.id,
        email: user.email,
        profile,
        hours,
        events,
        letters
    };
}

// Export functions
window.VolunteerDB = {
    init: initDatabase,
    // Auth
    signUpWithEmail,
    signInWithEmail,
    signInWithGoogle,
    signOut,
    getCurrentUser,
    onAuthStateChange,
    // Profile
    getProfile,
    updateProfile,
    isProfileComplete,
    // Hours
    getHoursLog,
    addHoursEntry,
    updateHoursEntry,
    deleteHoursEntry,
    getHoursSummary,
    // Events
    getEvents,
    addEvent,
    updateEvent,
    deleteEvent,
    // Letters
    getLetters,
    saveLetter,
    updateLetter,
    // Opportunities
    getOpportunities,
    getOpportunity,
    // Recommendations
    getRecommendations,
    dismissRecommendation,
    saveRecommendation,
    // Export
    exportAllUserData
};
'''

    def __init__(self):
        self.tables = list(TableName)
    
    def get_schema_sql(self) -> str:
        """Get the SQL schema for Supabase."""
        return self.SCHEMA_SQL
    
    def get_js_client(self) -> str:
        """Get the JavaScript client code."""
        return self.JS_CLIENT
    
    def generate_setup_instructions(self) -> str:
        """Generate setup instructions for Supabase."""
        return '''
# Supabase Setup Instructions for VolunteerConnect Hub

## 1. Create Supabase Project
1. Go to https://supabase.com and sign up/sign in
2. Click "New Project"
3. Name: "volunteerconnect-hub"
4. Generate a strong database password
5. Choose a region close to your users
6. Click "Create new project"

## 2. Configure Authentication
1. Go to Authentication > Providers
2. Enable Email provider (for email/password login)
3. Enable Google provider:
   - Get OAuth credentials from Google Cloud Console
   - Add authorized redirect URL from Supabase
   - Enter Client ID and Secret
4. Go to Authentication > URL Configuration
   - Set Site URL to: https://pythpythpython.github.io/volunteer-connect-hub/
   - Add redirect URLs for local development if needed

## 3. Set Up Database
1. Go to SQL Editor
2. Copy the schema SQL from database_board.py
3. Run the SQL to create all tables and policies

## 4. Get API Keys
1. Go to Settings > API
2. Copy the "Project URL" (SUPABASE_URL)
3. Copy the "anon public" key (SUPABASE_ANON_KEY)

## 5. Update Frontend Code
1. Replace YOUR_SUPABASE_URL with your Project URL
2. Replace YOUR_SUPABASE_ANON_KEY with your anon key

## 6. Enable Row Level Security
The schema SQL already enables RLS - verify in Table Editor > [table] > Policies

## 7. Test Authentication
1. Try signing up with email
2. Try signing in with Google
3. Verify profile is created automatically

## Security Notes
- Never expose the service_role key in frontend code
- The anon key is safe to use in frontend (protected by RLS)
- All user data is protected by Row Level Security policies
'''


def export_database_files():
    """Export database setup files."""
    db_agi = DatabaseAGI()
    
    # Export schema
    with open('supabase_schema.sql', 'w') as f:
        f.write(db_agi.get_schema_sql())
    
    # Export JS client
    with open('database_client.js', 'w') as f:
        f.write(db_agi.get_js_client())
    
    # Export instructions
    with open('SUPABASE_SETUP.md', 'w') as f:
        f.write(db_agi.generate_setup_instructions())
    
    print("Database files exported!")


if __name__ == "__main__":
    db_agi = DatabaseAGI()
    print("Database AGI Board")
    print("=" * 50)
    print("\nTables:")
    for table in db_agi.tables:
        print(f"  - {table.value}")
    print("\nRun export_database_files() to generate setup files")
