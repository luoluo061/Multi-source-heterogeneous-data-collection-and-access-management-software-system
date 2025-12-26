# Multi-source heterogeneous data collection and access management system

一个可运行的 FastAPI MVP，用于多源异构数据的统一接入、调度、格式识别、基础校验、日志追踪与原始数据存储，覆盖 HTTP API、本地文件扫描、SQLite 三类数据源。

## 目录结构
```
app/
  api/            # FastAPI 路由
  adapters/       # 数据源适配器（http/file/sqlite）
  core/           # 配置、日志、错误类型
  models/         # SQLAlchemy 表定义与会话
  schemas/        # Pydantic 模型（API 层）
  services/       # 接入编排与业务流程
  scheduler/      # 定时调度器
  storage/        # 原始数据持久化
  validation/     # 格式识别与基础校验
main.py           # 运行入口（uvicorn 调起 app.main:app）
pyproject.toml    # 依赖与构建配置
```

## 快速启动
1. 安装依赖（可编辑模式）：
   ```bash
   pip install -e .
   ```
2. 启动 API（默认 8000 端口）：
   ```bash
   uvicorn app.main:app --reload
   ```
3. 日志输出到控制台与 `./logs/app.log`，SQLite 数据默认在 `./data/app.db`。

示例数据：
- `./data/sample.csv`
- `./data/example_source.db` (表 `metrics`)

## API 示例（curl）
创建 HTTP API 数据源：
```bash
curl -X POST http://localhost:8000/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jsonplaceholder post",
    "type": "HTTP_API",
    "enabled": true,
    "params": {"url": "https://jsonplaceholder.typicode.com/posts/1"},
    "schedule": {"interval_seconds": 60}
  }'
```

创建文件扫描数据源：
```bash
curl -X POST http://localhost:8000/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "local csv scan",
    "type": "FILE",
    "enabled": true,
    "params": {"directory": "./data", "pattern": "*.csv"}
  }'
```

创建 SQLite 数据源：
```bash
curl -X POST http://localhost:8000/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sqlite metrics",
    "type": "SQLITE",
    "enabled": true,
    "params": {"db_path": "./data/example_source.db", "table": "metrics"}
  }'
```

手动触发一次接入（替换 SOURCE_ID）：
```bash
curl -X POST "http://localhost:8000/runs/trigger?source_id=SOURCE_ID"
```

查看任务状态（替换 RUN_ID）：
```bash
curl http://localhost:8000/runs/RUN_ID
```

查看原始记录列表：
```bash
curl "http://localhost:8000/records?run_id=RUN_ID"
```

## 测试
```bash
pytest -q
```

## 设计要点
- 模块化：适配器/编排/调度/校验/存储边界清晰，便于扩展新的源或校验逻辑。
- 日志：统一格式包含 `run_id` 与 `source_id`，便于追踪全链路。
- 校验：非空、大小限制、JSON/CSV 解析可用性，简单结构检查。
- 存储：原始载荷、校验状态、checksum 与 format/raw_size 均入库，支撑追溯。
