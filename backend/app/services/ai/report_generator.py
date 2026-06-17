from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decrypt_secret
from app.models import AIGenerationRecord, AIModelConfig, AIPromptTemplate, Attachment, OvertimeLog, Project, Task, WorkLog
from app.services.ai.desensitizer import classify_security_work, desensitize_text, normalize_security_terms
from app.services.ai.prompt_renderer import render_prompt
from app.services.ai.providers import ProviderConfig, build_provider


DEFAULT_SYSTEM_PROMPT = """你是一名网络安全运营周报助手，擅长整理 WAF、API 安全、蜜罐、态势感知、告警分析、重保值守、攻防演练、工单处理、站点接入、策略优化、巡检和报表输出类工作内容。

要求：
1. 不得编造用户未提供的工作内容。
2. 不得夸大工作成果。
3. 对重复事项进行合并。
4. 保留安全运营相关专业表达。
5. 输出内容正式、简洁、适合工作汇报。
6. 如果要求只写干了什么，不要写原因、背景、意义和结果。
"""

DEFAULT_USER_PROMPT = """请根据以下工作记录生成本周周报。

【输出要求】
- 输出格式：{output_format}
- 编号格式：{number_style}
- 是否按分类输出：{group_by_category}
- 是否只写干了什么：{only_work_items}
- 是否包含加班情况：{include_overtime}
- 是否包含下周计划：{include_next_week_plan}

【本周工作记录】
{work_logs}

【本周任务记录】
{tasks}

【本周加班记录】
{overtime_logs}

【本周项目记录】
{projects}

【手动补充内容】
{manual_extra_content}
"""


def seed_prompt_templates(db: Session) -> None:
    if db.query(AIPromptTemplate).count() > 0:
        return
    templates = [
        ("个人简洁周报", "personal_simple", "weekly", "通用个人周报"),
        ("安全运营简洁周报", "security_simple", "weekly", "只写本周完成事项，适合复制到企业微信、钉钉、邮件或内部系统。"),
        ("安全运营正式周报", "security_formal", "weekly", "安全运营正式汇报版，按类别组织。"),
        ("团队工作周报", "team_weekly", "weekly", "团队工作量汇总模板，预留团队场景。"),
        ("加班说明生成", "overtime_reason", "overtime", "根据加班记录生成说明。"),
        ("工作记录润色", "polish_worklog", "polish", "润色原始工作记录。"),
        ("原始记录归类版", "raw_classified", "weekly", "按安全运营分类归纳原始事项。"),
        ("领导汇报版", "leader_report", "weekly", "面向管理层的简洁正式汇报。"),
    ]
    for index, (name, code, category, description) in enumerate(templates):
        db.add(
            AIPromptTemplate(
                name=name,
                code=code,
                category=category,
                description=description,
                system_prompt=DEFAULT_SYSTEM_PROMPT,
                user_prompt=DEFAULT_USER_PROMPT,
                output_format="markdown",
                work_domain="security_operations",
                is_default=index == 1,
                created_by=None,
            )
        )
    db.commit()


def _record_to_line(record: WorkLog, desensitize: bool, attachments: dict[int, list[Attachment]] | None = None) -> dict[str, Any]:
    text = normalize_security_terms(" ".join(filter(None, [record.title, record.content, record.result, record.problem])))
    safe_text = desensitize_text(text) if desensitize else text
    attachment_notes = []
    for attachment in (attachments or {}).get(record.id, []):
        note = attachment.summary or attachment.file_name
        if note:
            attachment_notes.append(desensitize_text(note) if desensitize else note)
    return {
        "date": record.work_date.isoformat(),
        "title": desensitize_text(record.title) if desensitize else record.title,
        "content": safe_text,
        "work_type": record.work_type,
        "duration_hours": record.duration_hours,
        "category": classify_security_work(safe_text),
        "attachments": "；".join(attachment_notes),
    }


def build_input_snapshot(
    db: Session,
    user_id: int,
    date_start: date,
    date_end: date,
    enable_desensitization: bool = True,
) -> dict[str, Any]:
    work_logs = (
        db.query(WorkLog)
        .filter(WorkLog.user_id == user_id, WorkLog.work_date >= date_start, WorkLog.work_date <= date_end)
        .order_by(WorkLog.work_date.asc(), WorkLog.id.asc())
        .all()
    )
    log_ids = [row.id for row in work_logs]
    attachments_by_log: dict[int, list[Attachment]] = {log_id: [] for log_id in log_ids}
    if log_ids:
        for attachment in (
            db.query(Attachment)
            .filter(Attachment.related_type == "work_log", Attachment.related_id.in_(log_ids))
            .order_by(Attachment.created_at.asc(), Attachment.id.asc())
            .all()
        ):
            attachments_by_log.setdefault(attachment.related_id, []).append(attachment)
    tasks = db.query(Task).filter(Task.creator_id == user_id).order_by(Task.updated_at.desc()).limit(200).all()
    overtime_logs = (
        db.query(OvertimeLog)
        .filter(OvertimeLog.user_id == user_id, OvertimeLog.overtime_date >= date_start, OvertimeLog.overtime_date <= date_end)
        .order_by(OvertimeLog.overtime_date.asc(), OvertimeLog.id.asc())
        .all()
    )
    projects = db.query(Project).filter(Project.owner_id == user_id).order_by(Project.updated_at.desc()).limit(100).all()
    return {
        "work_logs": [_record_to_line(row, enable_desensitization, attachments_by_log) for row in work_logs],
        "tasks": [
            {
                "title": desensitize_text(row.title) if enable_desensitization else row.title,
                "status": row.status,
                "priority": row.priority,
                "estimated_hours": row.estimated_hours,
                "actual_hours": row.actual_hours,
                "due_date": row.due_date.isoformat() if row.due_date else None,
            }
            for row in tasks
        ],
        "overtime_logs": [
            {
                "date": row.overtime_date.isoformat(),
                "type": row.overtime_type,
                "duration_hours": row.duration_hours,
                "reason": desensitize_text(row.reason or "") if enable_desensitization else row.reason,
                "content": desensitize_text(row.content or "") if enable_desensitization else row.content,
            }
            for row in overtime_logs
        ],
        "projects": [
            {
                "name": desensitize_text(row.name) if enable_desensitization else row.name,
                "status": row.status,
                "description": desensitize_text(row.description or "") if enable_desensitization else row.description,
            }
            for row in projects
        ],
    }


