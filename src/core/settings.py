from pydantic import BaseModel, ConfigDict, Field


class RpcSettings(BaseModel):
    model_config = ConfigDict(frozen=True)

    update_interval: float = Field(default=2.0, ge=1.0, le=30.0)
    seek_tolerance_seconds: float = Field(default=5.0, ge=1.0, le=60.0)
