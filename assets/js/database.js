/**
 * VolunteerConnect Hub - Database Client
 * ======================================
 * Supabase integration for production data persistence
 * 
 * SETUP INSTRUCTIONS:
 * 1. Create a Supabase project at https://supabase.com
 * 2. Run the SQL schema from agi_boards/database_board.py
 * 3. Replace the URL and key below with your project's values
 * 4. Enable Google OAuth in Supabase Authentication settings
 * 
 * See SUPABASE_SETUP.md for detailed instructions.
 */

// ============================================
// CONFIGURATION - Replace with your Supabase project details
// ============================================
const SUPABASE_URL = 'YOUR_SUPABASE_URL';  // e.g., https://xxxxx.supabase.co
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY';

// ============================================
// DATABASE CLIENT
// ============================================

let supabaseClient = null;
let dbInitialized = false;

/**
 * Initialize the Supabase client
 */
function initDatabase() {
    // Check if Supabase is configured
    if (SUPABASE_URL === 'YOUR_SUPABASE_URL' || SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
        console.log('Supabase not configured - using localStorage fallback');
        dbInitialized = false;
        return false;
    }
    
    // Check if Supabase library is loaded
    if (typeof supabase === 'undefined') {
        console.error('Supabase library not loaded');
        dbInitialized = false;
        return false;
    }
    
    try {
        supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
        dbInitialized = true;
        console.log('Supabase database initialized');
        
        // Set up auth state listener
        supabaseClient.auth.onAuthStateChange((event, session) => {
            handleSupabaseAuthChange(event, session);
        });
        
        return true;
    } catch (error) {
        console.error('Error initializing Supabase:', error);
        dbInitialized = false;
        return false;
    }
}

/**
 * Check if database is available (Supabase configured)
 */
function isDatabaseAvailable() {
    return dbInitialized && supabaseClient !== null;
}

// ============================================
// AUTHENTICATION
// ============================================

async function dbSignInWithGoogle() {
    if (!isDatabaseAvailable()) {
        // Fallback to demo login
        showDemoLogin();
        return;
    }
    
    const { data, error } = await supabaseClient.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: window.location.origin + '/volunteer-connect-hub/'
        }
    });
    
    if (error) {
        console.error('Google sign in error:', error);
        showAuthError(error.message);
    }
}

async function dbSignInWithEmail(email, password) {
    if (!isDatabaseAvailable()) {
        throw new Error('Database not configured');
    }
    
    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password
    });
    
    if (error) throw error;
    return data;
}

async function dbSignUpWithEmail(email, password) {
    if (!isDatabaseAvailable()) {
        throw new Error('Database not configured');
    }
    
    const { data, error } = await supabaseClient.auth.signUp({
        email,
        password
    });
    
    if (error) throw error;
    return data;
}

async function dbSignOut() {
    if (!isDatabaseAvailable()) {
        // Clear local storage
        localStorage.removeItem('volunteerConnectUser');
        localStorage.removeItem('volunteerProfile');
        handleAuthStateChange(null);
        return;
    }
    
    const { error } = await supabaseClient.auth.signOut();
    if (error) console.error('Sign out error:', error);
}

async function dbGetCurrentUser() {
    if (!isDatabaseAvailable()) {
        const stored = localStorage.getItem('volunteerConnectUser');
        return stored ? JSON.parse(stored) : null;
    }
    
    const { data: { user } } = await supabaseClient.auth.getUser();
    return user;
}

function handleSupabaseAuthChange(event, session) {
    if (session?.user) {
        const user = {
            uid: session.user.id,
            email: session.user.email,
            displayName: session.user.user_metadata?.full_name || session.user.email?.split('@')[0],
            photoURL: session.user.user_metadata?.avatar_url
        };
        handleAuthStateChange(user);
    } else {
        handleAuthStateChange(null);
    }
}

// ============================================
// PROFILE OPERATIONS
// ============================================

async function dbGetProfile() {
    if (!isDatabaseAvailable()) {
        return JSON.parse(localStorage.getItem('volunteerProfile') || 'null');
    }
    
    const user = await dbGetCurrentUser();
    if (!user) return null;
    
    const { data, error } = await supabaseClient
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single();
    
    if (error) {
        console.error('Error fetching profile:', error);
        return null;
    }
    
    return data;
}

