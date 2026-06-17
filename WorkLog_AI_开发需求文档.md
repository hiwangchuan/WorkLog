# WorkLog AI：个人及小团队工作任务、工作记录、加班工时与 AI 周报生成系统开发需求文档

## 一、项目名称

系统名称暂定为：

**WorkLog AI**

系统定位：

> 面向个人及小团队的工作任务管理、工作内容记录、加班工时统计、AI 周报生成与报表导出系统。

系统需要支持个人独立使用，也需要预留小团队协作能力。第一版优先完成个人使用闭环，数据库、接口和 UI 需要预留团队、角色、权限、审批能力。

---

## 二、产品目标

本系统主要解决以下问题：

1. 记录每天做了什么工作。
2. 管理个人或小团队任务。
3. 统计工作时长和加班时长。
4. 自动生成日报、周报、月报。
5. 支持调用 AI 大模型，根据自定义 Prompt 生成指定格式周报。
6. 针对网络安全运营、WAF、蜜罐、告警分析、重保、攻防演练等工作方向进行专业化优化。
7. 支持 Docker Compose 一键部署。
8. 支持 Markdown、Word、PDF、Excel 等格式导出。

---

## 三、目标用户

### 1. 个人用户

- 记录每日工作内容。
- 管理待办任务。
- 统计工时和加班。
- 生成个人周报。

### 2. 小团队

- 分配任务。
- 查看成员工作记录。
- 汇总团队工作量。
- 审核加班记录。
- 生成团队周报。

### 3. 安全运营人员

- WAF/API 设备巡检。
- WAF/蜜罐告警监测。
- 安全事件分析。
- 态势感知工单处理。
- 重保值守。
- 攻防演练支撑。
- 周报、日报、统计材料输出。

---

## 四、推荐技术栈

### 1. 前端

- Vue 3
- TypeScript
- Vite
- Naive UI
- ECharts
- Pinia
- Vue Router
- Axios
- Markdown 编辑器组件
- Monaco Editor 或 CodeMirror，用于 Prompt 编辑器

### 2. 后端

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT 鉴权
- Passlib / bcrypt
- Pandas / OpenPyXL，用于 Excel 导出
- python-docx，用于 Word 导出
- WeasyPrint 或 Playwright，用于 PDF 导出

### 3. 数据库与中间件

- PostgreSQL
- Redis

### 4. AI 大模型

需要支持以下模型接入方式：

- OpenAI
- Anthropic Claude
- DeepSeek
- 通义千问
- 智谱 GLM
- Ollama 本地模型
- OpenAI Compatible API

### 5. 部署方式

- Docker
- Docker Compose
- Nginx 反向代理

---

## 五、系统模块

系统包含以下模块：

1. 用户登录与账户管理
2. 首页仪表盘
3. 任务管理
4. 工作记录
5. 加班记录
6. 项目管理
7. AI 周报生成
8. Prompt 模板管理
9. AI 模型配置
10. 报表中心
11. 数据统计
12. 团队管理，第一版预留
13. 系统设置
14. Docker 部署
15. 数据备份与恢复

---

## 六、用户与权限设计

### 1. 用户角色

第一版优先实现个人用户权限，后续扩展团队权限。

预留角色：

1. 管理员
2. 负责人
3. 普通成员
4. 只读成员

### 2. 权限说明

| 角色 | 权限 |
|---|---|
| 管理员 | 管理团队、成员、项目、任务、工作记录、加班记录、AI 配置 |
| 负责人 | 分配任务、查看成员工作记录、审核加班 |
| 普通成员 | 管理自己的任务、工作记录、加班记录 |
| 只读成员 | 查看授权范围内的数据 |

### 3. 数据可见范围

工作记录需要支持以下可见范围：

1. 仅自己可见
2. 项目成员可见
3. 团队可见
4. 管理员可见

---

## 七、核心功能需求

### 1. 用户登录与账户管理

#### 功能要求

1. 用户注册。
2. 用户登录。
3. JWT 鉴权。
4. 修改密码。
5. 退出登录。
6. 获取当前用户信息。
7. 后续预留头像、昵称、邮箱、手机号等字段。

