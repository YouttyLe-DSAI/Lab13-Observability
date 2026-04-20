from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from structlog.contextvars import bind_contextvars

from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json

from .agent import LabAgent
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger, log_audit_event
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import tracing_enabled

configure_logging()
log = get_logger()
app = FastAPI(title="Day 13 Observability Lab")
app.add_middleware(CorrelationIdMiddleware)

# Mount static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse(STATIC_DIR / "dashboard.html")

agent = LabAgent()

LOG_FILE_PATH = Path("data/logs.jsonl")

def calculate_percentile(values, p):
    if not values: return 0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return items[idx]


@app.on_event("startup")
async def startup() -> None:
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        payload={"tracing_enabled": tracing_enabled()},
    )


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/dashboard/data")
async def dashboard_data() -> dict:
    if not LOG_FILE_PATH.exists():
        return {"timestamps": [], "traffic": [], "p50": 0, "p95": 0, "p99": 0, "total_cost": 0, "tokens_in": 0, "tokens_out": 0, "errors": {}, "quality": []}

    records = []
    with LOG_FILE_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except:
                continue

    api_records = [r for r in records if r.get("service") == "api" and "latency_ms" in r]
    
    # Process data for charts (last 30 points)
    window = api_records[-30:]
    
    errors = {}
    for r in records:
        if r.get("level") == "error":
            etype = r.get("error_type", "Unknown")
            errors[etype] = errors.get(etype, 0) + 1

    return {
        "timestamps": [r["ts"][11:19] for r in window],
        "traffic": list(range(len(api_records) - len(window) + 1, len(api_records) + 1)),
        "p50": calculate_percentile([r["latency_ms"] for r in api_records], 50),
        "p95": calculate_percentile([r["latency_ms"] for r in api_records], 95),
        "p99": calculate_percentile([r["latency_ms"] for r in api_records], 99),
        "total_cost": sum(r.get("cost_usd", 0) for r in api_records),
        "tokens_in": sum(r.get("tokens_in", 0) for r in api_records),
        "tokens_out": sum(r.get("tokens_out", 0) for r in api_records),
        "errors": errors,
        "quality": [r.get("quality_score", 0) for r in window]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    # Enrich logs with request context (user_id_hash, session_id, feature, model, env)
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=body.session_id,
        feature=body.feature,
        model=agent.model,
        turbo_mode=body.turbo_mode,
        env=os.getenv("APP_ENV", "dev"),
    )
    
    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
            turbo_mode=body.turbo_mode,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc


@app.post("/incidents/{name}/enable")
async def enable_incident(name: str) -> JSONResponse:
    try:
        enable(name)
        log_audit_event("incident_enabled", {"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(name: str) -> JSONResponse:
    try:
        disable(name)
        log_audit_event("incident_disabled", {"name": name})
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
