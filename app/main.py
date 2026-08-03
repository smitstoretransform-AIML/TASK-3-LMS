from app.models import members
from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import engine
from app.core.exception_handlers import register_exception_handlers
from app.utils.response import api_response

from app.routers import auth
from app.routers import books
from app.routers import users
from app.routers import members

app = FastAPI(title="Library Management System")

# Register global exception handlers
register_exception_handlers(app)


@app.get("/")
def root():
    return api_response(
        code=200,
        status="Success",
        message="Library Management API is running",
        data=None
    )


@app.get("/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return api_response(
            code=200,
            status="Success",
            message="Database connected successfully",
            data={
                "database": "connected"
            }
        )

    except Exception as e:
        return api_response(
            code=500,
            status="Error",
            message=str(e),
            data=None
        )


# Register routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(users.router)
app.include_router(members.router)