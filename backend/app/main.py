from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 — registers every model before any route touches the DB
from app.core.config import settings
from app.routes.v1.admin import router as admin_router
from app.routes.v1.ai import router as ai_router
from app.routes.v1.auth import router as auth_router
from app.routes.v1.batch import router as batch_router
from app.routes.v1.billing import router as billing_router
from app.routes.v1.billing import settings_router
from app.routes.v1.collaboration import router as collaboration_router
from app.routes.v1.creation import router as creation_router
from app.routes.v1.dashboard import router as dashboard_router
from app.routes.v1.editor import router as editor_router
from app.routes.v1.files import router as files_router
from app.routes.v1.organization import router as organization_router
from app.routes.v1.pdf import router as pdf_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Everything PDF. One Platform.",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

cors_origins = settings.cors_origins_list
allow_all = "*" in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=[] if allow_all else cors_origins,
    allow_origin_regex=".*" if allow_all else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(files_router, prefix=settings.API_V1_PREFIX)
app.include_router(pdf_router, prefix=settings.API_V1_PREFIX)
app.include_router(batch_router, prefix=settings.API_V1_PREFIX)
app.include_router(collaboration_router, prefix=settings.API_V1_PREFIX)
app.include_router(organization_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_router, prefix=settings.API_V1_PREFIX)
app.include_router(editor_router, prefix=settings.API_V1_PREFIX)
app.include_router(billing_router, prefix=settings.API_V1_PREFIX)
app.include_router(settings_router, prefix=settings.API_V1_PREFIX)
app.include_router(creation_router, prefix=settings.API_V1_PREFIX)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}
