from __future__ import annotations

import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

try:
    # Trong v4, observe nằm trực tiếp ở langfuse
    from langfuse import observe
    HAS_LANGFUSE = True
except Exception as e:
    HAS_LANGFUSE = False
    print(f"⚠️ Tracing disabled: {e}")

if not HAS_LANGFUSE:
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY") and HAS_LANGFUSE)