#### 接口

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
PUT  /api/auth/password
```

---

### 2. 首页仪表盘

首页用于展示工作概览。

#### 个人首页需要展示

1. 今日待办任务数。
2. 今日已完成任务数。
3. 本周完成任务数。
4. 本月累计工时。
5. 本月累计加班时长。
6. 超期任务数量。
7. 今日待办任务列表。
8. 最近工作记录。
9. 最近生成的周报。
10. 本周工时趋势图。
11. 任务状态分布图。
12. 项目工时分布图。
13. 加班趋势图。

#### 团队首页预留展示

1. 团队成员数。
2. 团队任务总数。
3. 进行中任务数。
4. 已完成任务数。
5. 超期任务数。
6. 团队总工时。
7. 团队加班时长。
8. 成员工作量排行。
9. 项目工时分布。

#### 接口

```http
GET /api/dashboard/summary
GET /api/dashboard/work-hours-trend
GET /api/dashboard/task-status
GET /api/dashboard/project-hours
GET /api/dashboard/overtime-trend
```

---

### 3. 任务管理

#### 功能要求

1. 新建任务。
2. 编辑任务。
3. 删除任务。
4. 查看任务详情。
5. 修改任务状态。
6. 设置任务优先级。
7. 设置截止时间。
8. 设置预计工时。
9. 根据工作记录自动汇总实际工时。
10. 支持任务关联项目。
11. 支持任务关联工作记录。
12. 支持任务关联加班记录。
13. 支持标签。
14. 支持列表视图。
15. 支持看板视图。
16. 支持日历视图。
17. 后续预留甘特图视图。
18. 支持按项目、状态、优先级、负责人、截止日期、关键词筛选。
19. 支持批量操作。

#### 任务字段

```text
id
team_id
project_id
title
description
status
priority
assignee_id
creator_id
due_date
estimated_hours
actual_hours
completed_at
created_at
updated_at
```

#### 任务状态

```text
todo：待开始
in_progress：进行中
blocked：阻塞
completed：已完成
cancelled：已取消
```

#### 任务优先级

```text
low：低
medium：中
high：高
urgent：紧急
```

#### 接口

```http
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/{id}
PUT    /api/tasks/{id}
DELETE /api/tasks/{id}
PATCH  /api/tasks/{id}/status
```

---

### 4. 工作记录

工作记录是系统核心模块之一，需要支持快速填写。

#### 功能要求

1. 新增工作记录。
2. 编辑工作记录。
3. 删除工作记录。
4. 查看工作记录详情。
5. 支持按日期筛选。
6. 支持按项目筛选。
7. 支持按任务筛选。
8. 支持按工作类型筛选。
9. 支持关键词搜索。
10. 支持时间线视图。
11. 支持表格视图。
12. 支持快速新增。
13. 支持“保存并继续添加”。
14. 支持工作记录模板。
15. 支持关联任务。
16. 支持关联项目。
17. 支持填写工作时长。
18. 支持根据开始时间和结束时间自动计算工时。
19. 支持记录处理结果、问题风险、后续计划。
20. 支持作为 AI 周报生成的数据来源。

#### 工作记录字段

```text
id
team_id
project_id
task_id
user_id
work_date
title
content
work_type
start_time
end_time
duration_hours
result
problem
next_plan
visibility
created_at
updated_at
```

#### 工作类型

```text
daily：日常工作
project：项目工作
meeting：会议
operation：运维
security：安全分析
incident：故障/应急
document：文档
development：开发
testing：测试
learning：学习
other：其他
```

#### 安全运营工作模板

系统需要内置以下工作记录模板：

1. WAF/API 设备巡检
2. WAF 告警分析
3. 蜜罐告警分析
4. 态势工单处理
5. 站点接入支撑
6. 端口分配
7. 网络连通性测试
8. 策略调整
9. 证书替换
10. 重保值守
11. 攻防演练支撑
12. 周报整理
13. 会议沟通
14. 故障排查
15. 应急响应

#### 接口

```http
GET    /api/work-logs
POST   /api/work-logs
GET    /api/work-logs/{id}
PUT    /api/work-logs/{id}
DELETE /api/work-logs/{id}
```

---

### 5. 加班记录

#### 功能要求

1. 新增加班记录。
2. 编辑加班记录。
3. 删除加班记录。
4. 查看加班详情。
5. 选择开始时间和结束时间后自动计算加班时长。
6. 支持工作日加班。
7. 支持周末加班。
8. 支持节假日加班。
9. 支持夜间值班。
10. 支持关联任务。
11. 支持关联项目。
12. 支持填写加班原因和具体工作内容。
13. 支持审核状态字段，第一版可不做完整审核流程，但字段必须预留。
14. 支持调休状态字段，第一版预留。
15. 支持按月份、加班类型、审核状态、项目筛选。
16. 支持加班统计。
17. 支持作为 AI 周报或加班说明的数据来源。

#### 加班记录字段

```text
id
team_id
project_id
task_id
user_id
overtime_date
overtime_type
start_time
end_time
duration_hours
reason
content
approval_status
approver_id
approval_comment
is_compensatory_leave
compensatory_status
created_at
updated_at
```

#### 加班类型

```text
weekday：工作日加班
weekend：周末加班
holiday：节假日加班
night_shift：夜间值班
```

#### 审核状态

```text
draft：草稿
pending：待审核
approved：已通过
rejected：已驳回
```

#### 接口

```http
GET    /api/overtime-logs
POST   /api/overtime-logs
GET    /api/overtime-logs/{id}
PUT    /api/overtime-logs/{id}
DELETE /api/overtime-logs/{id}
POST   /api/overtime-logs/{id}/submit
POST   /api/overtime-logs/{id}/approve
POST   /api/overtime-logs/{id}/reject
```

---

### 6. 项目管理

#### 功能要求

1. 创建项目。
2. 编辑项目。
3. 删除项目。
4. 查看项目详情。
5. 项目关联任务。
6. 项目关联工作记录。
7. 项目关联加班记录。
8. 项目详情页展示任务列表。
9. 项目详情页展示工作记录。
10. 项目详情页展示工时统计。
11. 项目详情页展示加班统计。
12. 项目详情页展示成员贡献，团队版使用。

#### 项目字段

```text
id
team_id
name
description
status
owner_id
start_date
end_date
created_at
updated_at
```

#### 项目状态

```text
active：进行中
completed：已完成
paused：暂停
cancelled：已取消
```

#### 接口

```http
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}
GET    /api/projects/{id}/summary
```

---

## 八、AI 周报生成模块

AI 周报生成是系统核心差异化功能。

### 1. 模块目标

系统需要支持调用 AI 大模型，根据用户选择的时间范围、工作记录、任务记录、加班记录、项目记录和手动补充内容，结合 Prompt 模板生成指定格式的日报、周报、月报和加班说明。

### 2. AI 周报生成流程

```text
选择时间范围
  ↓
