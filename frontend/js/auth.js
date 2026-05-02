/**
 * Authentication Page Script
 * ==========================
 * Handles login and registration form submissions.
 * Manages tab switching between login and register views.
 */

// ============================================================
// CHECK IF ALREADY LOGGED IN
// ============================================================

// If user is already authenticated, redirect to dashboard
(function() {
    const token = localStorage.getItem('token');
    if (token) {
        window.location.href = '/dashboard';
    }
})();

// ============================================================
// TAB SWITCHING
// ============================================================

/**
 * Switch between Login and Register tabs
 * @param {string} tab - 'login' or 'register'
 */
function showTab(tab) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    // Hide all forms
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.add('hidden');
    
    // Show selected form
    if (tab === 'login') {
        document.getElementById('login-form').classList.remove('hidden');
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
    } else {
        document.getElementById('register-form').classList.remove('hidden');
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
    }
    
    // Clear any messages
    hideMessage();
}

// ============================================================
// LOGIN HANDLER
// ============================================================

/**
 * Handle login form submission
 * Sends credentials to API and stores token on success
 */
async function handleLogin(event) {
    event.preventDefault();  // Prevent form from reloading page
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        // Make API call to login endpoint
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showMessage(data.detail || 'Login failed', 'error');
            return;
        }
        
        // Store token and user data
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
        
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    }
}

// ============================================================
// REGISTER HANDLER
// ============================================================

/**
 * Handle registration form submission
 * Creates new user account and logs them in
 */
async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const role = document.getElementById('reg-role').value;
    
    try {
        // Make API call to register endpoint
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, role })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showMessage(data.detail || 'Registration failed', 'error');
            return;
        }
        
        // Store token and user data (auto-login after registration)
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
        
    } catch (error) {
        showMessage('Network error. Please try again.', 'error');
    }
}

// ============================================================
// MESSAGE DISPLAY HELPERS
// ============================================================

/**
 * Show a message below the form
 */
function showMessage(text, type) {
    const msgEl = document.getElementById('auth-message');
    msgEl.textContent = text;
    msgEl.className = `message message-${type}`;
    msgEl.classList.remove('hidden');
}

/**
 * Hide the message
 */
function hideMessage() {
    const msgEl = document.getElementById('auth-message');
    msgEl.classList.add('hidden');
}
