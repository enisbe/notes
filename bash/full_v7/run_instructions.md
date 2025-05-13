# Credit Risk Data API - Full Version

This directory contains a FastAPI application for managing credit risk data, including Obligors, Facilities, and their associated Ratings and Profiles.

## Project Structure

```
app/db/playgroud/full_v5/
├── .gitignore          # (Recommended) Git ignore file
├── crud.py             # Contains CRUD (Create, Read, Update, Delete) database operations
├── database.py         # Database engine setup and session management
├── db_instructions.md  # Original schema and requirements for this project
├── instructions.md     # This file: How to run and understand the project
├── main.py             # FastAPI application, endpoints, and main logic
├── models.py           # SQLAlchemy ORM models (database table definitions)
├── populate_db.py      # Script to populate the database with initial sample data
├── schemas.py          # Pydantic models for data validation and serialization
└── playground_full.db  # SQLite database file (will be created on first run)
```

## Prerequisites

*   Python 3.7+
*   pip (Python package installer)

## Setup and Installation

1.  **Navigate to the backend root directory:**
    Make sure your terminal is in the `/backend` directory (the parent of `app`).

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate it:
    *   Windows: `venv\Scripts\activate`
    *   macOS/Linux: `source venv/bin/activate`

3.  **Install dependencies:**
    Create a `requirements.txt` file in the `app/db/playgroud/full/` directory (or at the project root `backend/`) with the following content:

    ```txt
    fastapi
    uvicorn[standard]
    sqlalchemy
    pydantic
    # Add other dependencies if any were introduced
    ```
    Then install them:
    ```bash
    pip install -r app/db/playgroud/full/requirements.txt 
    # Or if requirements.txt is at backend/
    # pip install -r requirements.txt 
    ```
    *(Note: If you already have a `requirements.txt` at the `backend/` level that includes these, you can skip creating a new one here and just ensure it's up-to-date.)*


## Running the Application

1.  **Ensure tables are created and database is populated (first time):**
    The `main.py` script automatically calls `models.Base.metadata.create_all(bind=engine)` which creates the database tables if they don't exist based on `models.py`.

    To populate the database with initial sample data, run the `populate_db.py` script. From the `backend/` directory:
    ```bash
    python -m app.db.playgroud.full.populate_db
    ```
    Or, navigate to `app/db/playgroud/full/` and run:
    ```bash
    python populate_db.py
    ```
    This will create `playground_full.db` if it doesn't exist and fill it with data as specified in `db_instructions.md`.

2.  **Start the FastAPI server:**
    From the `backend/` directory:
    ```bash
    uvicorn app.db.playgroud.full.main:app --reload --host 0.0.0.0 --port 8000
    ```
    Alternatively, if your current working directory is `app/db/playgroud/full/`:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    The `--reload` flag makes the server restart automatically after code changes.

3.  **Access the API:**
    Once the server is running, you can access the API documentation (Swagger UI) in your browser at:
    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

    You can also access the alternative ReDoc documentation at:
    [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Key Files Overview

*   **`models.py`**: Defines the database structure using SQLAlchemy ORM. Each class represents a table.
*   **`schemas.py`**: Defines data shapes for API requests and responses using Pydantic. This ensures data validation.
*   **`crud.py`**: Contains functions to interact with the database (Create, Read, Update, Delete operations). Separates database logic from API endpoint logic.
*   **`database.py`**: Configures the database connection (SQLite in this case) and provides session management for database interactions.
*   **`main.py`**: The main entry point of the FastAPI application. It defines API routes (endpoints) and uses functions from `crud.py` and `schemas.py` to handle requests.
*   **`populate_db.py`**: A utility script to fill the database with sample data. Useful for development and testing.
*   **`db_instructions.md`**: The original requirements document detailing the data model and desired functionality.

## Database

*   The application uses SQLite, and the database file is `playground_full.db`, created in the `app/db/playgroud/full/` directory.
*   Database table creation is handled automatically when `main.py` starts or when `populate_db.py` is run.

## Further Development

*   **Migrations**: For a production environment or more complex schema changes, consider using a database migration tool like Alembic.
*   **Error Handling**: Enhance error handling and validation logic in API endpoints and CRUD functions.
*   **Testing**: Implement unit and integration tests.
*   **Constraint `1` from `db_instructions.md`**: The constraint "ORR_RATING and LRR_RATING have rating_records but they must be tied to the same obligor" is not fully enforced at the point of individual rating creation yet. This would typically be handled by:
    *   A more complex service layer function that creates a `RatingRecord` along with its LRR and ORR ratings, ensuring consistency.
    *   Validation logic within the `RatingRecord` creation process if LRR/ORR are passed in.
*   **Update/Delete Operations**: The current `crud.py` primarily focuses on Create and Read. Update and Delete functions can be added as needed. 