<!-- .github/copilot-instructions.md - guidance for AI coding agents -->
# Copilot 指令（针对本仓库）

目的：让 AI 编码代理快速在此仓库中开展工作、理解约定并做出安全且一致的更改。

快速概览
- 主入口：`main.py`（当前只是 bootstrap 打印）。
- 声明的运行时/依赖见：`pyproject.toml`（FastAPI, Uvicorn, SQLAlchemy, Pydantic）。
- README 很短，仅说明项目名称；仓库当前为最小骨架。

已发现的架构与意图（可被代理安全依赖）
- 技术栈：后端 API 风格的栈（FastAPI + Uvicorn）与关系型 ORM（SQLAlchemy）以及 Pydantic 用于数据校验——见 `pyproject.toml` 的 `dependencies`。
- 当前代码：`main.py` 仅打印引导信息，尚未包含 FastAPI 应用实例或 ORM 配置；因此任何引入 API/DB 的改动都将是新增内容而非替换。

开发/运行工作流（可验证/执行的命令）
- 快速验证仓库骨架：运行

```powershell
python main.py
```

 这应输出引导消息。
- 安装依赖（本仓库使用 `pyproject.toml` 列出依赖）：

```powershell
python -m pip install -e .
# 或者安装最小运行依赖
python -m pip install fastapi uvicorn sqlalchemy pydantic
```

- 典型 FastAPI 运行（在添加 FastAPI 应用后）：

```powershell
uvicorn app.main:app --reload --port 8000
```

 约定与项目特性（从代码可发现）
- 目前未强制的文件布局，但若引入 API，请按照常见约定：把 FastAPI 实例放在 `app/main.py`（导出 `app` 对象），路由在 `app/routes/`，模型在 `app/models/`，Pydantic schema 在 `app/schemas/`。
- ORM 与迁移：仓库未包含迁移工具或 DB 配置；如果新增数据库支持，请把连接/会话初始化放入 `app/db.py` 并尽量使用 SQLAlchemy 的 SessionLocal/engine 模式。

安全与变更策略（针对 AI 代理）
- 不要在无测试和无运行验证的情况下修改生产关键逻辑；本仓库当前可在本地通过 `python main.py` 验证基础改动。
- 对于新增依赖，更新 `pyproject.toml` 的 `dependencies` 并在提交说明中列出变更。

示例任务与示例实现片段（可直接应用）
- 任务：添加 FastAPI 应用骨架。
  - 在 `app/main.py` 中创建：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
```

  - 运行：`uvicorn app.main:app --reload`，访问 `http://localhost:8000/health`。

- 任务：保持最小破坏性——不要移除 `main.py`；若替换入口，保留旧入口或添加迁移说明。

查阅文件（重要参考）
- 仓库根：`main.py`（启动脚本示例）
- 依赖声明：`pyproject.toml`
- 说明文档：`README.md`

沟通与反馈
- 如果某些实现需外部凭据（数据库、第三方 API），在未获得凭据前只实现可本地化运行（mock / in-memory）。
- 我已基于可发现信息草拟本指令；如果你希望我把仓库从骨架扩展为完整 FastAPI 服务，我可以继续实现并添加测试与 CI 配置。

---
请查看并指出任何缺失的上下文或偏好（例如希望采用的文件布局或测试框架），我会据此迭代此文档。
