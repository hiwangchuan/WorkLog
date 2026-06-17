from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=128)
    nickname: str | None = None

    @field_validator("email", "nickname", mode="before")
    @classmethod
    def blank_to_none(cls, value: Any):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)


class UserOut(ORMModel):
    id: int
    username: str
    email: str | None = None
    avatar: str | None = None
    nickname: str | None = None
    phone: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    status: Literal["active", "completed", "paused", "cancelled"] = "active"
    start_date: date | None = None
    end_date: date | None = None
    team_id: int | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    team_id: int | None = None


class ProjectOut(ProjectBase, ORMModel):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: Literal["todo", "in_progress", "blocked", "completed", "cancelled"] = "todo"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    project_id: int | None = None
    assignee_id: int | None = None
    team_id: int | None = None
    due_date: date | None = None
    estimated_hours: float = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    project_id: int | None = None
    assignee_id: int | None = None
    team_id: int | None = None
    due_date: date | None = None
    estimated_hours: float | None = None


class StatusPatch(BaseModel):
    status: Literal["todo", "in_progress", "blocked", "completed", "cancelled"]


class TaskOut(TaskBase, ORMModel):
    id: int
    creator_id: int
    actual_hours: float
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class WorkLogBase(BaseModel):
    work_date: date
    title: str
    content: str | None = None
    work_type: str = "daily"
    project_id: int | None = None
    task_id: int | None = None
    team_id: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration_hours: float = 0
    result: str | None = None
    problem: str | None = None
    next_plan: str | None = None
    visibility: str = "private"


class WorkLogCreate(WorkLogBase):
    pass


class WorkLogUpdate(BaseModel):
    work_date: date | None = None
    title: str | None = None
    content: str | None = None
    work_type: str | None = None
    project_id: int | None = None
    task_id: int | None = None
    team_id: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration_hours: float | None = None
    result: str | None = None
    problem: str | None = None
    next_plan: str | None = None
    visibility: str | None = None


class WorkLogOut(WorkLogBase, ORMModel):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class OvertimeBase(BaseModel):
    overtime_date: date
    overtime_type: Literal["weekday", "weekend", "holiday", "night_shift"] = "weekday"
    project_id: int | None = None
    task_id: int | None = None
    team_id: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration_hours: float = 0
    reason: str | None = None
    content: str | None = None
    approval_status: str = "draft"
    is_compensatory_leave: bool = False
    compensatory_status: str = "none"


class OvertimeCreate(OvertimeBase):
    pass


class OvertimeUpdate(BaseModel):
    overtime_date: date | None = None
    overtime_type: str | None = None
    project_id: int | None = None
    task_id: int | None = None
    team_id: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration_hours: float | None = None
    reason: str | None = None
    content: str | None = None
    approval_status: str | None = None
    is_compensatory_leave: bool | None = None
    compensatory_status: str | None = None


class OvertimeOut(OvertimeBase, ORMModel):
    id: int
    user_id: int
    approver_id: int | None = None
    approval_comment: str | None = None
    created_at: datetime
    updated_at: datetime


class AIModelConfigBase(BaseModel):
    provider: Literal["openai", "anthropic", "deepseek", "qwen", "zhipu", "ollama", "openai_compatible"]
    name: str
    base_url: str | None = None
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 3000
    timeout_seconds: int = 60
    is_default: bool = False
    team_id: int | None = None


class AIModelConfigCreate(AIModelConfigBase):
    api_key: str | None = None


class AIModelConfigUpdate(BaseModel):
    provider: str | None = None
    name: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    model_name: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    timeout_seconds: int | None = None
    is_default: bool | None = None
    team_id: int | None = None


class AIModelConfigOut(AIModelConfigBase, ORMModel):
    id: int
    api_key_masked: str = ""
    created_by: int
    created_at: datetime
    updated_at: datetime


class PromptTemplateBase(BaseModel):
    name: str
    code: str
    category: str = "weekly"
    description: str | None = None
    system_prompt: str
    user_prompt: str
    output_format: str = "markdown"
    work_domain: str = "security_operations"
    is_default: bool = False
    team_id: int | None = None


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    category: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    user_prompt: str | None = None
    output_format: str | None = None
    work_domain: str | None = None
    is_default: bool | None = None
    team_id: int | None = None


class PromptTemplateOut(PromptTemplateBase, ORMModel):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime


class GenerateReportRequest(BaseModel):
    date_start: date
    date_end: date
    template_id: int | None = None
    model_config_id: int | None = None
    output_format: str = "markdown"
    number_style: str = "chinese_comma"
    group_by_category: bool = True
    only_work_items: bool = True
    include_overtime: bool = False
    include_next_week_plan: bool = False
    enable_desensitization: bool = True
    manual_extra_content: str | None = None


class GenerationRecordOut(ORMModel):
    id: int
    user_id: int
    team_id: int | None = None
    prompt_template_id: int | None = None
    model_config_id: int | None = None
    report_type: str
    date_start: date
    date_end: date
    input_snapshot: dict[str, Any]
    prompt_content: str
    ai_output: str | None = None
    final_output: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class FinalOutputUpdate(BaseModel):
    final_output: str


class DesensitizePreviewRequest(BaseModel):
    text: str


class SettingUpdate(BaseModel):
    ai_desensitization_default: bool = True