选择数据来源
  ↓
系统读取工作记录、任务、加班记录、项目记录
  ↓
进行数据预处理
  ↓
合并重复事项
  ↓
识别安全运营工作分类
  ↓
敏感信息脱敏
  ↓
组装 Prompt
  ↓
调用 AI 大模型
  ↓
获取生成结果
  ↓
进行格式校验
  ↓
用户编辑确认
  ↓
保存最终版本
  ↓
复制或导出
```

### 3. AI 输入数据来源

1. 工作记录。
2. 任务记录。
3. 加班记录。
4. 项目记录。
5. 标签。
6. 工作类型。
7. 手动补充内容。
8. 附件摘要，后续预留。

### 4. AI 数据预处理

调用大模型前必须进行预处理：

1. 按日期范围筛选记录。
2. 删除空记录。
3. 删除无效记录。
4. 合并重复内容。
5. 按项目归类。
6. 按任务归类。
7. 按工作类型归类。
8. 识别安全运营分类。
9. 提取关键词。
10. 对敏感信息脱敏。
11. 构造结构化输入。

### 5. 安全运营分类模型

系统需要内置以下安全运营分类：

| 分类 | 典型内容 |
|---|---|
| WAF/API 日常巡检 | 设备状态、服务状态、资源占用、站点运行情况 |
| WAF 告警监测 | 攻击请求、拦截情况、攻击类型、源 IP、站点 TOP |
| 蜜罐告警监测 | 探针状态、攻击源、攻击行为、事件分析 |
| 告警分析与上报 | 告警研判、误报分析、事件上报、态势同步 |
| 安全事件排查 | SQL 注入、目录穿越、扫描器、信息泄露、弱口令等 |
| 重保/攻防演练 | 重保值守、演练支撑、告警复盘、日报输出 |
| 站点接入与变更 | 站点创建、端口分配、证书替换、网络测试 |
| 策略优化 | WAF 策略调整、规则优化、拦截模式变更 |
| 工单处理 | 天眼工单、态势工单、接口人反馈、问题闭环 |
| 自动化与报表 | 周报、脚本、Excel、统计图、自动化推送规则 |
| 会议与沟通 | 对接会议、需求沟通、方案讨论 |
| 加班与值守 | 夜间值守、应急处理、周末支撑 |

### 6. 安全运营术语归一化

系统需要对口语化记录进行专业表达转换：

| 原始表达 | 周报表达 |
|---|---|
| 看了一下 WAF 告警 | WAF 告警监测及分析 |
| 查了蜜罐日志 | 蜜罐告警日志分析 |
| 处理天眼单子 | 态势感知平台工单处理 |
| 跟业务打网 | 网络连通性测试 |
| 加站点 | 站点接入配置 |
| 换证书 | 证书替换及配置验证 |
| 开拦截 | WAF 拦截策略调整 |
| 写周报 | 安全运营周报编写与输出 |

### 7. AI 周报模板

系统内置以下 Prompt 模板：

1. 个人简洁周报
2. 安全运营简洁周报
3. 安全运营正式周报
4. 团队工作周报
5. 加班说明生成
6. 工作记录润色
7. 原始记录归类版
8. 领导汇报版

### 8. 安全运营简洁周报模板规则

模板名称：

**安全运营简洁周报**

适用场景：

个人周报、日常工作汇总、复制到企业微信、钉钉、邮件或内部系统。

输出规则：

1. 只输出本周完成的工作事项。
2. 只写干了什么。
3. 不写为什么。
4. 不写结果。
5. 不写价值总结。
6. 不写“保障了”“提升了”“有效支撑了”等空泛表达。
7. 不编造未提供内容。
8. 重复事项要合并。
9. 不按日期输出。
10. 使用 1、2、3、4 编号。
11. 每条内容简洁正式。
12. 每条建议控制在 20 到 40 字左右。

优先保留以下工作方向：

1. WAF/API 设备每日巡检。
2. WAF/蜜罐告警监测及上报。
3. 告警分析与事件排查。
4. 态势感知平台工单处理。
5. 站点接入、端口分配、网络测试。
6. 策略调整、证书替换、变更支撑。
7. 重保值守、攻防演练支撑。
8. 周报、报表、材料整理输出。

输出示例：

```text
1、WAF/API设备每日巡检。
2、WAF/蜜罐告警监测及上报。
3、态势感知平台工单处理。
4、配合完成站点接入、端口分配及网络测试。
5、整理并输出本周安全运营周报。
```

### 9. AI 系统 Prompt 示例

```text
你是一名网络安全运营周报助手，擅长整理 WAF、API 安全、蜜罐、态势感知、告警分析、重保值守、攻防演练、工单处理、站点接入、策略优化、巡检和报表输出类工作内容。

你需要根据用户提供的工作记录，生成指定格式的周报内容。

要求：
1. 不得编造用户未提供的工作内容。
2. 不得夸大工作成果。
3. 对重复事项进行合并。
4. 保留安全运营相关专业表达。
5. 输出内容要正式、简洁、适合工作汇报。
6. 如果用户要求“只写干了什么”，则不要写原因、背景、意义和结果。
7. 对 WAF、蜜罐、态势、重保、工单、巡检等内容进行优先归类。
```

### 10. AI 用户 Prompt 模板

```text
请根据以下工作记录生成本周周报。

