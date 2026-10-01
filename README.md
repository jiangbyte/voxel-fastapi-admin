# Voxel FastAPI Admin

管理端 Python 后端（FastAPI），扁平 xfg-ddd（**无 `src/`**）：

`voxel_types/`（types 层；避免遮蔽标准库 `types`）· `api/` · `domain/` · `infrastructure/` · `cases/` · `trigger/` · `app/`

仅 `/api/v1/admin/**`。默认端口 `8100`。

```bash
uvicorn app.main:app --port 8100
python -c "import domain, cases, trigger, infrastructure, api, types, app"
```
