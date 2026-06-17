from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.responses import AppError, ok, page
from app.core.security import decrypt_secret, encrypt_secret, mask_secret
from app.models import AIGenerationRecord, AIModelConfig, AIPromptTemplate, User
from app.schemas import (
    AIModelConfigCreate,
    AIModelConfigOut,
    AIModelConfigUpdate,
    DesensitizePreviewRequest,
    FinalOutputUpdate,
    GenerateReportRequest,
    GenerationRecordOut,
    PromptTemplateCreate,
    PromptTemplateOut,
    PromptTemplateUpdate,
)
from app.services.ai.desensitizer import preview_desensitization
from app.services.ai.providers import ProviderConfig, build_provider
from app.services.ai.report_generator import generate_report
from app.utils.serializers import dump, dump_list

router = APIRouter(prefix="/ai", tags=["ai"])


def _model_out(model: AIModelConfig) -> dict:
    api_key = decrypt_secret(model.api_key_encrypted)
    model._extra_response = {"api_key_masked": mask_secret(api_key)}
    return dump(AIModelConfigOut, model)


def _ensure_default_exclusive(db: Session, user_id: int, current_id: int | None = None):
    query = db.query(AIModelConfig).filter(AIModelConfig.created_by == user_id)
    if current_id:
        query = query.filter(AIModelConfig.id != current_id)
    for item in query.all():
        item.is_default = False
        db.add(item)


@router.get("/model-configs")
def list_model_configs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(AIModelConfig).filter(AIModelConfig.created_by == current_user.id).order_by(AIModelConfig.updated_at.desc()).all()
    return ok([_model_out(item) for item in items])