【输出要求】
- 输出格式：{output_format}
- 编号格式：{number_style}
- 是否按分类输出：{group_by_category}
- 是否只写干了什么：{only_work_items}
- 是否包含加班情况：{include_overtime}
- 是否包含下周计划：{include_next_week_plan}
- 语言风格：{tone}
- 字数要求：{word_limit}

【我的工作方向】
网络安全运营，主要涉及 WAF/API 设备巡检、WAF/蜜罐告警监测与上报、告警分析、态势感知平台工单、重保值守、攻防演练、站点接入、策略优化、变更支撑和周报材料输出。

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

【输出格式示例】
{format_example}
```

### 11. AI 输出格式

系统需要支持以下输出格式：

1. 纯文本。
2. Markdown。
3. Word。
4. PDF。
5. Excel。
6. JSON。

### 12. 编号格式

支持：

```text
1、2、3、4
1. 2. 3. 4.
一、二、三、四
- 无序列表
Markdown 标题结构
```

---

## 九、AI 模型配置

### 1. 功能要求

1. 支持新增模型配置。
2. 支持编辑模型配置。
3. 支持删除模型配置。
4. 支持设置默认模型。
5. 支持测试连接。
6. 支持不同模型供应商。
7. 支持 OpenAI Compatible API。
8. API Key 必须加密存储。
9. API Key 不能明文展示。
10. 支持超时时间配置。
11. 支持 temperature 配置。
12. 支持 max_tokens 配置。

### 2. 支持供应商

```text
openai
anthropic
deepseek
qwen
zhipu
ollama
openai_compatible
```

### 3. 推荐默认参数

```text
temperature: 0.2
max_tokens: 3000
timeout_seconds: 60
```

### 4. ai_model_configs 表

```text
id
provider
name
base_url
api_key_encrypted
model_name
temperature
max_tokens
timeout_seconds
is_default
team_id
created_by
created_at
updated_at
```

---

## 十、Prompt 模板管理

### 1. 功能要求

1. 新增 Prompt 模板。
2. 编辑 Prompt 模板。
3. 删除 Prompt 模板。
4. 设置默认模板。
5. 按模板分类筛选。
6. 按工作方向筛选。
7. 支持 System Prompt。
8. 支持 User Prompt。
9. 支持输出示例。
10. 支持变量提示。
11. 支持测试生成。

### 2. 支持变量

```text
{work_logs}
{tasks}
{overtime_logs}
{projects}
{date_start}
{date_end}
{output_format}
{manual_extra_content}
{number_style}
{group_by_category}
{only_work_items}
{include_overtime}
{include_next_week_plan}
```

### 3. ai_prompt_templates 表

```text
id
name
code
category
description
system_prompt
user_prompt
output_format
work_domain
is_default
team_id
created_by
created_at
updated_at
```

---

## 十一、AI 生成记录

### 1. 功能要求

1. 保存每次 AI 生成记录。
2. 保存输入数据快照。
3. 保存实际发送给模型的 Prompt。
4. 保存 AI 原始输出。
5. 保存用户编辑后的最终版本。
6. 支持查看历史记录。
7. 支持重新生成。
8. 支持删除记录。
9. 支持导出历史记录。

### 2. ai_generation_records 表

```text
id
user_id
team_id
prompt_template_id
model_config_id
report_type
date_start
date_end
input_snapshot
prompt_content
ai_output
final_output
status
error_message
created_at
updated_at
```

### 3. 接口

```http
GET    /api/ai/generation-records
GET    /api/ai/generation-records/{id}
PUT    /api/ai/generation-records/{id}/final-output
DELETE /api/ai/generation-records/{id}
```

---

## 十二、AI 报告生成接口

### 1. AI 配置接口

```http
GET    /api/ai/model-configs
POST   /api/ai/model-configs
PUT    /api/ai/model-configs/{id}
DELETE /api/ai/model-configs/{id}
POST   /api/ai/model-configs/{id}/test
```

### 2. Prompt 模板接口

```http
GET    /api/ai/prompt-templates
POST   /api/ai/prompt-templates
GET    /api/ai/prompt-templates/{id}
PUT    /api/ai/prompt-templates/{id}
DELETE /api/ai/prompt-templates/{id}
```

### 3. 报告生成接口

```http
POST /api/ai/reports/daily/generate
POST /api/ai/reports/weekly/generate
POST /api/ai/reports/monthly/generate
POST /api/ai/reports/overtime/generate
```

### 4. 周报生成请求示例

```json
{
  "date_start": "2026-06-08",
  "date_end": "2026-06-14",
  "template_id": 1,
  "model_config_id": 1,
  "output_format": "markdown",
  "number_style": "chinese_comma",
  "group_by_category": true,
  "only_work_items": true,
  "include_overtime": false,
  "include_next_week_plan": false,
  "enable_desensitization": true,
  "manual_extra_content": "补充本周配合完成安全生产月相关变更管控说明。"
}
```

---

## 十三、敏感信息脱敏

### 1. 功能要求

系统调用外部大模型前，需要支持敏感信息脱敏。

默认开启脱敏。

### 2. 脱敏范围

| 类型 | 示例 | 脱敏后 |
|---|---|---|
| 内网 IP | 10.10.23.45 | 10.x.x.x |
| 公网 IP | 1.2.3.4 | x.x.x.x |
| 域名 | test.example.com | 某业务域名 |
| 系统名 | XXX系统 | 某系统 |
| 联系人 | 张三 | 某接口人 |
| Token/API Key | abc123xxx | [已脱敏] |
| 账号 | admin/test | [账号已脱敏] |
| 密码 | password123 | [密码已脱敏] |

### 3. 脱敏要求

1. AI 生成前支持脱敏预览。
2. 支持查看脱敏前后差异。
3. 默认脱敏后再发送给外部模型。
4. 本地 Ollama 模型可允许关闭脱敏。
5. 系统设置中需要有全局默认脱敏开关。

---

## 十四、报表中心

### 1. 功能要求

1. 生成日报。
2. 生成周报。
3. 生成月报。
4. 生成加班报表。
5. 生成工时报表。
6. 查看历史报表。
7. 按时间范围筛选。
8. 按项目筛选。
9. 按成员筛选，团队版使用。
10. 导出 Markdown。
11. 导出 Word。
12. 导出 PDF。
13. 导出 Excel。
14. 删除报表。

### 2. 报表接口

```http
GET /api/reports/daily
GET /api/reports/weekly
GET /api/reports/monthly
GET /api/reports/overtime
GET /api/reports/work-hours
GET /api/reports/export
```

---

## 十五、数据统计

### 1. 统计内容

1. 每日工时趋势。
2. 每周工时趋势。
3. 每月工时统计。
4. 项目工时分布。
5. 任务状态分布。
6. 任务完成趋势。
7. 加班趋势。
8. 加班类型占比。
9. 工作类型占比。
10. 成员工作量排行，团队版使用。
11. 工作记录日历热力图。

### 2. 图表类型

1. 折线图。
2. 柱状图。
3. 横向条形图。
4. 饼图。
5. 环形图。
6. 日历热力图。
7. 堆叠柱状图。

### 3. 接口

```http
GET /api/statistics/tasks
GET /api/statistics/work-hours
GET /api/statistics/overtime
GET /api/statistics/projects
GET /api/statistics/work-types
GET /api/statistics/calendar-heatmap
```

---

## 十六、数据库设计

### 1. users

```text
id
username
email
password_hash
avatar
status
created_at
updated_at
```

### 2. teams

```text
id
name
description
owner_id
created_at
updated_at
```

### 3. team_members

```text
id
team_id
user_id
role
joined_at
```

### 4. projects

```text
id
team_id
name
description
status
owner_id
start_date
end_date
created_at
updated_at
```

### 5. tasks

```text
id
team_id
project_id
title
description
status
priority
assignee_id
creator_id
due_date
estimated_hours
actual_hours
completed_at
created_at
updated_at
```

### 6. work_logs

```text
id
team_id
project_id
task_id
user_id
work_date
title
content
work_type
start_time
end_time
duration_hours
result
problem
next_plan
visibility
created_at
updated_at
```

### 7. overtime_logs

```text
id
team_id
project_id
task_id
user_id
overtime_date
overtime_type
start_time
end_time
duration_hours
reason
content
approval_status
approver_id
approval_comment
is_compensatory_leave
compensatory_status
created_at
updated_at
```

### 8. tags

```text
id
team_id
name
color
type
created_at
```

### 9. task_tags

```text
task_id
tag_id
```

### 10. attachments

```text
id
related_type
related_id
file_name
file_url
file_size
uploader_id
created_at
```

### 11. ai_model_configs

```text
id
provider
name
base_url
api_key_encrypted
model_name
temperature
max_tokens
timeout_seconds
is_default
team_id
created_by
created_at
updated_at
```

### 12. ai_prompt_templates

```text
id
name
code
category
description
system_prompt
user_prompt
output_format
work_domain
is_default
team_id
created_by
created_at
updated_at
```

### 13. ai_generation_records

```text
id
user_id
team_id
prompt_template_id
model_config_id
report_type
date_start
date_end
input_snapshot
prompt_content
ai_output
final_output
status
error_message
created_at
updated_at
```

---

## 十七、UI/UX 设计要求

### 1. 整体风格

系统需要具备现代化、简洁、专业的后台管理系统 UI。

设计风格：

1. 现代化。
2. 简洁。
3. 专业。
4. 信息密度适中偏高。
5. 适合长期工作记录。
6. 适合个人和小团队使用。
7. 适合安全运营场景。

### 2. 整体布局

使用：

```text
左侧导航栏 + 顶部工具栏 + 主内容区域
```

左侧导航：

```text
首页仪表盘
任务管理
工作记录
加班记录
项目管理
AI 周报生成
报表中心
团队管理
数据统计
系统设置
```

顶部工具栏：

1. 全局搜索。
2. 快捷新增任务。
3. 快捷新增工作记录。
4. 快捷新增加班。
5. AI 生成周报入口。
6. 通知。
7. 用户菜单。

### 3. 视觉规范

主色调建议：

```text
主色：蓝色或靛蓝色
背景：浅灰白
文字：深灰
成功：绿色
警告：橙色
错误：红色
信息：蓝色
```

状态颜色：

| 状态 | 颜色 |
|---|---|
| 待开始 | 灰色 |
| 进行中 | 蓝色 |
| 阻塞 | 橙色 |
| 已完成 | 绿色 |
| 已取消 | 浅灰色 |
| 已超期 | 红色 |

卡片要求：

1. 圆角 8px 到 12px。
2. 浅边框。
3. 轻微阴影。
4. 留白合理。

表格要求：

1. 固定表头。
2. 支持排序。
3. 支持筛选。
4. 支持分页。
5. 支持列显示隐藏。
6. 支持批量操作。

### 4. 首页仪表盘 UI

首页结构：

```text
首页仪表盘
├── 顶部数据卡片
│   ├── 今日待办
│   ├── 本周完成
│   ├── 本月工时
│   ├── 本月加班
│   └── 超期任务
├── 今日待办任务
├── 快速新增工作记录
├── 快速新增加班记录
├── 本周工时趋势图
├── 任务状态分布图
├── 项目工时分布图
├── 加班趋势图
└── 最近动态
```

### 5. 任务管理 UI

任务管理页需要支持：

1. 列表视图。
2. 看板视图。
3. 日历视图。
4. 甘特图视图预留。
5. 顶部筛选区。
6. 右侧抽屉新建任务。
7. 右侧抽屉编辑任务。
8. 右侧抽屉查看任务详情。
9. 任务状态彩色 Tag。
10. 优先级彩色 Tag。
11. 临近截止时间高亮。
12. 超期任务红色提示。

任务详情抽屉包含：

```text
基本信息
任务描述
关联工作记录
关联加班记录
附件
操作历史
评论/备注
```

### 6. 工作记录 UI

工作记录页需要支持：

1. 时间线视图。
2. 表格视图。
3. 快速新增工作记录。
4. 右侧抽屉编辑。
5. 日期筛选。
6. 项目筛选。
7. 工作类型筛选。
8. 关键词搜索。
9. 保存并继续添加。
10. 工作记录模板选择。

新增工作记录抽屉字段：

```text
工作日期
工作标题
工作类型
所属项目
关联任务
开始时间
结束时间
工作时长
工作内容
处理结果
问题风险
后续计划
保存
保存并继续
```

### 7. 加班记录 UI

加班记录页包含：

```text
本月加班统计卡片
工作日加班统计卡片
周末加班统计卡片
节假日加班统计卡片
调休余额卡片，预留
加班记录表格
筛选区
```

筛选项：

1. 月份。
2. 加班类型。
3. 审核状态。
4. 项目。

加班记录表格字段：

```text
日期
类型
开始时间
结束时间
时长
原因
审核状态
操作
```

### 8. AI 周报生成 UI

AI 周报生成页是系统核心页面，需要重点设计。

采用：

```text
左侧配置区 + 右侧预览编辑区
```

页面结构：

```text
AI 周报生成
├── 左侧配置区
│   ├── 时间范围
│   ├── 数据来源
│   ├── Prompt 模板
│   ├── 输出格式
│   ├── 编号方式
│   ├── 是否按分类输出
│   ├── 是否包含加班情况
│   ├── 是否包含下周计划
│   ├── 是否启用脱敏
│   ├── 手动补充内容
│   └── 生成周报按钮
│
└── 右侧结果区
    ├── 输入数据预览
    ├── 脱敏预览
    ├── AI 生成结果
    ├── Markdown 编辑器
    ├── 最终编辑版
    ├── 复制
    ├── 保存
    ├── 重新生成
    ├── 导出 Markdown
    ├── 导出 Word
    └── 导出 PDF
