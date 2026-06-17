from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.models import AIGenerationRecord, User, WorkLog
from app.schemas import GenerationRecordOut
from app.services.report_service import excel_bytes, markdown_bytes, pdf_bytes, word_bytes
from app.utils.serializers import dump_list

router = APIRouter(prefix="/reports", tags=["reports"])


def _records(report_type: str, db: Session, user: User, page_number: int, page_size: int):
    query = db.query(AIGenerationRecord).filter(AIGenerationRecord.user_id == user.id, AIGenerationRecord.report_type == report_type)
    total = query.count()
    items = query.order_by(AIGenerationRecord.created_at.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page(dump_list(GenerationRecordOut, items), total, page_number, page_size)


@router.get("/daily")
def daily(page_number: int = Query(1, alias="page"), page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _records("daily", db, current_user, page_number, page_size)


@router.get("/weekly")
def weekly(page_number: int = Query(1, alias="page"), page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _records("weekly", db, current_user, page_number, page_size)


@router.get("/monthly")
def monthly(page_number: int = Query(1, alias="page"), page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _records("monthly", db, current_user, page_number, page_size)


@router.get("/overtime")
def overtime(page_number: int = Query(1, alias="page"), page_size: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _records("overtime", db, current_user, page_number, page_size)


@router.get("/work-hours")
def work_hours(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(WorkLog).filter(WorkLog.user_id == current_user.id).order_by(WorkLog.work_date.desc()).all()
    total = round(sum(row.duration_hours or 0 for row in logs), 2)
    return ok({"total_hours": total, "count": len(logs)})


@router.get("/export")
def export_report(
    record_id: int | None = None,
    format: str = "markdown",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if record_id:
        record = db.query(AIGenerationRecord).filter(AIGenerationRecord.id == record_id, AIGenerationRecord.user_id == current_user.id).first()
        if not record:
            raise AppError("报表不存在", status_code=404)
        content = record.final_output or record.ai_output or ""
        filename = f"worklog_{record.report_type}_{record.date_start}_{record.date_end}"
        if format == "excel":
            data = excel_bytes([{"content": line} for line in content.splitlines()])
            media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            suffix = "xlsx"
        elif format == "word":
            data = word_bytes("WorkLog AI 报表", content)
            media = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            suffix = "docx"
        elif format == "pdf":
            data = pdf_bytes("WorkLog AI 报表", content)
            media = "application/pdf"
            suffix = "pdf"
        else:
            data = markdown_bytes(content)
            media = "text/markdown; charset=utf-8"
            suffix = "md"
    else:
        logs = db.query(WorkLog).filter(WorkLog.user_id == current_user.id).order_by(WorkLog.work_date.desc()).all()
        rows = [
            {
                "日期": row.work_date.isoformat(),
                "标题": row.title,
                "类型": row.work_type,
                "时长": row.duration_hours,
                "内容": row.content,
                "结果": row.result,
            }
            for row in logs
        ]
        data = excel_bytes(rows)
        media = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "worklog_hours"
        suffix = "xlsx"
    return Response(
        content=data,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{filename}.{suffix}"'},
    )
