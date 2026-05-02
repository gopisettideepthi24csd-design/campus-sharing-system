/**
 * Dashboard Page Script
 * =====================
 * Loads and displays:
 * - User stats (total resources, books, my items, pending requests)
 * - Recent available books and resources
 * - Notifications about request status changes
 */

// ============================================================
// INITIALIZATION
// ============================================================

// Check authentication and load data on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    setNavUserInfo();
    loadDashboardData();
});

// ============================================================
// LOAD DASHBOARD DATA
// ============================================================

/**
 * Load all dashboard data in parallel
 */
async function loadDashboardData() {
    const user = getUser();
    
    // Set welcome name
    document.getElementById('welcome-name').textContent = user.name;
    
    try {
        // Fetch all data in parallel for better performance
        const [resources, books, myRequests, receivedRequests] = await Promise.all([
            apiRequest('/resources/'),
            apiRequest('/books/'),
            apiRequest('/requests/my'),
            apiRequest('/requests/received')
        ]);
        
        // Update stats
        document.getElementById('stat-resources').textContent = resources.length;
        document.getElementById('stat-books').textContent = books.length;
        
        // Count my items (resources + books owned by current user)
        const myResources = resources.filter(r => r.owner_id === user.id);
        const myBooks = books.filter(b => b.owner_id === user.id);
        document.getElementById('stat-my-items').textContent = myResources.length + myBooks.length;
        
        // Count pending requests (received)
        const pendingRequests = receivedRequests.filter(r => r.status === 'Pending');
        document.getElementById('stat-pending').textContent = pendingRequests.length;
        
        // Display recent books (available only, max 4)
        const availableBooks = books.filter(b => b.status === 'Available').slice(0, 4);
        displayRecentBooks(availableBooks);
        
        // Display recent resources (available only, max 4)
        const availableResources = resources.filter(r => r.status === 'Available').slice(0, 4);
        displayRecentResources(availableResources);
        
        // Build notifications from requests
        buildNotifications(myRequests, receivedRequests);
        
    } catch (error) {
        showToast('Error loading dashboard data', 'error');
    }
}

// ============================================================
// DISPLAY RECENT BOOKS
// ============================================================

function displayRecentBooks(books) {
    const container = document.getElementById('recent-books');
    
    if (books.length === 0) {
        container.innerHTML = '<p class="text-muted">No books available</p>';
        return;
    }
    
    container.innerHTML = books.map(book => `
        <div class="item-card">
            <div class="item-card-header">
                <span class="item-card-title">${book.title}</span>
                <span class="badge ${getStatusBadgeClass(book.status)}">${book.status}</span>
            </div>
            <div class="item-card-meta">
                ${book.author ? `Author: ${book.author}` : ''}
                ${book.subject ? ` | Subject: ${book.subject}` : ''}
            </div>
            <div class="item-card-footer">
                <span class="item-card-meta">Owner: ${book.owner_name}</span>
                ${book.status === 'Available' && book.owner_id !== getUser().id ? 
                    `<button class="btn btn-sm btn-primary" onclick="requestItem(${book.id}, 'book')">Request</button>` : 
                    ''}
            </div>
        </div>
    `).join('');
}

// ============================================================
// DISPLAY RECENT RESOURCES
// ============================================================

function displayRecentResources(resources) {
    const container = document.getElementById('recent-resources');
    
    if (resources.length === 0) {
        container.innerHTML = '<p class="text-muted">No resources available</p>';
        return;
    }
    
    container.innerHTML = resources.map(resource => `
        <div class="item-card">
            <div class="item-card-header">
                <span class="item-card-title">${resource.title}</span>
                <span class="badge ${getStatusBadgeClass(resource.status)}">${resource.status}</span>
            </div>
            <div class="item-card-meta">Category: ${resource.category}</div>
            <div class="item-card-description">${resource.description || 'No description'}</div>
            <div class="item-card-footer">
                <span class="item-card-meta">Owner: ${resource.owner_name}</span>
                ${resource.status === 'Available' && resource.owner_id !== getUser().id ? 
                    `<button class="btn btn-sm btn-primary" onclick="requestItem(${resource.id}, 'resource')">Request</button>` : 
                    ''}
            </div>
        </div>
    `).join('');
}

// ============================================================
// BUILD NOTIFICATIONS
// ============================================================

function buildNotifications(myRequests, receivedRequests) {
    const container = document.getElementById('notifications-list');
    const notifications = [];
    
    // Notifications for my requests (status changes)
    myRequests.forEach(req => {
        if (req.status === 'Approved') {
            notifications.push({
                message: `Your request for "${req.item_title}" has been approved!`,
                time: req.borrow_date,
                type: 'success'
            });
        } else if (req.status === 'Rejected') {
            notifications.push({
                message: `Your request for "${req.item_title}" was rejected.`,
                time: req.created_at,
                type: 'error'
            });
        }
    });
    
    // Notifications for received requests (new pending)
    receivedRequests.filter(r => r.status === 'Pending').forEach(req => {
        notifications.push({
            message: `${req.requester_name} requested your "${req.item_title}"`,
            time: req.created_at,
            type: 'info'
        });
    });
    
    if (notifications.length === 0) {
        container.innerHTML = '<p class="text-muted">No new notifications</p>';
        return;
    }
    
    // Sort by time (most recent first) and show max 5
    notifications.sort((a, b) => new Date(b.time) - new Date(a.time));
    
    container.innerHTML = notifications.slice(0, 5).map(n => `
        <div class="notification-item">
            <span>${n.message}</span>
            <span class="time">${formatDate(n.time)}</span>
        </div>
    `).join('');
}

// ============================================================
// REQUEST ITEM (from dashboard)
// ============================================================

async function requestItem(itemId, itemType) {
    try {
        await apiRequest('/requests/', {
            method: 'POST',
            body: JSON.stringify({ item_id: itemId, item_type: itemType })
        });
        showToast('Request sent successfully!', 'success');
        // Reload dashboard data
        loadDashboardData();
    } catch (error) {
        showToast(error.message, 'error');
    }
}
