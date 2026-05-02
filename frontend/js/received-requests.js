/**
 * Received Requests Page Script
 * ==============================
 * Displays all borrow requests received for the user's items.
 * Allows owners to approve or reject pending requests.
 * Admin can see and manage all requests.
 */

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    setNavUserInfo();
    loadReceivedRequests();
});

// ============================================================
// LOAD RECEIVED REQUESTS
// ============================================================

async function loadReceivedRequests() {
    try {
        const requests = await apiRequest('/requests/received');
        displayReceivedRequests(requests);
    } catch (error) {
        showToast('Error loading requests', 'error');
    }
}

// ============================================================
// DISPLAY RECEIVED REQUESTS
// ============================================================

function displayReceivedRequests(requests) {
    const tbody = document.getElementById('received-tbody');
    
    if (requests.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-muted">No requests received</td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = requests.map(req => `
        <tr>
            <td><strong>${req.item_title}</strong></td>
            <td>${req.item_type}</td>
            <td>${req.requester_name}</td>
            <td><span class="badge ${getStatusBadgeClass(req.status)}">${req.status}</span></td>
            <td>${formatDate(req.created_at)}</td>
            <td>
                ${req.status === 'Pending' ? `
                    <button class="btn btn-sm btn-success" onclick="approveRequest(${req.id})">Approve</button>
                    <button class="btn btn-sm btn-danger" onclick="rejectRequest(${req.id})">Reject</button>
                ` : '-'}
            </td>
        </tr>
    `).join('');
}

// ============================================================
// APPROVE REQUEST
// ============================================================

/**
 * Approve a pending borrow request.
 * This will:
 * - Change request status to 'Approved'
 * - Change item status to 'Borrowed'
 * - Record the borrow date
 */
async function approveRequest(requestId) {
    try {
        await apiRequest(`/requests/${requestId}/action`, {
            method: 'PUT',
            body: JSON.stringify({ action: 'approve' })
        });
        showToast('Request approved!', 'success');
        loadReceivedRequests(); // Reload the table
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================
// REJECT REQUEST
// ============================================================

/**
 * Reject a pending borrow request.
 * This will change request status to 'Rejected'.
 * The item remains Available.
 */
async function rejectRequest(requestId) {
    if (!confirm('Are you sure you want to reject this request?')) return;
    
    try {
        await apiRequest(`/requests/${requestId}/action`, {
            method: 'PUT',
            body: JSON.stringify({ action: 'reject' })
        });
        showToast('Request rejected', 'info');
        loadReceivedRequests(); // Reload the table
    } catch (error) {
        showToast(error.message, 'error');
    }
}
