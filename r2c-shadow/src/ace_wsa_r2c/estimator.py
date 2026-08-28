from __future__ import annotations
import json, math
from typing import Any

def estimate_tokens(value: Any) -> int:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return max(1, math.ceil(len(text) / 3.5))
