import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import models  # registers all ORM models
from core.config import settings
from core.database import init_db
from routes import auth_router, mood_router, tasks_router, streak_router, analytics_router

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initialising database tables…")
    init_db()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="ADHD Mood-Based Productivity API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Error Handlers ────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " → ".join(str(e) for e in err["loc"] if e != "body")
        errors.append({"field": field, "message": err["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "detail": "Internal server error"},
    )


# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(mood_router)
app.include_router(tasks_router)
app.include_router(streak_router)
app.include_router(analytics_router)


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
