/**
 * My Requests Page Script
 * =======================
 * Displays all borrow requests made by the current user.
 * Allows returning borrowed items.
 */

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    setNavUserInfo();
    loadMyRequests();
});

// ============================================================
// LOAD MY REQUESTS
// ============================================================

async function loadMyRequests() {
    try {
        const requests = await apiRequest('/requests/my');
        displayMyRequests(requests);
    } catch (error) {
        showToast('Error loading requests', 'error');
    }
}

// ============================================================
// DISPLAY REQUESTS IN TABLE
// ============================================================

function displayMyRequests(requests) {
    const tbody = document.getElementById('requests-tbody');
    
    if (requests.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-muted">You haven't made any requests yet</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = requests.map(req => `
        <tr>
            <td><strong>${req.item_title}</strong></td>
            <td>${req.item_type}</td>
            <td>${req.owner_name}</td>
            <td><span class="badge ${getStatusBadgeClass(req.status)}">${req.status}</span></td>
            <td>${formatDate(req.borrow_date)}</td>
            <td>${formatDate(req.return_date)}</td>
            <td>
                ${req.status === 'Approved' ? 
                    `<button class="btn btn-sm btn-warning" onclick="returnItem(${req.id})">Return</button>` : 
                    '-'}
            </td>
        </tr>
    `).join('');
}

// ============================================================
// RETURN ITEM
// ============================================================

/**
 * Mark a borrowed item as returned
 * Updates both request status and item availability
 */
async function returnItem(requestId) {
    if (!confirm('Are you sure you want to return this item?')) return;
    
    try {
        await apiRequest(`/requests/${requestId}/return`, {
            method: 'PUT'
        });
        showToast('Item returned successfully!', 'success');
        loadMyRequests(); // Reload the table
    } catch (error) {
        showToast(error.message, 'error');
    }
}
