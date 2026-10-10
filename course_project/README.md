# 课程贯穿项目：组会纪要与行动项

这是第 3–10 周共用的学生起始代码库。应用提供最小的组会纪要 REST API，功能刻意保持有限，供每周逐步扩展。

## 环境

建议 Python 3.10 或更新版本。

以下命令请在 `course_project` 目录内执行。

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 启动与检查

```bash
python -m uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000/docs` 查看当前 API。健康检查为 `GET /health`；纪要列表和创建接口分别为 `GET /notes`、`POST /notes`。

数据仅保存在进程内存中，重启服务后会清空。这个起始项目不适合存放真实会议记录或个人信息。