@router.post("/model-configs")
def create_model_config(payload: AIModelConfigCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.is_default:
        _ensure_default_exclusive(db, current_user.id)
    data = payload.model_dump(exclude={"api_key"})
    model = AIModelConfig(**data, api_key_encrypted=encrypt_secret(payload.api_key), created_by=current_user.id)
    db.add(model)
    db.commit()
    db.refresh(model)
    return ok(_model_out(model))


@router.put("/model-configs/{config_id}")
def update_model_config(
    config_id: int,
    payload: AIModelConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = db.query(AIModelConfig).filter(AIModelConfig.id == config_id, AIModelConfig.created_by == current_user.id).first()
    if not model:
        raise AppError("模型配置不存在", status_code=404)
    data = payload.model_dump(exclude_unset=True)
    api_key = data.pop("api_key", None)
    if data.get("is_default"):
        _ensure_default_exclusive(db, current_user.id, current_id=config_id)
    for key, value in data.items():
        setattr(model, key, value)
    if api_key is not None:
        model.api_key_encrypted = encrypt_secret(api_key)
    db.add(model)
    db.commit()
    db.refresh(model)
    return ok(_model_out(model))


@router.delete("/model-configs/{config_id}")
def delete_model_config(config_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = db.query(AIModelConfig).filter(AIModelConfig.id == config_id, AIModelConfig.created_by == current_user.id).first()
    if not model:
        raise AppError("模型配置不存在", status_code=404)
    db.delete(model)
    db.commit()
    return ok({"deleted": True})


@router.post("/model-configs/{config_id}/test")
async def test_model_config(config_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = db.query(AIModelConfig).filter(AIModelConfig.id == config_id, AIModelConfig.created_by == current_user.id).first()
    if not model:
        raise AppError("模型配置不存在", status_code=404)
    provider = build_provider(
        ProviderConfig(
            provider=model.provider,
            base_url=model.base_url,
            api_key=decrypt_secret(model.api_key_encrypted),
            model_name=model.model_name,
            temperature=model.temperature,
            max_tokens=min(model.max_tokens, 64),
            timeout_seconds=model.timeout_seconds,
        )
    )
    try:
        return ok(await provider.test())
    except Exception as exc:
        raise AppError(f"模型连接测试失败：{exc}", code=50001, status_code=502)


@router.get("/prompt-templates")
def list_prompt_templates(
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AIPromptTemplate).filter(
        (AIPromptTemplate.created_by.is_(None)) | (AIPromptTemplate.created_by == current_user.id)
    )
    if category:
        query = query.filter(AIPromptTemplate.category == category)
    items = query.order_by(AIPromptTemplate.is_default.desc(), AIPromptTemplate.updated_at.desc()).all()
    return ok(dump_list(PromptTemplateOut, items))


@router.post("/prompt-templates")
def create_prompt_template(payload: PromptTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.is_default:
        for item in db.query(AIPromptTemplate).filter(AIPromptTemplate.created_by == current_user.id).all():
            item.is_default = False
            db.add(item)
    template = AIPromptTemplate(**payload.model_dump(), created_by=current_user.id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return ok(dump(PromptTemplateOut, template))


@router.get("/prompt-templates/{template_id}")
def get_prompt_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = (
        db.query(AIPromptTemplate)
        .filter(AIPromptTemplate.id == template_id)
        .filter((AIPromptTemplate.created_by.is_(None)) | (AIPromptTemplate.created_by == current_user.id))
        .first()
    )
    if not template:
        raise AppError("Prompt 模板不存在", status_code=404)
    return ok(dump(PromptTemplateOut, template))


@router.put("/prompt-templates/{template_id}")
def update_prompt_template(
    template_id: int,
    payload: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = (
        db.query(AIPromptTemplate)
        .filter(AIPromptTemplate.id == template_id, AIPromptTemplate.created_by == current_user.id)
        .first()
    )
    if not template:
        raise AppError("只能编辑自己创建的 Prompt 模板", status_code=404)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    db.add(template)
    db.commit()
    db.refresh(template)
    return ok(dump(PromptTemplateOut, template))


@router.delete("/prompt-templates/{template_id}")
def delete_prompt_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    template = (
        db.query(AIPromptTemplate)
        .filter(AIPromptTemplate.id == template_id, AIPromptTemplate.created_by == current_user.id)
        .first()
    )
    if not template:
        raise AppError("只能删除自己创建的 Prompt 模板", status_code=404)
    db.delete(template)
    db.commit()
    return ok({"deleted": True})


async def _generate(report_type: str, payload: GenerateReportRequest, db: Session, current_user: User):
    options = payload.model_dump()
    record = await generate_report(
        db=db,
        user_id=current_user.id,
        report_type=report_type,
        date_start=payload.date_start,
        date_end=payload.date_end,
        template_id=payload.template_id,
        model_config_id=payload.model_config_id,
        options=options,
    )
    if record.status == "failed":
        return ok(dump(GenerationRecordOut, record), message=record.error_message or "AI 生成失败")
    return ok(dump(GenerationRecordOut, record))


@router.post("/reports/daily/generate")
async def generate_daily(payload: GenerateReportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await _generate("daily", payload, db, current_user)


@router.post("/reports/weekly/generate")
async def generate_weekly(payload: GenerateReportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await _generate("weekly", payload, db, current_user)


@router.post("/reports/monthly/generate")
async def generate_monthly(payload: GenerateReportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await _generate("monthly", payload, db, current_user)


@router.post("/reports/overtime/generate")
async def generate_overtime(payload: GenerateReportRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await _generate("overtime", payload, db, current_user)


@router.get("/generation-records")
def list_generation_records(
    report_type: str | None = None,
    page_number: int = Query(1, alias="page", ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AIGenerationRecord).filter(AIGenerationRecord.user_id == current_user.id)
    if report_type:
        query = query.filter(AIGenerationRecord.report_type == report_type)
    total = query.count()
    items = query.order_by(AIGenerationRecord.created_at.desc()).offset((page_number - 1) * page_size).limit(page_size).all()
    return page(dump_list(GenerationRecordOut, items), total, page_number, page_size)


@router.get("/generation-records/{record_id}")
def get_generation_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(AIGenerationRecord).filter(AIGenerationRecord.id == record_id, AIGenerationRecord.user_id == current_user.id).first()
    if not record:
        raise AppError("AI 生成记录不存在", status_code=404)
    return ok(dump(GenerationRecordOut, record))


@router.put("/generation-records/{record_id}/final-output")
def update_final_output(
    record_id: int,
    payload: FinalOutputUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(AIGenerationRecord).filter(AIGenerationRecord.id == record_id, AIGenerationRecord.user_id == current_user.id).first()
    if not record:
        raise AppError("AI 生成记录不存在", status_code=404)
    record.final_output = payload.final_output
    db.add(record)
    db.commit()
    db.refresh(record)
    return ok(dump(GenerationRecordOut, record))


@router.delete("/generation-records/{record_id}")
def delete_generation_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(AIGenerationRecord).filter(AIGenerationRecord.id == record_id, AIGenerationRecord.user_id == current_user.id).first()
    if not record:
        raise AppError("AI 生成记录不存在", status_code=404)
    db.delete(record)
    db.commit()
    return ok({"deleted": True})


@router.post("/desensitize/preview")
def desensitize_preview(payload: DesensitizePreviewRequest, current_user: User = Depends(get_current_user)):
    return ok(preview_desensitization(payload.text))
