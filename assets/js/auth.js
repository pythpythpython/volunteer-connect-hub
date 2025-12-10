/**
 * VolunteerConnect Hub - Authentication Module
 * ============================================
 * Google OAuth authentication for the volunteering platform
 * 
 * Powered by AGI Board:
 * - UniteSee-G4: System integration for auth flows
 * - RetainGood-G4: User data management
 */

// Firebase Configuration - Replace with your own Firebase project config
const firebaseConfig = {
    apiKey: "YOUR_FIREBASE_API_KEY",
    authDomain: "volunteer-connect-hub.firebaseapp.com",
    projectId: "volunteer-connect-hub",
    storageBucket: "volunteer-connect-hub.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// Initialize Firebase (only if config is set)
let auth = null;
let googleProvider = null;

function initializeFirebase() {
    if (firebaseConfig.apiKey !== "YOUR_FIREBASE_API_KEY" && typeof firebase !== 'undefined') {
        try {
            firebase.initializeApp(firebaseConfig);
            auth = firebase.auth();
            googleProvider = new firebase.auth.GoogleAuthProvider();
            
            // Listen for auth state changes
            auth.onAuthStateChanged(handleAuthStateChange);
        } catch (error) {
            console.error('Firebase initialization error:', error);
            initializeDemoMode();
        }
    } else {
        console.log('Firebase not configured - using demo mode');
        initializeDemoMode();
    }
}

function initializeDemoMode() {
    // Demo mode - check for stored user
    const storedUser = localStorage.getItem('volunteerConnectUser');
    if (storedUser) {
        try {
            handleAuthStateChange(JSON.parse(storedUser));
        } catch (e) {
            localStorage.removeItem('volunteerConnectUser');
            handleAuthStateChange(null);
        }
    } else {
        handleAuthStateChange(null);
    }
}

// Sign in with Google
async function signInWithGoogle() {
    if (auth && googleProvider) {
        try {
            const result = await auth.signInWithPopup(googleProvider);
            console.log('Signed in:', result.user);
            return result.user;
        } catch (error) {
            console.error('Sign in error:', error);
            // If popup blocked or other error, try redirect
            if (error.code === 'auth/popup-blocked') {
                try {
                    await auth.signInWithRedirect(googleProvider);
                } catch (redirectError) {
                    showAuthError('Could not sign in. Please try again.');
                }
            } else {
                showAuthError(error.message);
            }
            return null;
        }
    } else {
        // Demo mode - show demo login
        showDemoLogin();
    }
}

// Sign out
async function signOut() {
    if (auth) {
        try {
            await auth.signOut();
            console.log('Signed out');
        } catch (error) {
            console.error('Sign out error:', error);
        }
    } else {
        // Demo mode
        localStorage.removeItem('volunteerConnectUser');
        handleAuthStateChange(null);
    }
}

// Handle auth state changes - MAIN UI UPDATE FUNCTION
function handleAuthStateChange(user) {
    // Core auth elements
    const loginBtn = document.getElementById('loginBtn');
    const userMenu = document.getElementById('userMenu');
    const userAvatar = document.getElementById('userAvatar');
    const userName = document.getElementById('userName');
    
    if (user) {
        // === USER IS SIGNED IN ===
        
        // Update nav auth elements
        if (loginBtn) loginBtn.classList.add('hidden');
        if (userMenu) userMenu.classList.remove('hidden');
        
        // Update avatar
        if (userAvatar) {
            userAvatar.src = user.photoURL || `https://ui-avatars.com/api/?name=${encodeURIComponent(user.displayName || 'U')}&background=4F46E5&color=fff`;
            userAvatar.alt = user.displayName || 'User';
        }
        
        // Update name
        if (userName) {
            userName.textContent = user.displayName || user.email || 'User';
        }
        
        // Update ALL elements with auth classes
        document.querySelectorAll('.auth-show-logged-out').forEach(el => {
            el.style.display = 'none';
        });
        document.querySelectorAll('.auth-show-logged-in').forEach(el => {
            el.style.display = '';
        });
        
        // Update app state
        if (window.VolunteerConnect && window.VolunteerConnect.AppState) {
            window.VolunteerConnect.AppState.user = {
                uid: user.uid,
                name: user.displayName,
                email: user.email,
                photoURL: user.photoURL
            };
        }
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('userSignedIn', { detail: user }));
        
    } else {
        // === USER IS SIGNED OUT ===
        
        // Update nav auth elements
        if (loginBtn) loginBtn.classList.remove('hidden');
        if (userMenu) userMenu.classList.add('hidden');
        
        // Update ALL elements with auth classes
        document.querySelectorAll('.auth-show-logged-out').forEach(el => {
            el.style.display = '';
        });
        document.querySelectorAll('.auth-show-logged-in').forEach(el => {
            el.style.display = 'none';
        });
        
        // Update app state
        if (window.VolunteerConnect && window.VolunteerConnect.AppState) {
            window.VolunteerConnect.AppState.user = null;
        }
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('userSignedOut'));
    }
}

