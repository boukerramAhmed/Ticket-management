from fastapi import FastAPI,  Request, status
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.main import api_router
from app.config.settings import settings
from app.core.database.base import Base
from app.core.database.dependencies import engine
from typing import Callable
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
        except Exception:
            logger.exception(f"Unhandled exception for \
                {request.method} {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "detail": "Une erreur interne est survenue."
                },
            )


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
)
app.add_middleware(ExceptionHandlingMiddleware)


if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)
