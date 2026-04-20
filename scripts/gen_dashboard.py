import json
import os
from pathlib import Path
from statistics import mean

LOG_PATH = Path("data/logs.jsonl")
TEMPLATE_PATH = Path("app/static/dashboard.html")
OUTPUT_PATH = Path("dashboard.html")

def percentile(values, p):
    if not values: return 0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return items[idx]

def main():
    if not LOG_PATH.exists():
        print("No logs found. Run some tests first.")
        return

    records = []
    with LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try: records.append(json.loads(line))
            except: continue

    api_records = [r for r in records if r.get("service") == "api" and "latency_ms" in r]
    
    # Process data for charts
    raw_data = {
        "timestamps": [r["ts"][11:19] for r in api_records][-20:],
        "traffic": list(range(1, len(api_records) + 1))[-20:],
        "p50": percentile([r["latency_ms"] for r in api_records], 50),
        "p95": percentile([r["latency_ms"] for r in api_records], 95),
        "p99": percentile([r["latency_ms"] for r in api_records], 99),
        "total_cost": sum(r.get("cost_usd", 0) for r in api_records),
        "tokens_in": sum(r.get("tokens_in", 0) for r in api_records),
        "tokens_out": sum(r.get("tokens_out", 0) for r in api_records),
        "errors": {},
        "quality": [r.get("quality_score", 0) for r in api_records][-20:]
    }

    # Error breakdown
    for r in records:
        if r.get("level") == "error":
            etype = r.get("error_type", "Unknown")
            raw_data["errors"][etype] = raw_data["errors"].get(etype, 0) + 1

    # Inject into template
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    final_html = template.replace("/* DATA_JSON */ {}", json.dumps(raw_data))
    
    OUTPUT_PATH.write_text(final_html, encoding="utf-8")
    print(f"Dashboard generated successfully: {OUTPUT_PATH.absolute()}")

if __name__ == "__main__":
    main()
