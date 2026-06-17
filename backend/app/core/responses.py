from typing import Any

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": 0, "message": message, "data": data}


def page(items: list[Any], total: int, page_number: int, page_size: int) -> dict[str, Any]:
    return ok({"items": items, "total": total, "page": page_number, "page_size": page_size})


class AppError(HTTPException):
    def __init__(self, message: str, code: int = 40001, status_code: int = 400):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})


def error_response(code: int, message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "data": None})
