/**
 * VolunteerConnect Hub - Authentication Module
 * ============================================
 * Google OAuth authentication for the volunteering platform
 */

// Firebase Configuration
// Note: Replace with your actual Firebase config
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
        firebase.initializeApp(firebaseConfig);
        auth = firebase.auth();
        googleProvider = new firebase.auth.GoogleAuthProvider();
        
        // Listen for auth state changes
        auth.onAuthStateChanged(handleAuthStateChange);
    } else {
        console.log('Firebase not configured - using demo mode');
        // Demo mode - check for stored user
        const storedUser = localStorage.getItem('volunteerConnectUser');
        if (storedUser) {
            handleAuthStateChange(JSON.parse(storedUser));
        }
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
            showAuthError(error.message);
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

// Handle auth state changes
function handleAuthStateChange(user) {
    const loginBtn = document.getElementById('loginBtn');
    const userMenu = document.getElementById('userMenu');
    const userAvatar = document.getElementById('userAvatar');
    const userName = document.getElementById('userName');
    
    if (user) {
        // User is signed in
        if (loginBtn) loginBtn.classList.add('hidden');
        if (userMenu) userMenu.classList.remove('hidden');
        
        if (userAvatar) {
            userAvatar.src = user.photoURL || '/assets/images/default-avatar.png';
            userAvatar.alt = user.displayName || 'User';
        }
        
        if (userName) {
            userName.textContent = user.displayName || user.email;
        }
        
        // Update app state
        if (window.VolunteerConnect) {
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
        // User is signed out
        if (loginBtn) loginBtn.classList.remove('hidden');
        if (userMenu) userMenu.classList.add('hidden');
        
        if (window.VolunteerConnect) {
            window.VolunteerConnect.AppState.user = null;
        }
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('userSignedOut'));
    }
}

// Show demo login modal
function showDemoLogin() {
    const modalHtml = `
        <div class="modal-overlay active" id="demoLoginModal">
            <div class="modal">
                <div class="modal-header">
                    <h2 class="modal-title">Demo Login</h2>
                    <button class="modal-close" onclick="closeDemoLogin()">
                        <span class="material-icons">close</span>
                    </button>
                </div>
                <div class="modal-body">
                    <p style="margin-bottom: 16px;">Enter your details to try the demo:</p>
                    <div class="form-group">
                        <label class="form-label" for="demoName">Name</label>
                        <input type="text" class="form-input" id="demoName" placeholder="Your name">
                    </div>
                    <div class="form-group">
                        <label class="form-label" for="demoEmail">Email</label>
                        <input type="email" class="form-input" id="demoEmail" placeholder="your@email.com">
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-outline" onclick="closeDemoLogin()">Cancel</button>
                    <button class="btn btn-primary" onclick="completeDemoLogin()">Sign In</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

function closeDemoLogin() {
    const modal = document.getElementById('demoLoginModal');
    if (modal) modal.remove();
}

function completeDemoLogin() {
    const name = document.getElementById('demoName').value || 'Demo User';
    const email = document.getElementById('demoEmail').value || 'demo@volunteerconnect.app';
    
    const demoUser = {
        uid: 'demo-' + Date.now(),
        displayName: name,
        email: email,
        photoURL: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=4F46E5&color=fff`
    };
    
    localStorage.setItem('volunteerConnectUser', JSON.stringify(demoUser));
    handleAuthStateChange(demoUser);
    closeDemoLogin();
}

// Show auth error
function showAuthError(message) {
    const alertHtml = `
        <div class="alert alert-error" style="position: fixed; top: 80px; right: 20px; z-index: 3000; max-width: 400px;" id="authErrorAlert">
            <span class="material-icons">error</span>
            <div>
                <strong>Authentication Error</strong>
                <p>${message}</p>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    setTimeout(() => {
        const alert = document.getElementById('authErrorAlert');
        if (alert) alert.remove();
    }, 5000);
}

// Get current user
function getCurrentUser() {
    if (auth) {
        return auth.currentUser;
    }
    const stored = localStorage.getItem('volunteerConnectUser');
    return stored ? JSON.parse(stored) : null;
}

// Check if user is authenticated
function isAuthenticated() {
    return getCurrentUser() !== null;
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initializeFirebase);

// Export functions
window.signInWithGoogle = signInWithGoogle;
window.signOut = signOut;
window.getCurrentUser = getCurrentUser;
window.isAuthenticated = isAuthenticated;