```

AI 生成过程需要显示步骤：

```text
正在整理工作记录...
正在合并重复事项...
正在进行敏感信息脱敏...
正在调用 AI 模型...
正在生成周报内容...
正在进行格式校验...
```

AI 生成失败时需要明确提示：

```text
AI 生成失败：模型连接超时，请检查 API Key、Base URL 或网络配置。
```

### 9. Prompt 模板管理 UI

页面包含：

1. 模板列表。
2. 新增模板。
3. 编辑模板。
4. 删除模板。
5. 设置默认模板。
6. 模板分类。
7. 工作方向。
8. System Prompt 编辑器。
9. User Prompt 编辑器。
10. 输出示例编辑器。
11. 可用变量提示。
12. 测试生成按钮。

Prompt 编辑器使用等宽字体。

### 10. AI 模型配置 UI

页面包含：

1. 模型配置列表。
2. 新增模型配置。
3. 编辑模型配置。
4. 删除模型配置。
5. 设置默认模型。
6. 测试连接。
7. Provider 选择。
8. Base URL 输入。
9. API Key 输入。
10. Model Name 输入。
11. Temperature 配置。
12. Max Tokens 配置。
13. Timeout 配置。

API Key 展示规则：

```text
sk-***************abcd
```

不允许展示完整 API Key。

### 11. 报表中心 UI

报表中心包含：

1. 日报列表。
2. 周报列表。
3. 月报列表。
4. 加班报表。
5. 工时报表。
6. 时间范围筛选。
7. 项目筛选。
8. 成员筛选，团队版。
9. 查看报表。
10. 导出报表。
11. 删除报表。

### 12. 数据统计 UI

统计页面包含：

1. 每日工时趋势折线图。
2. 项目工时分布柱状图。
3. 任务状态分布饼图。
4. 成员工作量排行。
5. 加班趋势图。
6. 工作类型占比图。
7. 工作记录日历热力图。

### 13. 移动端适配

第一版不需要独立 App，但 Web 需要适配移动端。

移动端底部导航：

```text
首页
任务
记录
加班
AI周报
我的
```

移动端至少支持：

1. 查看首页概览。
2. 查看今日任务。
3. 新增工作记录。
4. 新增加班记录。
5. 生成和复制 AI 周报。
6. 查看个人中心。

### 14. 交互体验

1. 所有新增和编辑操作优先使用右侧抽屉。
2. 表格需要支持分页、排序、筛选。
3. 重要操作需要二次确认。
4. 表单需要基础校验。
5. 工作记录编辑器支持草稿自动保存。
6. AI 周报编辑器支持草稿自动保存。
7. 空数据页面需要有友好提示和快捷创建按钮。
8. AI 生成失败时需要给出明确原因。
9. 长耗时操作需要显示进度或步骤。
10. 支持一键复制周报内容。
11. 支持 Ctrl/Cmd + S 保存。

---

## 十八、Docker 部署要求

系统必须支持 Docker 和 Docker Compose 一键部署。

### 1. 部署目标

需要支持以下命令启动完整系统：

```bash
docker compose up -d --build
```

### 2. Docker 服务组成

至少包含以下服务：

1. frontend：前端静态页面服务。
2. backend：FastAPI 后端服务。
3. postgres：PostgreSQL 数据库。
4. redis：缓存和任务队列。
5. nginx：统一反向代理入口。

可选服务：

1. minio：附件对象存储。
2. worker：异步任务处理，用于 AI 生成、报表导出、定时任务。
3. ollama：本地大模型服务。

### 3. 推荐目录结构

```text
worklog-ai/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── src/
│
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── alembic/
│   ├── requirements.txt
│   └── entrypoint.sh
│
├── nginx/
│   └── nginx.conf
│
├── data/
│   ├── uploads/
│   ├── exports/
│   ├── logs/
│   ├── certs/
│   └── backups/
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

