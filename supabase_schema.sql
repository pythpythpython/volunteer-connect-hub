-- VolunteerConnect Hub - Supabase Database Schema
-- ================================================
-- Run this SQL in Supabase SQL Editor to set up the database
-- 
-- IMPORTANT: Run this ENTIRE script at once. Tables are ordered correctly
-- to handle foreign key dependencies.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- STEP 1: Create tables WITHOUT foreign key dependencies first
-- ============================================

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

-- Opportunities table (NO foreign key dependencies - create early)
CREATE TABLE IF NOT EXISTS public.opportunities (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Source info
    source TEXT NOT NULL,
    source_id TEXT,
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
    commitment_type TEXT,
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

-- ============================================
-- STEP 2: Create tables that depend on profiles only
-- ============================================

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
    status TEXT DEFAULT 'scheduled',
    notes TEXT
);

-- ============================================
-- STEP 3: Create tables that depend on both profiles AND opportunities
-- ============================================

-- Letters table (depends on profiles and opportunities)
CREATE TABLE IF NOT EXISTS public.letters (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    letter_type TEXT NOT NULL,
    organization TEXT,
    recipient_name TEXT,
    recipient_email TEXT,
    subject TEXT,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    sent_at TIMESTAMP WITH TIME ZONE,
    opportunity_id UUID REFERENCES public.opportunities(id) ON DELETE SET NULL,
    notes TEXT
);

-- Applications table (depends on profiles and opportunities)
CREATE TABLE IF NOT EXISTS public.applications (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    opportunity_id UUID REFERENCES public.opportunities(id) ON DELETE SET NULL,
    organization TEXT NOT NULL,
    position TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    submitted_at TIMESTAMP WITH TIME ZONE,
    response_received_at TIMESTAMP WITH TIME ZONE,
    
    cover_letter TEXT,
    answers JSONB DEFAULT '{}'::JSONB,
    documents JSONB DEFAULT '[]'::JSONB,
    
    follow_up_date DATE,
    follow_up_notes TEXT,
    notes TEXT
);

-- Recommendations table (depends on profiles and opportunities)
CREATE TABLE IF NOT EXISTS public.recommendations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    opportunity_id UUID REFERENCES public.opportunities(id) ON DELETE CASCADE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    score DECIMAL NOT NULL,
    match_reasons JSONB DEFAULT '[]'::JSONB,
    is_dismissed BOOLEAN DEFAULT FALSE,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    is_saved BOOLEAN DEFAULT FALSE,
    saved_at TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(user_id, opportunity_id)
);

-- ============================================
-- STEP 4: Enable Row Level Security
-- ============================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hours_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.letters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;

-- ============================================
-- STEP 5: Create RLS Policies
-- ============================================

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

-- Opportunities: Anyone can view active opportunities (public data)
CREATE POLICY "Anyone can view active opportunities" ON public.opportunities
    FOR SELECT USING (is_active = TRUE);

-- Recommendations: Users can only see their own recommendations
CREATE POLICY "Users can view own recommendations" ON public.recommendations
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own recommendations" ON public.recommendations
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================
-- STEP 6: Create Indexes for Performance
-- ============================================

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

-- ============================================
-- STEP 7: Create Functions and Triggers
-- ============================================

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
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- DONE! All tables, policies, and triggers created.
-- ============================================
