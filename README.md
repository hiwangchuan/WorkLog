# WorkLog AI

WorkLog AI 是面向个人和小团队的工作任务、工作记录、加班工时统计与 AI 周报生成系统。第一版优先完成个人使用闭环，并在数据库、接口和 UI 中预留团队、角色、权限和审批扩展能力。

## 功能清单

- 用户注册、登录、JWT 鉴权、修改密码、当前用户信息。
- 首页仪表盘：待办、完成数、月工时、月加班、超期任务、趋势图和近期记录。
- 任务管理：列表、看板、日历视图、状态/优先级/截止日期/工时。
- 工作记录：时间线、表格、模板快速填写、工时自动计算、保存并继续。
- 加班记录：类型、审核状态、调休字段、提交/审批字段预留。
- 项目管理：项目 CRUD、任务和工时归集字段。
- AI 周报：模型配置、Prompt 模板、敏感信息脱敏、输入快照、Prompt 留痕、历史记录、最终版本编辑。
- 报表导出：Markdown、Excel、Word、PDF。
- 数据统计：工时、任务、项目、加班、工作类型和记录热力。
- Docker Compose 一键部署，Nginx 统一入口。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Naive UI、Pinia、Vue Router、Axios、ECharts。
- 后端：Python、FastAPI、SQLAlchemy、Alembic、Pydantic、JWT、Passlib、Pandas、OpenPyXL、python-docx、ReportLab。
- 数据库与中间件：PostgreSQL、Redis。
- 部署：Docker、Docker Compose、Nginx。

## 本地开发

后端：

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://worklog:worklog-password@localhost:5432/worklog
export REDIS_URL=redis://localhost:6379/0
alembic upgrade head
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

本地前端默认访问 `http://localhost:5173`，API 代理到 `http://127.0.0.1:8000`。

## Docker 部署

```bash
cp .env.example .env
# 修改 .env 中的 CONTAINER_PREFIX、POSTGRES_PASSWORD、JWT_SECRET_KEY、CONFIG_ENCRYPTION_KEY、HOST_PORT
docker compose up -d --build
```

访问地址：

```text
http://服务器IP:HOST_PORT
```

后端 Swagger：

```text
http://服务器IP:HOST_PORT/api/docs
```

## 环境变量

关键变量：

- `CONTAINER_PREFIX`：容器名前缀，默认 `worklog`。同机部署测试环境时必须换成独立值。
- `HOST_PORT`：宿主机暴露端口，默认 `8080`。
- `POSTGRES_PASSWORD`：PostgreSQL 密码。
- `DATABASE_URL`：后端数据库连接。
- `REDIS_URL`：Redis 连接。
- `JWT_SECRET_KEY`：JWT 签名密钥。
- `CONFIG_ENCRYPTION_KEY`：AI API Key 加密密钥。
- `CORS_ORIGINS`：允许的前端来源。

`.env` 不应提交到代码仓库。

## 默认账号

系统不内置默认账号。首次访问注册页面创建账号即可使用。

## AI 模型配置

进入「系统设置 -> AI 模型配置」新增模型：

- OpenAI Compatible：填写 `Base URL`、`API Key`、`Model Name`。
- OpenAI、DeepSeek、通义千问、智谱等兼容 `/chat/completions` 的接口可按 OpenAI Compatible 配置。
- Ollama：Provider 选择 `ollama`，Base URL 默认可用 `http://ollama:11434` 或你自己的 Ollama 地址。

API Key 使用 Fernet 派生密钥加密存储，列表只展示掩码。

没有配置 AI 模型时，AI 周报页面会使用本地规则生成，保证第一版可直接使用。

## Prompt 模板

系统启动后会自动初始化 8 个 Prompt 模板，包括「安全运营简洁周报」。模板支持变量：

```text
{work_logs} {tasks} {overtime_logs} {projects} {date_start} {date_end}
{output_format} {manual_extra_content} {number_style} {group_by_category}
{only_work_items} {include_overtime} {include_next_week_plan}
```

## 数据库迁移

容器启动时自动执行：

```bash
alembic upgrade head
```

手动执行：

```bash
docker compose exec backend alembic upgrade head
```

## 备份与恢复

升级前推荐使用内置脚本自动备份数据库和文件目录：

```bash
./scripts/backup.sh ./.env
```

无损升级流程：

```bash
git pull
./scripts/upgrade.sh ./.env
```

脚本会先备份 PostgreSQL 数据和 `data/uploads`、`data/exports`、`data/certs`，再构建镜像、启动容器并执行 Alembic 迁移。迁移文件只做增量变更，不会删除已有业务数据。

备份数据库：

```bash
mkdir -p ./data/backups
docker exec worklog-postgres pg_dump -U worklog worklog > ./data/backups/worklog_$(date +%F).sql
```

恢复数据库：

```bash
cat ./data/backups/worklog_2026-06-16.sql | docker exec -i worklog-postgres psql -U worklog -d worklog
```

上传文件、导出文件和证书目录位于：

```text
data/uploads
data/exports
data/certs
```

升级容器：

```bash
docker compose pull
docker compose up -d --build
```

清理数据卷前必须确认已有备份：

```bash
docker compose down -v
```

该命令会删除 PostgreSQL 和 Redis 数据卷。

## 日志查看

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
```

## 隔离测试环境

同一台服务器上部署测试环境时，不复用生产路径、容器名、端口和数据卷：

```bash
cp deploy/staging.env.example .env.staging
# 修改 .env.staging 中的密码、密钥和 HOST_PORT
docker compose --env-file .env.staging up -d --build
```

建议测试部署路径与生产分离，例如：

```text
/root/App/WorkLog-Staging
```

默认测试端口示例为 `18081`。生产环境继续使用自己的 `.env` 和 `CONTAINER_PREFIX=worklog`。

## 常见问题

- 前端能打开但 API 失败：检查 `nginx`、`backend` 容器状态和 `/api/health`。
- AI 生成失败：检查 API Key、Base URL、模型名称和服务器网络。
- Docker 端口冲突：修改 `.env` 中 `HOST_PORT`。
- 数据库连接失败：检查 `POSTGRES_PASSWORD` 与 `DATABASE_URL` 是否一致。

## 目录结构

```text
backend/   FastAPI 后端、Alembic 迁移和 AI/报表服务
frontend/  Vue 3 前端应用
nginx/     统一反向代理配置
data/      上传、导出、日志、证书和备份目录
```