### 4. docker-compose.yml 要求

docker-compose.yml 需要包含：

```text
postgres
redis
backend
frontend
nginx
```

端口要求：

```text
nginx: 80 / 443
backend: 8000，仅容器内部访问
frontend: 80，仅容器内部访问
postgres: 5432，默认不暴露到宿主机
redis: 6379，默认不暴露到宿主机
```

### 5. .env.example 要求

必须提供 `.env.example`。

至少包含：

```env
APP_NAME=WorkLog AI
APP_ENV=production
APP_DEBUG=false
APP_SECRET_KEY=please-change-this-secret
APP_BASE_URL=http://localhost

POSTGRES_PASSWORD=please-change-this-password
DATABASE_URL=postgresql://worklog:please-change-this-password@postgres:5432/worklog

REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=please-change-this-jwt-secret
JWT_EXPIRE_MINUTES=1440

UPLOAD_DRIVER=local
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=50

AI_ENABLE=true
AI_DEFAULT_PROVIDER=openai_compatible
AI_REQUEST_TIMEOUT=60
AI_DESENSITIZATION_DEFAULT=true

CONFIG_ENCRYPTION_KEY=please-change-this-32-byte-key

CORS_ORIGINS=http://localhost,http://127.0.0.1
```

### 6. 后端 Docker 要求

