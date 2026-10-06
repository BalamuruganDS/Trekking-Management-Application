TREKKING MANAGEMENT APPLICATION
================================

Project Overview
----------------
A full-stack Trekking Management Application built using Flask for the
backend and Vue.js for the frontend.

 The application helps manage trekking activities by providing separate functionalities for Admins, Trek Staff, and Trekkers.


TECHNOLOGY STACK
----------------
Backend:
- Python
- Flask
- Flask-SQLAlchemy
- SQLite

Frontend:
- Vue.js
- Vue Router

Database:
- SQLite
- SQLAlchemy ORM


PROJECT STRUCTURE
-----------------
backend/
    app.py              - Flask application entry point
    config.py           - Application configuration
    extensions.py       - Flask extension initialization
    models/             - Database models
    routes/             - API routes

frontend/
    src/
        components/     - Reusable Vue components
        views/          - Application pages
        router/         - Vue Router configuration
        store/          - Frontend state management
    index.html          - Frontend entry point

requirements.txt        - Backend dependencies
README.txt              - Project documentation


DATABASE
--------
The application uses three main database tables:

1. users
   Stores user accounts, roles, profile information, and staff details.

2. treks
   Stores trekking event information including location, difficulty,
   price, capacity, dates, status, and assigned staff.

3. bookings
   Stores trek reservations including user, trek, number of seats,
   booking status, payment status, and creation date.

Relationships:
- bookings.user_id -> users.id
- bookings.trek_id -> treks.id
- treks.assigned_staff_id -> users.id


USER ROLES
----------
Admin:
- Manage trekking events
- Manage staff
- Assign staff to treks
- View bookings
- Manage users
- View dashboard statistics

Staff:
- View assigned treks
- Update trek status
- Update available slots
- View registered participants

Trekker:
- Register and login
- Browse treks
- View trek details
- Book treks
- View booking history
- Cancel bookings
- Update profile


### Core API Endpoints

| Method            |     Endpoint   |                              | Description |
| :---              |   :---  | :--- |
| `POST`            | `/api/auth/register`                  | User registration |
| `POST`            | `/api/auth/login`                     | User/Staff/Admin login |
| `GET`             | `/api/admin/dashboard`                | View dashboard statistics |
| `GET` / `POST`    | `/api/admin/treks`                    | List all treks / Create a new trek |
| `PUT` / `DELETE`  | `/api/admin/treks/{id}`               | Update / Delete a trek |
| `GET` / `POST`    | `/api/admin/staff`                    | List staff / Register a new staff member |
| `GET`             | `/api/admin/bookings`                 | View all system bookings |
| `GET`             | `/api/staff/treks`                    | View assigned treks for logged-in staff |
| `PUT`             | `/api/staff/treks/{id}`               | Update trek status, slots, or info |
| `GET`             | `/api/staff/treks/{id}/participants`  | View trek participant roster |
| `GET`             | `/api/user/treks`                     | Browse available treks |
| `POST`            | `/api/user/book/{id}`                 | Book a trek |
| `GET`             | `/api/user/bookings`                  | View user booking history |
| `PUT`             | `/api/user/bookings/{id}/cancel`      | Cancel a booking |
| `PUT`             | `/api/user/profile`                   | Update user profile |


MAIN FEATURES
-------------
Authentication:
- User registration and login
- Secure password hashing
- Role-based access

Admin:
- Dashboard statistics
- Trek creation and management
- Staff management
- Staff assignment
- Booking management
- User management

Trek Staff:
- Assigned trek management
- Trek status updates
- Available slot updates
- Participant viewing

Trekker:
- Trek browsing
- Trek booking
- Booking history
- Booking cancellation
- Profile management


SECURITY
--------
- Passwords are stored using secure password hashing.
- Protected operations require authentication.
- Role-based authorization controls access to Admin, Staff,
  and Trekker functionality.
- Staff access is restricted to assigned trekking events.
- Trek capacity is checked before confirming bookings.


## RUNNING THE PROJECT

Backend:

    1. Open a terminal 1 in the backend/project directory.

    2. Create and activate a Python virtual environment if required.

    3. Install dependencies:

    pip install -r requirements.txt

    4. Start the Flask application:

    python app.py

    The backend normally runs on:

    http://127.0.0.1:5000

Frontend:

    1. Open another terminal 2 in the frontend directory.

    2. Install Node.js dependencies:

    npm install

    3. Start the Vue development server:

    npm run dev

    The exact frontend command may depend on the project's Vue/Vite setup.

    The Application runs in:

    http://localhost:5173/



Redis / Memurai:

    1. Redis/Memurai must be running before starting Celery.

    2. On Windows, check Redis/Memurai using:

    memurai-cli ping

    The expected output is:

     PONG

Celery Worker:

    1. Open another terminal 3 in the backend directory.

    2. Start the Celery Worker:

    python -m celery -A utils.celery_app.celery worker --loglevel=info --pool=solo

Celery Beat:

    1. Open another terminal 4 in the backend directory.

    2. Start Celery Beat:

    python -m celery -A utils.celery_app.celery beat --loglevel=info


The complete application requires the following services to be running:

   1. Redis / Memurai
   2. Flask Backend
   3. Vue Frontend
   4. Celery Worker
   5. Celery Beat

   

DATABASE
--------
The project uses SQLite with SQLAlchemy.

The database is created and managed through the Flask application and
SQLAlchemy models.


NOTES
-----
- The application uses a unified users table for Admin, Staff, and
  Trekker accounts.
- A staff member is assigned to a trek through assigned_staff_id.
- A booking connects a user and a trek.
- Booking date is represented by the booking model's created_at value.