// Show demo login modal
function showDemoLogin() {
    // Remove existing modal if any
    closeDemoLogin();
    
    const modalHtml = `
        <div class="modal-overlay active" id="demoLoginModal" onclick="if(event.target === this) closeDemoLogin()">
            <div class="modal" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2 class="modal-title">Sign In</h2>
                    <button class="modal-close" onclick="closeDemoLogin()">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info" style="margin-bottom: 16px;">
                        <span class="material-icons">info</span>
                        <span>This is a demo. Enter any name and email to try the app.</span>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="demoName">Name *</label>
                        <input type="text" class="form-input" id="demoName" placeholder="Your name" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="demoEmail">Email *</label>
                        <input type="email" class="form-input" id="demoEmail" placeholder="your@email.com" required>
                    </div>
                    <p style="font-size: 12px; color: var(--gray-500); margin-top: 16px;">
                        Your data is stored locally in your browser. Nothing is sent to any server.
                    </p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeDemoLogin()">Cancel</button>
                    <button class="btn btn-primary" onclick="completeDemoLogin()">
                        <span class="material-icons">login</span>
                        Sign In
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    document.body.style.overflow = 'hidden';
    
    // Focus name input
    setTimeout(() => {
        document.getElementById('demoName')?.focus();
    }, 100);
    
    // Handle enter key
    const handleEnter = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            completeDemoLogin();
        }
    };
    document.getElementById('demoName')?.addEventListener('keypress', handleEnter);
    document.getElementById('demoEmail')?.addEventListener('keypress', handleEnter);
}

function closeDemoLogin() {
    const modal = document.getElementById('demoLoginModal');
    if (modal) {
        modal.remove();
        document.body.style.overflow = '';
    }
}

function completeDemoLogin() {
    const nameInput = document.getElementById('demoName');
    const emailInput = document.getElementById('demoEmail');
    
    const name = nameInput?.value?.trim();
    const email = emailInput?.value?.trim();
    
    if (!name) {
        nameInput?.focus();
        showAuthError('Please enter your name');
        return;
    }
    
    if (!email) {
        emailInput?.focus();
        showAuthError('Please enter your email');
        return;
    }
    
    // Simple email validation
    if (!email.includes('@')) {
        emailInput?.focus();
        showAuthError('Please enter a valid email');
        return;
    }
    
    const demoUser = {
        uid: 'demo-' + Date.now(),
        displayName: name,
        email: email,
        photoURL: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=4F46E5&color=fff`
    };
    
    localStorage.setItem('volunteerConnectUser', JSON.stringify(demoUser));
    handleAuthStateChange(demoUser);
    closeDemoLogin();
    
    // Show success message
    showAuthSuccess(`Welcome, ${name}!`);
}

// Show auth error
function showAuthError(message) {
    // Remove existing error
    document.getElementById('authErrorAlert')?.remove();
    
    const alertHtml = `
        <div class="alert alert-error" style="position: fixed; top: 80px; right: 20px; z-index: 3000; max-width: 400px; animation: slideIn 0.3s ease;" id="authErrorAlert">
            <span class="material-icons">error</span>
            <div>
                <strong>Error</strong>
                <p style="margin: 0;">${message}</p>
            </div>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; cursor: pointer; padding: 4px;">
                <span class="material-icons" style="font-size: 18px;">close</span>
            </button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    setTimeout(() => {
        document.getElementById('authErrorAlert')?.remove();
    }, 5000);
}

// Show auth success
function showAuthSuccess(message) {
    const alertHtml = `
        <div class="alert alert-success" style="position: fixed; top: 80px; right: 20px; z-index: 3000; max-width: 400px; animation: slideIn 0.3s ease;" id="authSuccessAlert">
            <span class="material-icons">check_circle</span>
            <div>
                <strong>Success</strong>
                <p style="margin: 0;">${message}</p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    setTimeout(() => {
        document.getElementById('authSuccessAlert')?.remove();
    }, 3000);
}

// Get current user
function getCurrentUser() {
    if (auth) {
        return auth.currentUser;
    }
    const stored = localStorage.getItem('volunteerConnectUser');
    if (stored) {
        try {
            return JSON.parse(stored);
        } catch (e) {
            return null;
        }
    }
    return null;
}

// Check if user is authenticated
function isAuthenticated() {
    return getCurrentUser() !== null;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initializeFirebase);

// Export functions to global scope
window.signInWithGoogle = signInWithGoogle;
window.signOut = signOut;
window.getCurrentUser = getCurrentUser;
window.isAuthenticated = isAuthenticated;