1. 后端需要提供 Dockerfile。
2. 使用 Python 3.12 slim 镜像。
3. 安装依赖时使用 requirements.txt。
4. 启动命令使用 uvicorn。
5. 启动前需要等待数据库可用。
6. 启动前自动执行 alembic upgrade head。
7. 提供 `/api/health` 健康检查接口。

后端启动流程：

```text
等待 PostgreSQL 可用
  ↓
执行 Alembic 数据库迁移
  ↓
启动 FastAPI 服务
```

### 7. 前端 Docker 要求

1. 前端需要提供 Dockerfile。
2. 使用 Node 镜像构建前端。
3. 使用 Nginx 镜像托管 dist 静态文件。
4. 支持前端路由 history fallback。
5. API 请求通过 `/api` 反向代理到后端。

### 8. Nginx 要求

1. 提供 `nginx/nginx.conf`。
2. `/` 代理到 frontend。
3. `/api/` 代理到 backend。
4. 支持 `client_max_body_size`，默认 50m。
5. 预留 HTTPS 配置。
6. 支持后续挂载 SSL 证书。

### 9. 数据持久化

需要持久化：

1. PostgreSQL 数据。
2. 上传附件。
3. 导出文件。
4. 系统日志。
5. SSL 证书。
6. 数据库备份文件。

建议目录：

```text
data/
├── uploads/
├── exports/
├── logs/
├── certs/
└── backups/
```

### 10. 备份恢复要求

README 中必须提供：

1. 数据库备份命令。
2. 数据库恢复命令。
3. 上传文件备份说明。
4. 容器升级说明。
5. 数据卷清理风险提示。

数据库备份示例：

```bash
docker exec worklog-postgres pg_dump -U worklog worklog > ./data/backups/worklog_$(date +%F).sql
```

数据库恢复示例：

```bash
cat ./data/backups/worklog_2026-06-16.sql | docker exec -i worklog-postgres psql -U worklog -d worklog
```

### 11. 健康检查

后端健康检查接口：

```http
GET /api/health
```

