import hashlib
import json
from uuid import UUID

from ..schemas.agent_tasks import AgentTaskCreate


def generate_request_hash(
    *,
    user_id: UUID,
    request: AgentTaskCreate,
) -> str:

    # Normalize Pydantic data into JSON-compatible values.
    request_data = request.model_dump(mode="json")

    # Only include fields that determine the actual task execution.
    payload = {
        "version": 1,
        "user_id": str(user_id),
        "merchant_id": str(request.merchant_id),
        "task_type": request_data["task_type"],
        "prompt": request_data["prompt"],
        "input_data": request_data.get("input_data"),
    }

    # Generate deterministic JSON.
    canonical_request = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )

    # Generate SHA-256 digest.
    return hashlib.sha256(
        canonical_request.encode("utf-8")
    ).hexdigest()