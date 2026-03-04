from typing import Any, Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class TinyFishSSEEvent(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    type: Literal["STARTED", "STREAMING_URL", "PROGRESS", "COMPLETE", "HEARTBEAT", "ERROR"]
    run_id: str | None = None
    timestamp: str | None = None
    # Event specific fields
    purpose: str | None = None
    streaming_url: str | None = None
    status: str | None = None
    result_json: dict[str, Any] | None = None
    message: str | None = None  # For errors