async function dbUpdateProfile(profileData) {
    if (!isDatabaseAvailable()) {
        // Save to localStorage
        const existing = JSON.parse(localStorage.getItem('volunteerProfile') || '{}');
        const updated = { ...existing, ...profileData, updated_at: new Date().toISOString() };
        localStorage.setItem('volunteerProfile', JSON.stringify(updated));
        return updated;
    }
    
    const user = await dbGetCurrentUser();
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

async function dbIsProfileComplete() {
    const profile = await dbGetProfile();
    return profile?.profile_complete === true;
}

// ============================================
// HOURS LOG OPERATIONS
// ============================================

async function dbGetHoursLog(filters = {}) {
    if (!isDatabaseAvailable()) {
        const hours = JSON.parse(localStorage.getItem('volunteerHoursLog') || '[]');
        // Apply filters
        let filtered = hours;
        if (filters.startDate) {
            filtered = filtered.filter(h => h.date >= filters.startDate);
        }
        if (filters.endDate) {
            filtered = filtered.filter(h => h.date <= filters.endDate);
        }
        return filtered;
    }
    
    const user = await dbGetCurrentUser();
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
    
    const { data, error } = await query;
    if (error) throw error;
    return data || [];
}

async function dbAddHoursEntry(entry) {
    if (!isDatabaseAvailable()) {
        const hours = JSON.parse(localStorage.getItem('volunteerHoursLog') || '[]');
        const newEntry = {
            ...entry,
            id: Date.now().toString(),
            created_at: new Date().toISOString()
        };
        hours.push(newEntry);
        localStorage.setItem('volunteerHoursLog', JSON.stringify(hours));
        return newEntry;
    }
    
    const user = await dbGetCurrentUser();
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

async function dbDeleteHoursEntry(id) {
    if (!isDatabaseAvailable()) {
        let hours = JSON.parse(localStorage.getItem('volunteerHoursLog') || '[]');
        hours = hours.filter(h => h.id !== id);
        localStorage.setItem('volunteerHoursLog', JSON.stringify(hours));
        return;
    }
    
    const user = await dbGetCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { error } = await supabaseClient
        .from('hours_log')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);
    
    if (error) throw error;
}

// ============================================
// EVENTS OPERATIONS
// ============================================

async function dbGetEvents(filters = {}) {
    if (!isDatabaseAvailable()) {
        let events = JSON.parse(localStorage.getItem('volunteerEvents') || '[]');
        if (filters.upcoming) {
            const today = new Date().toISOString().split('T')[0];
            events = events.filter(e => e.date >= today);
        }
        return events;
    }
    
    const user = await dbGetCurrentUser();
    if (!user) return [];
    
    let query = supabaseClient
        .from('events')
        .select('*')
        .eq('user_id', user.id)
        .order('date', { ascending: true });
    
    if (filters.upcoming) {
        query = query.gte('date', new Date().toISOString().split('T')[0]);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data || [];
}

async function dbAddEvent(event) {
    if (!isDatabaseAvailable()) {
        const events = JSON.parse(localStorage.getItem('volunteerEvents') || '[]');
        const newEvent = {
            ...event,
            id: Date.now().toString(),
            created_at: new Date().toISOString()
        };
        events.push(newEvent);
        localStorage.setItem('volunteerEvents', JSON.stringify(events));
        return newEvent;
    }
    
    const user = await dbGetCurrentUser();
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

async function dbDeleteEvent(id) {
    if (!isDatabaseAvailable()) {
        let events = JSON.parse(localStorage.getItem('volunteerEvents') || '[]');
        events = events.filter(e => e.id !== id);
        localStorage.setItem('volunteerEvents', JSON.stringify(events));
        return;
    }
    
    const user = await dbGetCurrentUser();
    if (!user) throw new Error('Not authenticated');
    
    const { error } = await supabaseClient
        .from('events')
        .delete()
        .eq('id', id)
        .eq('user_id', user.id);
    
    if (error) throw error;
}

// ============================================
// LETTERS OPERATIONS
// ============================================

async function dbGetLetters(filters = {}) {
    if (!isDatabaseAvailable()) {
        return JSON.parse(localStorage.getItem('volunteerLetters') || '[]');
    }
    
    const user = await dbGetCurrentUser();
    if (!user) return [];
    
    let query = supabaseClient
        .from('letters')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });
    
    if (filters.type) {
        query = query.eq('letter_type', filters.type);
    }
    
    const { data, error } = await query;
    if (error) throw error;
    return data || [];
}

async function dbSaveLetter(letter) {
    if (!isDatabaseAvailable()) {
        const letters = JSON.parse(localStorage.getItem('volunteerLetters') || '[]');
        const newLetter = {
            ...letter,
            id: Date.now().toString(),
            created_at: new Date().toISOString()
        };
        letters.push(newLetter);
        localStorage.setItem('volunteerLetters', JSON.stringify(letters));
        return newLetter;
    }
    
    const user = await dbGetCurrentUser();
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

// ============================================
// OPPORTUNITIES (Public data)
// ============================================

async function dbGetOpportunities(filters = {}) {
    // Always try to get from Supabase for latest data
    if (isDatabaseAvailable()) {
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
        if (filters.limit) {
            query = query.limit(filters.limit);
        }
        
        const { data, error } = await query;
        if (!error && data) {
            return data;
        }
    }
    
    // Fallback to static JSON file
    try {
        const response = await fetch('/volunteer-connect-hub/data/opportunities.json');
        const data = await response.json();
        return data.opportunities || [];
    } catch (error) {
        console.error('Error loading opportunities:', error);
        return [];
    }
}

// ============================================
// DATA EXPORT
// ============================================

async function dbExportAllUserData() {
    const profile = await dbGetProfile();
    const hours = await dbGetHoursLog();
    const events = await dbGetEvents();
    const letters = await dbGetLetters();
    
    return {
        exportedAt: new Date().toISOString(),
        profile,
        hours,
        events,
        letters
    };
}

// ============================================
// INITIALIZE
// ============================================

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    initDatabase();
});

// Export to global scope
window.VolunteerDB = {
    init: initDatabase,
    isAvailable: isDatabaseAvailable,
    // Auth
    signInWithGoogle: dbSignInWithGoogle,
    signInWithEmail: dbSignInWithEmail,
    signUpWithEmail: dbSignUpWithEmail,
    signOut: dbSignOut,
    getCurrentUser: dbGetCurrentUser,
    // Profile
    getProfile: dbGetProfile,
    updateProfile: dbUpdateProfile,
    isProfileComplete: dbIsProfileComplete,
    // Hours
    getHoursLog: dbGetHoursLog,
    addHoursEntry: dbAddHoursEntry,
    deleteHoursEntry: dbDeleteHoursEntry,
    // Events
    getEvents: dbGetEvents,
    addEvent: dbAddEvent,
    deleteEvent: dbDeleteEvent,
    // Letters
    getLetters: dbGetLetters,
    saveLetter: dbSaveLetter,
    // Opportunities
    getOpportunities: dbGetOpportunities,
    // Export
    exportAllData: dbExportAllUserData
};
