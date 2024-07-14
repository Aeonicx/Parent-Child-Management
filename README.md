# Parent Child Management System

The Parent-Child Management System is a comprehensive application built using FastAPI, PostgreSQL, and SQLAlchemy for ORM, designed to efficiently manage parent and child data. This system facilitates seamless user interaction and data handling through a well-structured RESTful API.

### Installation:

Install required packages using:

```bash
pip install -r requirements.txt
```

### Usage:

Create a .env file in the root of your project
```dosini
# Secret Key configuration
SECRET_KEY = "your_secret_key"

# Database configuration
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres

# Email configuration
EMAIL_HOST = sandbox.smtp.mailtrap.io
EMAIL_HOST_USER = user
EMAIL_HOST_PASSWORD = password
EMAIL_PORT = 587
```

### Migrate tables:

```bash
alembic upgrade head
```


### Running the Server:

```bash
uvicorn main:app --reload
```

### API Documentation:

```bash
http://127.0.0.1:8000/docs
```