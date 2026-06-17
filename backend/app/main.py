from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.responses import error_response
from app.services.ai.report_generator import seed_prompt_templates


app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_seed():
    try:
        with SessionLocal() as db:
            seed_prompt_templates(db)
    except Exception:
        # Database may not be ready during tooling import; Docker entrypoint runs migrations before serving.
        pass


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        return error_response(exc.detail.get("code", exc.status_code), exc.detail.get("message", "请求失败"), exc.status_code)
    return error_response(exc.status_code, str(exc.detail), exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(40001, "参数错误", 422)


app.include_router(api_router)
