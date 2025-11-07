# Munify API with FastAPI

A municipal funding platform API built with FastAPI and PostgreSQL.

## Features

- User management and authentication
- Organization management
- Project management
- Commitment tracking
- Document management
- PostgreSQL database integration
- RESTful API endpoints
- Automatic API documentation
- Alembic database migrations

## Project Structure

```
blog-project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # API router configuration
│   │       └── endpoints/      # API endpoints
│   │           ├── __init__.py
│   │           ├── posts.py    # Post-related endpoints
│   │           ├── users.py    # User-related endpoints
│   │           └── comments.py # Comment-related endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   └── database.py         # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLAlchemy model
│   │   ├── post.py             # Post SQLAlchemy model
│   │   └── comment.py          # Comment SQLAlchemy model
│   └── schemas/
│       ├── __init__.py
│       ├── user.py             # User Pydantic schemas
│       ├── post.py             # Post Pydantic schemas
│       └── comment.py          # Comment Pydantic schemas
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
├── database_init.py           # Database initialization script
├── run.py                     # Application runner
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 12 or higher installed and running
- PostgreSQL user with database creation privileges

### 1. Clone the Repository

```bash
git clone <repository-url>
cd blog-project
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update with your PostgreSQL credentials:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file and update PostgreSQL credentials:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=munify_db
```

**Note:** The default password in `config.py` is `"root"`. If your PostgreSQL password is different, update `.env` file.

### 5. Database Setup (Automatic)

Alembic will automatically create the database and all tables when you run migrations:

```bash
alembic upgrade head
```

This command will:
- ✅ Create the PostgreSQL database if it doesn't exist
- ✅ Create all tables based on SQLAlchemy models
- ✅ Apply all migrations

**No manual database creation needed!**

### 6. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- **Interactive API docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints

### Users
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `POST /api/v1/users/` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Posts
- `GET /api/v1/posts/` - Get all posts (with status filter)
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `POST /api/v1/posts/` - Create new post
- `PUT /api/v1/posts/{post_id}` - Update post
- `DELETE /api/v1/posts/{post_id}` - Delete post

### Comments
- `GET /api/v1/comments/` - Get all comments (with status filter)
- `GET /api/v1/comments/post/{post_id}` - Get comments for a post
- `GET /api/v1/comments/{comment_id}` - Get comment by ID
- `POST /api/v1/comments/` - Create new comment
- `PUT /api/v1/comments/{comment_id}` - Update comment
- `DELETE /api/v1/comments/{comment_id}` - Delete comment

## Environment Variables

See `.env.example` for all available environment variables. Key variables:

```env
# PostgreSQL Configuration (Required)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=munify_db

# Application Settings
PROJECT_NAME=Munify API
VERSION=0.1.0
API_V1_STR=/api/v1
DEBUG=true
APP_ENV=dev

# Server Configuration
HOST=127.0.0.1
PORT=8000

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173
```

## Development

The application uses:
- **FastAPI** for the web framework
- **SQLAlchemy 2.0** for ORM
- **PostgreSQL** as the database
- **psycopg** for PostgreSQL database connection
- **Alembic** for database migrations
- **Pydantic** for data validation
- **Passlib** for password hashing
- **Uvicorn** as the ASGI server

## Database Migrations

This project uses Alembic for database migrations. The database is automatically created when you run migrations.

### Common Migration Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration version
alembic current

# Show migration history
alembic history
```

**Note:** The `alembic/env.py` file automatically creates the database if it doesn't exist, so you don't need to manually create it.

## Quick Start for New Developers

After cloning the repository:

1. **Create virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   copy .env.example .env  # Windows
   # Edit .env with your PostgreSQL credentials
   ```

3. **Initialize database (automatic):**
   ```bash
   alembic upgrade head
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

That's it! The database will be created automatically, and all tables will be set up.

## Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running: `pg_isready` or check PostgreSQL service
- Verify credentials in `.env` file match your PostgreSQL setup
- Check if PostgreSQL user has database creation privileges

### Migration Issues

- If migrations fail, check PostgreSQL connection settings
- Ensure you're using the correct virtual environment
- Run `alembic current` to check migration status