def _format_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "无"
    lines = []
    for item in items:
        values = [f"{key}: {value}" for key, value in item.items() if value not in (None, "")]
        lines.append("- " + "；".join(values))
    return "\n".join(lines)


def render_report_prompt(template: AIPromptTemplate | None, snapshot: dict[str, Any], options: dict[str, Any]) -> tuple[str, str]:
    system_prompt = template.system_prompt if template else DEFAULT_SYSTEM_PROMPT
    user_prompt_template = template.user_prompt if template else DEFAULT_USER_PROMPT
    variables = {
        **options,
        "work_logs": _format_list(snapshot["work_logs"]),
        "tasks": _format_list(snapshot["tasks"]),
        "overtime_logs": _format_list(snapshot["overtime_logs"]),
        "projects": _format_list(snapshot["projects"]),
    }
    return system_prompt, render_prompt(user_prompt_template, variables)


def local_generate(snapshot: dict[str, Any], options: dict[str, Any]) -> str:
    work_items: list[str] = []
    seen: set[str] = set()
    for row in snapshot.get("work_logs", []):
        content = row.get("content") or row.get("title") or ""
        if row.get("attachments"):
            content = f"{content}；附件摘要：{row['attachments']}"
        category = row.get("category") or "其他工作"
        item = normalize_security_terms(content).strip("。；; ")
        if not item:
            continue
        item = item if len(item) <= 42 else item[:42].rstrip() + "..."
        normalized = item.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        if options.get("group_by_category"):
            work_items.append(f"{category}：{item}")
        else:
            work_items.append(item)
    if options.get("include_overtime"):
        for row in snapshot.get("overtime_logs", []):
            content = row.get("content") or row.get("reason") or "加班值守支撑"
            item = normalize_security_terms(content).strip("。；; ")
            if item and item.lower() not in seen:
                seen.add(item.lower())
                work_items.append(f"加班与值守：{item}")
    if options.get("manual_extra_content"):
        item = normalize_security_terms(options["manual_extra_content"]).strip()
        if item:
            work_items.append(item)
    if not work_items:
        return "本时间范围内暂无可生成周报的工作记录。"
    if options.get("number_style") == "markdown_dash":
        return "\n".join(f"- {item}。" for item in work_items)
    if options.get("number_style") == "dot":
        return "\n".join(f"{idx}. {item}。" for idx, item in enumerate(work_items, 1))
    return "\n".join(f"{idx}、{item}。" for idx, item in enumerate(work_items, 1))


async def generate_report(
    db: Session,
    user_id: int,
    report_type: str,
    date_start: date,
    date_end: date,
    template_id: int | None,
    model_config_id: int | None,
    options: dict[str, Any],
) -> AIGenerationRecord:
    template = db.get(AIPromptTemplate, template_id) if template_id else None
    if template is None:
        template = db.query(AIPromptTemplate).filter(AIPromptTemplate.is_default.is_(True)).first()
    snapshot = build_input_snapshot(
        db,
        user_id,
        date_start,
        date_end,
        enable_desensitization=bool(options.get("enable_desensitization", settings.ai_desensitization_default)),
    )
    system_prompt, user_prompt = render_report_prompt(template, snapshot, options)
    model_config = db.get(AIModelConfig, model_config_id) if model_config_id else None
    if model_config is None:
        model_config = db.query(AIModelConfig).filter(AIModelConfig.created_by == user_id, AIModelConfig.is_default.is_(True)).first()
    status = "completed"
    error_message = None
    if settings.ai_enable and model_config:
        provider = build_provider(
            ProviderConfig(
                provider=model_config.provider,
                base_url=model_config.base_url,
                api_key=decrypt_secret(model_config.api_key_encrypted),
                model_name=model_config.model_name,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
                timeout_seconds=model_config.timeout_seconds,
            )
        )
        try:
            output = await provider.generate(system_prompt, user_prompt)
        except Exception as exc:
            output = ""
            status = "failed"
            error_message = f"AI 生成失败：模型连接失败，请检查 API Key、Base URL 或网络配置。{exc}"
    else:
        output = local_generate(snapshot, options)
    record = AIGenerationRecord(
        user_id=user_id,
        prompt_template_id=template.id if template else None,
        model_config_id=model_config.id if model_config else None,
        report_type=report_type,
        date_start=date_start,
        date_end=date_end,
        input_snapshot=snapshot,
        prompt_content=f"System:\n{system_prompt}\n\nUser:\n{user_prompt}",
        ai_output=output,
        final_output=output,
        status=status,
        error_message=error_message,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
