from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.responses import ok
from app.models import User

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("")
def list_teams(current_user: User = Depends(get_current_user)):
    return ok(
        [
            {
                "id": None,
                "name": "个人空间",
                "description": "第一版默认个人空间，团队协作字段已预留。",
                "role": "admin",
            }
        ]
    )
