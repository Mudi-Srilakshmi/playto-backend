## Playto Engineering Challenge – Backend

This repository contains the backend implementation for the Playto Engineering Challenge.  
The project builds a community feed with threaded discussions, likes with karma, and a dynamic leaderboard using Django and Django REST Framework (DRF).

--------------------------------------------------

## TECH STACK

Backend: Django, Django REST Framework  
Database: SQLite (local development), PostgreSQL (production-ready)  
Authentication: Django Auth  
ORM: Django ORM  
Concurrency Handling: Database constraints and transactions

--------------------------------------------------

## FEATURES

### FEED
- Displays text-based posts
- Each post includes author, content, created timestamp, and like count

### THREADED COMMENTS (REDDIT-STYLE)
- Supports unlimited nested replies
- Implemented using a self-referential Comment model
- All comments for a post are fetched in a single query
- Comment tree is constructed in memory
- Avoids the N+1 query problem

### LIKES & KARMA SYSTEM
- Users can like posts (5 karma points)
- Users can like comments (1 karma point)
- Duplicate likes are prevented using database-level unique constraints
- Like operations are wrapped in atomic transactions

### LEADERBOARD (LAST 24 HOURS ONLY)
- Displays the top 5 users based on karma earned in the last 24 hours
- Karma is calculated dynamically from transaction history
- No cached or stored daily karma values

--------------------------------------------------

## CONCURRENCY & DATA INTEGRITY

- transaction.atomic() ensures safe concurrent operations
- select_for_update() prevents race conditions
- Database constraints guarantee one-like-per-user per post or comment
- Prevents karma inflation under concurrent requests

--------------------------------------------------

# LOCAL SETUP INSTRUCTIONS

### 1. Clone the repository
   git clone https://github.com/Mudi-Srilakshmi/playto-backend.git
   cd playto-backend

### 2. Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate   (Linux / macOS)
   venv\Scripts\activate      (Windows)

### 3. Install dependencies
   pip install -r requirements.txt

### 4. Run database migrations
   python manage.py makemigrations
   python manage.py migrate

### 5. Create superuser (optional)
   python manage.py createsuperuser

### 6. Run development server
   python manage.py runserver

### Application will be available at:
http://127.0.0.1:8000/

--------------------------------------------------

## API ENDPOINTS

### Feed
GET /api/posts/

### Post detail with nested comments
GET /api/posts/<post_id>/

### Like a post or comment
POST /api/like/

### Request body for post like:
{ "post_id": 1 }

### Request body for comment like:
{ "comment_id": 3 }

### Leaderboard (last 24 hours)
GET /api/leaderboard/

--------------------------------------------------

## DESIGN & ARCHITECTURE NOTES

- Nested comments use an adjacency list pattern
- Comment trees are built in memory to avoid recursive database queries
- Karma is tracked using immutable transaction records
- Leaderboard is computed using time-based aggregation queries
- Design prioritizes correctness, performance, and scalability

Detailed explanations are available in EXPLAINER.md.

--------------------------------------------------

## DOCUMENTATION

README.md – Project overview and setup instructions  
EXPLAINER.md – Detailed explanation of design decisions, queries, and AI audit

--------------------------------------------------

## AUTHOR

Srilakshmi Mudi
