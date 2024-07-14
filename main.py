from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from authentication.routes import router as auth_router
from apps.parent.routes import router as parent_router
from apps.child.routes import router as child_router
from fastapi.openapi.utils import get_openapi
from common.scheduler import start_scheduler

app = FastAPI()


prefix = "/api"


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ParentChild Management",
        version="1.0.0",
        description="API Documentation for ParentChild Management System",
        routes=app.routes,
    )

    # Define security schemes for Bearer authentication
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    # Apply Bearer authentication to all routes
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Include routes
app.include_router(auth_router, prefix=f"{prefix}")
app.include_router(parent_router, prefix=f"{prefix}/parent")
app.include_router(child_router, prefix=f"{prefix}/child")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "detail": "An unexpected error occurred",
            "error": str(exc),
        },
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "detail": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
