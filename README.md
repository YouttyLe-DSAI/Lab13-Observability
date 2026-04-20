# Day 13 Observability Lab Template

Template repo for a 4-hour hands-on lab on Monitoring, Logging, and Observability.

## What students will build

A small FastAPI "agent" instrumented with:
- structured JSON logging
- correlation ID propagation
- PII scrubbing
- Langfuse tracing
- minimal metrics aggregation
- SLOs, alerts, and a blueprint report

This template is intentionally incomplete. Teams are expected to finish TODOs during the lab.

## Suggested lab flow (Gapped Template)

1. **Run the starter app**: Observe that logs are basic and correlation IDs are missing.
2. **Implement Correlation IDs**: Fix `app/middleware.py` so every request has a unique `x-request-id`.
3. **Enrich Logs**: Update `app/main.py` to bind user, session, and feature context to every log.
4. **Sanitize Data**: Implement the PII scrubber in `app/logging_config.py`.
5. **Verify with Script**: Run `python scripts/validate_logs.py` to check your progress.
6. **Tracing**: Send 10-20 requests and verify traces in Langfuse (ensure `observe` decorator is used).
7. **Dashboards**: Build your 6-panel dashboard from exported metrics.
8. **Alerting**: Configure alert rules in `config/alert_rules.yaml` and test them.

## 🛠 Quick Start (Running the Lab)

### 1. Setup Environment
```bash
# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup API Key (Add your OPENAI_API_KEY to .env)
cp .env.example .env
```

### 2. Run the Server
```bash
# Start the FastAPI server
uvicorn app.main:app
```

### 3. Automated Lab Execution
Chạy toàn bộ quy trình từ Load Test, Benchmark đến Dashboard chỉ với 1 câu lệnh:
```bash
python scripts/run_full_lab.py
```

## 🔍 Advanced Tooling

### Generate Traffic
```bash
# Run load test with specific concurrency and limit
python scripts/load_test.py --concurrency 4 --limit 10
```

### Mock Incidents (System Failures)
```bash
# Simulate RAG Latency
python scripts/inject_incident.py --scenario rag_slow
# Simulate API Outage (System Error)
python scripts/inject_incident.py --scenario api_outage
# Disable all incidents
python scripts/inject_incident.py --scenario rag_slow --disable
```

### Monitoring & Dashboard
- **SRE Dashboard (Real-time)**: [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Technical Evidence**: [http://127.0.0.1:8000/static/evidence.html](http://127.0.0.1:8000/static/evidence.html)

## Repo map

```text
app/
  main.py                FastAPI app
  agent.py               core agent pipeline
  logging_config.py      structlog config
  middleware.py          correlation ID middleware
  pii.py                 scrubbing helpers
  tracing.py             Langfuse helpers
  schemas.py             request/response/log models
  metrics.py             in-memory metrics helpers
  incidents.py           toggles for injected failures
  mock_llm.py            deterministic fake LLM
  mock_rag.py            deterministic fake retrieval
config/
  slo.yaml               starter SLOs
  alert_rules.yaml       starter alerts
  logging_schema.json    expected log schema
scripts/
  load_test.py           generate requests
  inject_incident.py     flip incident toggles
  validate_logs.py       schema checks for logs
data/
  sample_queries.jsonl   requests for testing
  expected_answers.jsonl starter quality checks
  incidents.json         scenario descriptions
  logs.jsonl             app output target
  audit.jsonl            optional audit log output

docs/
  blueprint-template.md  team submission template
  alerts.md              runbook + alert worksheet
  dashboard-spec.md      6-panel dashboard checklist
  grading-evidence.md    evidence collection sheet
  mock-debug-qa.md       oral/written debugging questions
```

## Team role suggestion

- Member A: logging + PII
- Member B: tracing + tags
- Member C: SLO + alerts
- Member D: load test + incident injection
- Member E: dashboard + evidence
- Member F: blueprint + demo lead

## Grading policy (60/40 Split)

Your final grade is calculated as follows:

1. **Group Score (60%)**: 
   - **Technical Implementation (30 pts)**: Verified by `validate_logs.py` and live system state.
   - **Incident Response (10 pts)**: Accuracy of your root cause analysis in the report.
   - **Live Demo (20 pts)**: Team presentation and system demonstration.
2. **Individual Score (40%)**:
   - **Individual Report (20 pts)**: Quality of your specific contributions in `docs/blueprint-template.md`.
   - **Git Evidence (20 pts)**: Traceable work via commits and code ownership.

**Passing Criteria**: 
- All `TODO` blocks must be completed.
- Minimum of 10 traces must be visible in Langfuse.
- Dashboard must show all 6 required panels.
