"""加载基础设施层任务处理器（避免 application 依赖 infrastructure）。"""

_loaded = False


def load_infrastructure_handlers() -> None:
    """导入 infra / 跨 BC 任务模块，触发 @job_handler 注册。"""
    global _loaded
    if _loaded:
        return
    _loaded = True
    from infrastructure.iam.jobs import (
        account_tasks as _account,  # noqa: F401
    )
    from infrastructure.sys.audit import (
        task_handlers as _audit,  # noqa: F401
    )
    from infrastructure.sys.banner import (
        task_handlers as _banner,  # noqa: F401
    )
    from infrastructure.sys.job import handlers as _job  # noqa: F401
