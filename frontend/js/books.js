/**
 * Books Page Script
 * =================
 * Handles:
 * - Loading and displaying all books
 * - Search and filter functionality
 * - Adding new books
 * - Requesting to borrow books
 */

// Store all books for client-side filtering
let allBooks = [];

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    setNavUserInfo();
    loadBooks();
});

// ============================================================
// LOAD BOOKS
// ============================================================

/**
 * Fetch all books from the API and display them
 */
async function loadBooks() {
    try {
        allBooks = await apiRequest('/books/');
        displayBooks(allBooks);
    } catch (error) {
        showToast('Error loading books', 'error');
    }
}

// ============================================================
// DISPLAY BOOKS
// ============================================================

/**
 * Render books as cards in the grid
 * @param {Array} books - Array of book objects to display
 */
function displayBooks(books) {
    const container = document.getElementById('books-grid');
    const user = getUser();
    
    if (books.length === 0) {
        container.innerHTML = '<p class="text-muted">No books found</p>';
        return;
    }
    
    container.innerHTML = books.map(book => `
        <div class="item-card">
            <div class="item-card-header">
                <span class="item-card-title">${book.title}</span>
                <span class="badge ${getStatusBadgeClass(book.status)}">${book.status}</span>
            </div>
            <div class="item-card-meta">
                ${book.author ? `<strong>Author:</strong> ${book.author}` : ''}
            </div>
            <div class="item-card-meta">
                ${book.subject ? `<strong>Subject:</strong> ${book.subject}` : ''}
            </div>
            <div class="item-card-footer">
                <span class="item-card-meta">Owner: ${book.owner_name}</span>
                <div>
                    ${book.status === 'Available' && book.owner_id !== user.id ? 
                        `<button class="btn btn-sm btn-primary" onclick="requestBook(${book.id})">Request</button>` : 
                        ''}
                    ${book.owner_id === user.id ? 
                        `<button class="btn btn-sm btn-danger" onclick="deleteBook(${book.id})">Delete</button>` : 
                        ''}
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================================
// SEARCH BOOKS
// ============================================================

/**
 * Filter books based on search input (title or author)
 */
function searchBooks() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const statusFilter = document.getElementById('status-filter').value;
    
    let filtered = allBooks.filter(book => 
        book.title.toLowerCase().includes(query) ||
        (book.author && book.author.toLowerCase().includes(query))
    );
    
    if (statusFilter) {
        filtered = filtered.filter(book => book.status === statusFilter);
    }
    
    displayBooks(filtered);
}

/**
 * Filter books by status
 */
function filterBooks() {
    searchBooks(); // Reuse search which also applies status filter
}

// ============================================================
// ADD BOOK
// ============================================================

/**
 * Show the add book modal
 */
function showAddBookModal() {
    document.getElementById('add-book-modal').classList.remove('hidden');
}

/**
 * Handle add book form submission
 */
async function handleAddBook(event) {
    event.preventDefault();
    
    const title = document.getElementById('book-title').value;
    const author = document.getElementById('book-author').value;
    const subject = document.getElementById('book-subject').value;
    
    try {
        await apiRequest('/books/', {
            method: 'POST',
            body: JSON.stringify({ title, author, subject })
        });
        
        showToast('Book added successfully!', 'success');
        closeModal('add-book-modal');
        
        // Clear form
        document.getElementById('book-title').value = '';
        document.getElementById('book-author').value = '';
        document.getElementById('book-subject').value = '';
        
        // Reload books
        loadBooks();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================
// REQUEST BOOK
// ============================================================

/**
 * Send a borrow request for a book
 */
async function requestBook(bookId) {
    try {
        await apiRequest('/requests/', {
            method: 'POST',
            body: JSON.stringify({ item_id: bookId, item_type: 'book' })
        });
        showToast('Request sent successfully!', 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================================
// DELETE BOOK
// ============================================================

/**
 * Delete a book (owner only)
 */
async function deleteBook(bookId) {
    if (!confirm('Are you sure you want to delete this book?')) return;
    
    try {
        await apiRequest(`/books/${bookId}`, { method: 'DELETE' });
        showToast('Book deleted successfully!', 'success');
        loadBooks();
    } catch (error) {
        showToast(error.message, 'error');
    }
}
