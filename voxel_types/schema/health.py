""" Author: Charlie

健康检查响应模型：根探针、存活探针与就绪探针。
"""

from voxel_types.schema.base import ApiSchema
from voxel_types.schema.wire import WireFlag


class RootHealthResponse(ApiSchema):
    """根健康检查响应结构（对齐 voxel-boot RootController data.name）。"""

    name: str


class LiveHealthResponse(ApiSchema):
    """存活探针响应结构。"""

    status: str


class HealthCheckItem(ApiSchema):
    """单个基础设施组件的就绪检查结果。"""

    enabled: WireFlag
    ok: WireFlag
    detail: str | None = None


class ReadyChecksResponse(ApiSchema):
    """聚合基础设施检查结果。"""

    database: HealthCheckItem
    redis: HealthCheckItem
    config_sync: HealthCheckItem
    storage: HealthCheckItem


class ReadyHealthResponse(ApiSchema):
    """就绪探针响应结构。"""

    status: str
    checks: ReadyChecksResponse
