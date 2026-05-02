# 🎓 Campus Sharing and Resource Sharing System

A full-stack web application that allows students to share resources, books, and manage borrowing with proper approval workflows.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Database Design](#database-design)
5. [API Endpoints](#api-endpoints)
6. [Setup Instructions](#setup-instructions)
7. [Running the Application](#running-the-application)
8. [Features Walkthrough](#features-walkthrough)
9. [Request & Approval Workflow](#request--approval-workflow)
10. [Code Explanation (For Viva)](#code-explanation-for-viva)

---

## System Overview

The Campus Sharing System enables students and administrators to:
- **Share** books, notes, tools, and other resources
- **Request** items from other users
- **Approve/Reject** borrow requests
- **Track** borrowing status through the complete lifecycle
- **Search & Filter** available items

### User Roles
| Role | Permissions |
|------|-------------|
| **Student** | Add items, request items, approve/reject requests for own items, return items |
| **Admin** | All student permissions + manage all requests, see all data |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, FastAPI |
| Database | MySQL / SQLite (configurable) |
| ORM | SQLAlchemy |
| Authentication | JWT (JSON Web Tokens) |
| Password Hashing | bcrypt (via passlib) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| API Documentation | Swagger UI (auto-generated) |

---

## Project Structure

```
campus-sharing-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # Package initialization
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── database.py              # Database connection & session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── models.py            # SQLAlchemy ORM models
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py           # Pydantic validation schemas
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── resources.py         # Resources CRUD endpoints
│   │   │   ├── books.py             # Books CRUD endpoints
│   │   │   └── requests.py          # Request & approval endpoints
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── auth.py              # JWT & password utilities
│   └── requirements.txt             # Python dependencies
├── frontend/
│   ├── index.html                   # Login/Register page
│   ├── dashboard.html               # Main dashboard
│   ├── books.html                   # Books listing page
│   ├── resources.html               # Resources listing page
│   ├── my-requests.html             # User's sent requests
│   ├── received-requests.html       # Received requests (for approval)
│   ├── css/
│   │   └── style.css                # Complete stylesheet
│   └── js/
│       ├── api.js                   # API utility functions
│       ├── auth.js                  # Login/Register logic
│       ├── dashboard.js             # Dashboard logic
│       ├── books.js                 # Books page logic
│       ├── resources.js             # Resources page logic
│       ├── my-requests.js           # My requests logic
│       └── received-requests.js     # Received requests logic
├── database/
│   ├── schema.sql                   # MySQL table creation queries
│   └── sample_data.sql              # Sample data insertion
└── README.md                        # This file
```

---

## Database Design

### Entity-Relationship Diagram

```
┌──────────┐       ┌────────────┐       ┌──────────┐
│  users   │───┐   │  requests  │   ┌───│  books   │
├──────────┤   │   ├────────────┤   │   ├──────────┤
│ id (PK)  │   ├──▶│ owner_id   │   │   │ id (PK)  │
│ name     │   │   │ requester_id│◀──┤   │ title    │
│ email    │   │   │ item_id    │───┘   │ author   │
│ password │   │   │ item_type  │       │ subject  │
│ role     │   │   │ status     │       │ status   │
│ created_at│  │   │ borrow_date│       │ owner_id │──▶ users.id
└──────────┘   │   │ return_date│       └──────────┘
               │   └────────────┘
               │                        ┌────────────┐
               │                        │ resources  │
               │                        ├────────────┤
               └───────────────────────▶│ id (PK)    │
                                        │ title      │
                                        │ description│
                                        │ category   │
                                        │ status     │
                                        │ owner_id   │──▶ users.id
                                        └────────────┘
```

### Table Definitions

#### users
| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK, Auto) | Unique user identifier |
| name | VARCHAR(100) | Full name |
| email | VARCHAR(100) | Email (unique) |
| password | VARCHAR(255) | Bcrypt hashed password |
| role | VARCHAR(20) | 'student' or 'admin' |
| created_at | DATETIME | Registration timestamp |

#### resources
| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK, Auto) | Unique resource identifier |
| title | VARCHAR(200) | Resource title |
| description | TEXT | Detailed description |
| category | VARCHAR(100) | Category (Notes/Tools/Electronics/etc.) |
| status | VARCHAR(20) | 'Available' or 'Borrowed' |
| owner_id | INT (FK) | References users.id |
| created_at | DATETIME | Creation timestamp |

#### books
| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK, Auto) | Unique book identifier |
| title | VARCHAR(200) | Book title |
| author | VARCHAR(100) | Author name |
| subject | VARCHAR(100) | Subject area |
| status | VARCHAR(20) | 'Available' or 'Borrowed' |
| owner_id | INT (FK) | References users.id |
| created_at | DATETIME | Creation timestamp |

#### requests
| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK, Auto) | Unique request identifier |
| item_id | INT | ID of requested resource/book |
| item_type | VARCHAR(20) | 'resource' or 'book' |
| requester_id | INT (FK) | User requesting the item |
| owner_id | INT (FK) | Owner of the item |
| status | VARCHAR(20) | Pending/Approved/Rejected/Returned |
| borrow_date | DATETIME | When item was borrowed |
| return_date | DATETIME | When item was returned |
| created_at | DATETIME | Request creation timestamp |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user profile |

### Resources
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/resources/` | Get all resources (with search/filter) |
| GET | `/api/resources/my` | Get current user's resources |
| POST | `/api/resources/` | Add new resource |
| DELETE | `/api/resources/{id}` | Delete resource (owner only) |

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/` | Get all books (with search/filter) |
| GET | `/api/books/my` | Get current user's books |
| POST | `/api/books/` | Add new book |
| DELETE | `/api/books/{id}` | Delete book (owner only) |

### Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/requests/` | Create borrow request |
| GET | `/api/requests/my` | Get my sent requests |
| GET | `/api/requests/received` | Get received requests |
| PUT | `/api/requests/{id}/action` | Approve/Reject request |
| PUT | `/api/requests/{id}/return` | Return borrowed item |

---

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- MySQL (optional - SQLite used by default)

### Step 1: Clone/Download the Project
```bash
cd campus-sharing-system
```

### Step 2: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 3: Configure Database

**Option A: SQLite (Default - No setup needed)**
The application uses SQLite by default. A file `campus_sharing.db` will be created automatically.

**Option B: MySQL**
1. Create the database:
```sql
CREATE DATABASE campus_sharing;
```
2. Set the environment variable:
```bash
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/campus_sharing"
```
3. Optionally run the schema manually:
```bash
mysql -u username -p campus_sharing < database/schema.sql
mysql -u username -p campus_sharing < database/sample_data.sql
```

### Step 4: Run the Application
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 5: Access the Application
- **Web App**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---

## Running the Application

### Quick Start (Single Command)
```bash
cd campus-sharing-system/backend
pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Demo Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@campus.edu | admin123 |
| Student | john@campus.edu | student123 |

---

## Features Walkthrough

### 1. Login/Register
- Clean authentication page with tab switching
- Form validation and error messages
- JWT token stored in localStorage

### 2. Dashboard
- Welcome message with user name
- Statistics cards (total resources, books, my items, pending requests)
- Notifications section (approved/rejected/new requests)
- Recent available books and resources with request buttons

### 3. Books Page
- Grid display of all books
- Search by title or author
- Filter by status (Available/Borrowed)
- Add new book modal
- Request button for available books
- Delete button for owned books

### 4. Resources Page
- Grid display of all resources
- Search by title or description
- Filter by category and status
- Add new resource modal
- Request button for available resources

### 5. My Requests
- Table showing all requests made by the user
- Status tracking (Pending → Approved → Returned)
- Return button for approved (borrowed) items

### 6. Received Requests
- Table showing requests received for user's items
- Approve/Reject buttons for pending requests
- Admin can see all requests

---

## Request & Approval Workflow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User      │     │   System    │     │   Owner/    │     │   System    │
│   Requests  │────▶│   Creates   │────▶│   Admin     │────▶│   Updates   │
│   Item      │     │   Request   │     │   Reviews   │     │   Status    │
│             │     │   (Pending) │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                    ┌─────────┴─────────┐
                                    │                   │
                              ┌─────▼─────┐       ┌────▼──────┐
                              │  Approve  │       │  Reject   │
                              │           │       │           │
                              │ Item →    │       │ Item stays│
                              │ Borrowed  │       │ Available │
                              └─────┬─────┘       └───────────┘
                                    │
                              ┌─────▼─────┐
                              │  Return   │
                              │           │
                              │ Item →    │
                              │ Available │
                              └───────────┘
```

---

## Code Explanation (For Viva)

### Q: What is FastAPI?
**A:** FastAPI is a modern Python web framework for building APIs. It's fast, supports automatic documentation, and uses Python type hints for data validation.

### Q: What is SQLAlchemy ORM?
**A:** SQLAlchemy ORM (Object-Relational Mapping) allows us to interact with the database using Python classes instead of raw SQL queries. Each class maps to a database table.

### Q: How does JWT authentication work?
**A:** 
1. User logs in with email/password
2. Server verifies credentials and creates a JWT token containing the user_id
3. Token is sent to the client and stored in localStorage
4. For every subsequent request, the token is sent in the Authorization header
5. Server decodes the token to identify the user

### Q: How is the password stored securely?
**A:** We use bcrypt hashing (via passlib library). The password is never stored in plain text. When a user logs in, we hash the input password and compare it with the stored hash.

### Q: Explain the Request-Approval workflow.
**A:**
1. A user finds an available item and clicks "Request"
2. A new record is created in the `requests` table with status = "Pending"
3. The item owner sees the request in "Received Requests"
4. Owner clicks "Approve" → request status becomes "Approved", item status becomes "Borrowed"
5. Or owner clicks "Reject" → request status becomes "Rejected", item stays "Available"
6. When the borrower returns the item → request status becomes "Returned", item status becomes "Available"

### Q: What is CORS and why is it needed?
**A:** CORS (Cross-Origin Resource Sharing) is a security mechanism. Since our frontend and backend might run on different ports during development, CORS middleware allows the frontend to make API calls to the backend.

### Q: What is Pydantic?
**A:** Pydantic is used for data validation. We define schemas that specify what data an API endpoint expects (request body) and what it returns (response). It automatically validates incoming data and returns clear error messages.

### Q: How does the frontend communicate with the backend?
**A:** The frontend uses the JavaScript `fetch()` API to make HTTP requests to the backend REST endpoints. The JWT token is included in the Authorization header for authenticated requests.

### Q: What design pattern is used?
**A:** The application follows the **MVC (Model-View-Controller)** pattern:
- **Model**: SQLAlchemy models (database tables)
- **View**: HTML/CSS/JS frontend
- **Controller**: FastAPI routers (handle requests and business logic)

---

## License

This project is created for educational purposes (college project/viva).
