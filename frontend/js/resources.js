/**
 * Resources Page Script
 * =====================
 * Handles:
 * - Loading and displaying all resources
 * - Search and filter by category/status
 * - Adding new resources
 * - Requesting to borrow resources
 */

// Store all resources for client-side filtering
let allResources = [];

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    setNavUserInfo();
    loadResources();
});

// ============================================================
// LOAD RESOURCES
// ============================================================

async function loadResources() {
    try {
        allResources = await apiRequest('/resources/');
        displayResources(allResources);
    } catch (error) {
        showToast('Error loading resources', 'error');
    }
}

// ============================================================
// DISPLAY RESOURCES
// ============================================================

function displayResources(resources) {
    const container = document.getElementById('resources-grid');
    const user = getUser();
    
    if (resources.length === 0) {
        container.innerHTML = '<p class="text-muted">No resources found</p>';
        return;
    }
    
    container.innerHTML = resources.map(resource => `
        <div class="item-card">
            <div class="item-card-header">
                <span class="item-card-title">${resource.title}</span>
                <span class="badge ${getStatusBadgeClass(resource.status)}">${resource.status}</span>
            </div>
            <div class="item-card-meta">
                <strong>Category:</strong> ${resource.category}
            </div>
            <div class="item-card-description">
                ${resource.description || 'No description provided'}
            </div>
            <div class="item-card-footer">
                <span class="item-card-meta">Owner: ${resource.owner_name}</span>
                <div>
                    ${resource.status === 'Available' && resource.owner_id !== user.id ? 
                        `<button class="btn btn-sm btn-primary" onclick="requestResource(${resource.id})">Request</button>` : 
                        ''}
                    ${resource.owner_id === user.id ? 
                        `<button class="btn btn-sm btn-danger" onclick="deleteResource(${resource.id})">Delete</button>` : 
                        ''}
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================================
// SEARCH & FILTER
// ============================================================

function searchResources() {
    applyFilters();
}

function filterResources() {
    applyFilters();
}

/**
 * Apply all active filters (search, category, status)
 */
function applyFilters() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const categoryFilter = document.getElementById('category-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    
    let filtered = allResources;
    
    // Search filter
    if (query) {
        filtered = filtered.filter(r => 
            r.title.toLowerCase().includes(query) ||
            (r.description && r.description.toLowerCase().includes(query))
        );
    }
    
    // Category filter
    if (categoryFilter) {
        filtered = filtered.filter(r => r.category === categoryFilter);
    }
    
    // Status filter
    if (statusFilter) {
        filtered = filtered.filter(r => r.status === statusFilter);
    }
    
    displayResources(filtered);
}

// ============================================================
// ADD RESOURCE
// ============================================================

function showAddResourceModal() {
    document.getElementById('add-resource-modal').classList.remove('hidden');
}

async function handleAddResource(event) {
    event.preventDefault();
    
    const title = document.getElementById('resource-title').value;
    const description = document.getElementById('resource-description').value;
    const category = document.getElementById('resource-category').value;
    
    try {
        await apiRequest('/resources/', {
            method: 'POST',
            body: JSON.stringify({ title, description, category })
        });
        
        showToast('Resource added successfully!', 'success');
        closeModal('add-resource-modal');
        
        // Clear form
        document.getElementById('resource-title').value = '';
        document.getElementById('resource-description').value = '';
        document.getElementById('resource-category').value = '';
        
        // Reload resources
        loadResources();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================
// REQUEST RESOURCE
// ============================================================

async function requestResource(resourceId) {
    try {
        await apiRequest('/requests/', {
            method: 'POST',
            body: JSON.stringify({ item_id: resourceId, item_type: 'resource' })
        });
        showToast('Request sent successfully!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================
// DELETE RESOURCE
// ============================================================

async function deleteResource(resourceId) {
    if (!confirm('Are you sure you want to delete this resource?')) return;
    
    try {
        await apiRequest(`/resources/${resourceId}`, { method: 'DELETE' });
        showToast('Resource deleted successfully!', 'success');
        loadResources();
    } catch (error) {
        showToast(error.message, 'error');
    }
}
