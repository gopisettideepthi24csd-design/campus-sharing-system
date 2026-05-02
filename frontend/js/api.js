/**
 * API Utility Module
 * ==================
 * Provides helper functions for making API calls to the backend.
 * Handles authentication tokens, error handling, and common operations.
 */

// Base URL for API calls (same origin since served by FastAPI)
const API_BASE = '/api';

// ============================================================
// TOKEN MANAGEMENT
// ============================================================

/**
 * Get the stored JWT token from localStorage
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Get the stored user data from localStorage
 */
function getUser() {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
}

/**
 * Save token and user data to localStorage after login/register
 */
function saveAuth(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

/**
 * Clear all stored authentication data (logout)
 */
function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
}

/**
 * Check if user is authenticated, redirect to login if not
 */
function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/';
        return false;
    }
    return true;
}

// ============================================================
// API REQUEST HELPER
// ============================================================

/**
 * Make an authenticated API request
 * 
 * @param {string} endpoint - API endpoint (e.g., '/auth/login')
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise} - Response data or error
 */
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    
    // Set default headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    // Add authorization header if token exists
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        // Parse response
        const data = await response.json();
        
        // Handle unauthorized (token expired)
        if (response.status === 401) {
            clearAuth();
            window.location.href = '/';
            return null;
        }
        
        // Handle errors
        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ============================================================
// TOAST NOTIFICATION
// ============================================================

/**
 * Show a toast notification
 * 
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'info', 'warning'
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast toast-${type}`;
    
    // Show toast
    toast.classList.remove('hidden');
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// ============================================================
// MODAL HELPERS
// ============================================================

/**
 * Close a modal by ID
 */
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// ============================================================
// LOGOUT FUNCTION
// ============================================================

/**
 * Log out the current user and redirect to login page
 */
function logout() {
    clearAuth();
    window.location.href = '/';
}

// ============================================================
// UI HELPERS
// ============================================================

/**
 * Set user info in the navigation bar
 */
function setNavUserInfo() {
    const user = getUser();
    if (user) {
        const nameEl = document.getElementById('user-name');
        const roleEl = document.getElementById('user-role');
        if (nameEl) nameEl.textContent = user.name;
        if (roleEl) {
            roleEl.textContent = user.role;
            roleEl.classList.add(`badge-${user.role}`);
        }
    }
}

/**
 * Get the appropriate badge class for a status
 */
function getStatusBadgeClass(status) {
    const classes = {
        'Available': 'badge-available',
        'Borrowed': 'badge-borrowed',
        'Pending': 'badge-pending',
        'Approved': 'badge-approved',
        'Rejected': 'badge-rejected',
        'Returned': 'badge-returned'
    };
    return classes[status] || '';
}

/**
 * Format a date string for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}
