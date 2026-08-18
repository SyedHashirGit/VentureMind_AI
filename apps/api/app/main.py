from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.services.firebase_service import init_firebase
from app.services.valkey_service import valkey
from app.services.semantic_cache import ensure_indexes
from app.routers import auth, workspaces, boardroom, sharktank, analytics, memory, timemachine


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_firebase()
    await valkey.connect()
    await ensure_indexes()  # create HNSW vector indexes if valkey-search is present
    yield
    await valkey.close()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="VentureMind AI API", version="0.7.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.cors_origins,
        allow_origin_regex=s.cors_origin_regex or None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    @app.get("/health")
    async def health():
        return {"status": "ok", "env": s.app_env}

    app.include_router(auth.router)
    app.include_router(workspaces.router)
    app.include_router(boardroom.router)
    app.include_router(sharktank.router)
    app.include_router(analytics.router)
    app.include_router(memory.router)
    app.include_router(timemachine.router)
    return app


app = create_app()