返回示例：

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok",
  "version": "1.0.0"
}
```

Docker healthcheck 需要覆盖：

1. backend。
2. postgres。
3. redis。

### 12. 生产安全要求

1. PostgreSQL 和 Redis 默认不暴露到公网。
2. API Key、JWT Secret、数据库密码不得写死在代码中。
3. AI 模型 API Key 必须加密存储。
4. `.env` 不允许提交到 Git。
5. 默认开启敏感信息脱敏。
6. Nginx 预留 HTTPS 配置。
7. 支持限制上传文件大小。
8. 支持 CORS 白名单配置。
9. 后端接口需要鉴权。
10. 用户只能访问自己有权限的数据。

---

## 十九、工程结构要求

### 1. 后端结构

```text
backend/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── tasks.py
│   │   ├── work_logs.py
│   │   ├── overtime_logs.py
│   │   ├── projects.py
│   │   ├── reports.py
│   │   ├── statistics.py
│   │   └── ai.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── permissions.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── ai/
│   │   │   ├── providers/
│   │   │   ├── prompt_renderer.py
│   │   │   ├── desensitizer.py
│   │   │   └── report_generator.py
│   │   ├── report_service.py
│   │   └── statistics_service.py
│   │
│   ├── utils/
│   └── main.py
│
├── alembic/
├── requirements.txt
├── Dockerfile
└── entrypoint.sh
```

### 2. 前端结构

```text
frontend/
├── src/
│   ├── api/
│   ├── assets/
│   ├── components/
│   ├── layouts/
│   ├── router/
│   ├── stores/
│   ├── views/
│   │   ├── dashboard/
│   │   ├── tasks/
│   │   ├── work-logs/
│   │   ├── overtime/
│   │   ├── projects/
│   │   ├── ai-report/
│   │   ├── reports/
│   │   ├── statistics/
│   │   └── settings/
│   ├── utils/
│   └── main.ts
│
├── package.json
├── Dockerfile
└── nginx.conf
```

---

## 二十、接口统一返回格式

所有接口统一返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误示例：

```json
{
  "code": 40001,
  "message": "参数错误",
  "data": null
}
```

分页格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 二十一、第一版优先级

### P0 必须实现

1. 用户注册登录。
2. JWT 鉴权。
3. 首页仪表盘。
4. 任务管理。
5. 工作记录。
6. 加班记录。
7. 项目管理。
8. AI 模型配置。
9. Prompt 模板管理。
10. AI 周报生成。
11. 安全运营简洁周报模板。
12. 敏感信息脱敏。
13. AI 生成历史。
14. Markdown 导出。
15. Excel 导出。
16. Docker Compose 一键部署。
17. README 部署文档。

### P1 第二阶段实现

1. Word 导出。
2. PDF 导出。
3. 团队管理。
4. 成员邀请。
5. 加班审核。
6. 团队周报。
7. 文件附件上传。
8. 报表中心增强。
9. 工作记录日历热力图。
10. AI 日报和月报。

### P2 后续增强

1. 飞书/企业微信/钉钉通知。
2. 本地 Ollama 模型部署。
3. MinIO 文件存储。
4. AI 自动提取任务。
5. AI 风险总结。
6. AI 工作记录润色。
7. 移动端独立 App。
8. 甘特图。
9. 定时自动生成周报。
10. 多团队空间。

---

## 二十二、第一版页面清单

第一版需要完成以下页面：

1. 登录页。
2. 注册页。
3. 首页仪表盘。
4. 任务管理页。
5. 工作记录页。
6. 加班记录页。
7. 项目管理页。
8. AI 周报生成页。
9. Prompt 模板管理页。
10. AI 模型配置页。
11. 报表中心页。
12. 数据统计页。
13. 系统设置页。

---

## 二十三、README 要求

README 必须包含：

1. 项目介绍。
2. 功能清单。
3. 技术栈说明。
4. 本地开发启动方式。
5. Docker 部署方式。
6. 环境变量说明。
7. 默认账号说明，如有初始化账号。
8. 数据库迁移说明。
9. AI 模型配置说明。
10. Prompt 模板说明。
11. 数据备份说明。
12. 数据恢复说明。
13. 日志查看说明。
14. 常见问题排查。
15. 目录结构说明。

---

## 二十四、开发要求

1. 请直接生成完整项目代码。
2. 保证前后端可以启动运行。
3. 保证 Docker Compose 可以一键部署。
4. 后端需要自动生成 OpenAPI / Swagger 文档。
5. 前端 API 请求需要统一封装。
6. 后端接口需要统一返回格式。
7. 表单需要基础校验。
8. 数据库迁移使用 Alembic。
9. AI Provider 需要使用适配器模式，方便扩展不同模型。
10. Prompt 渲染需要使用变量模板方式。
11. AI 调用失败需要有明确错误提示。
12. AI 生成记录需要可追溯。
13. API Key 必须加密存储。
14. 敏感信息默认脱敏。
15. 所有时间字段统一使用 ISO 格式。
16. 所有页面风格保持一致。
17. 不要只做静态页面，需要对接真实后端接口。
18. 不要省略 Docker 部署文件。
19. 不要省略 README。
20. 不要省略数据库模型和迁移文件。

---

## 二十五、最终交付标准

完成后需要满足以下标准：

1. 执行 `docker compose up -d --build` 后系统可访问。
2. 用户可以注册登录。
3. 用户可以创建任务。
4. 用户可以记录工作内容。
5. 用户可以记录加班。
6. 用户可以创建项目。
7. 用户可以配置 AI 模型。
8. 用户可以配置 Prompt 模板。
9. 用户可以选择时间范围生成 AI 周报。
10. 用户可以编辑 AI 生成结果。
11. 用户可以复制周报内容。
12. 用户可以导出 Markdown 和 Excel。
13. 首页可以展示基础统计数据。
14. 数据不会因为容器重启而丢失。
15. README 中有完整部署说明。

---

## 二十六、提交给 AI 开发工具时的补充说明

请优先实现 P0 功能，保证系统可以实际运行和 Docker 部署成功。UI 可以先做到完整可用、现代化、风格统一，不需要复杂动画。AI 周报生成页面、工作记录页面、加班记录页面、首页仪表盘是第一版重点。
