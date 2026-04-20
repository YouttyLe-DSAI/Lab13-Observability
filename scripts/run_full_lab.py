import subprocess
import time
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def run_cmd(cmd, description):
    print(f"\n>>> {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    print("="*60)
    print(f"{'AUTOMATED LAB EXECUTION PIPELINE':^60}")
    print("="*60)

    # 1. Validation
    if not os.getenv("OPENAI_API_KEY"):
        print("CRITICAL: OPENAI_API_KEY not found in environment.")
        sys.exit(1)

    # 2. Baseline Load Test (Reduced)
    run_cmd("python scripts/load_test.py --concurrency 4", "Running fast baseline load test")

    # 3. Cost Benchmarking (Optimized)
    run_cmd("python scripts/cost_bench.py", "Running cost optimization benchmark")

    # 4. Incident Injection & System Error Mock
    run_cmd("python scripts/inject_incident.py --scenario rag_slow", "Injecting LATENCY: RAG_SLOW")
    run_cmd("python scripts/load_test.py --concurrency 2", "Sampling latency logs...")
    run_cmd("python scripts/inject_incident.py --scenario rag_slow", "Disabling RAG_SLOW")

    run_cmd("python scripts/inject_incident.py --scenario api_outage", "Injecting SYSTEM ERROR: API_OUTAGE")
    run_cmd("python scripts/load_test.py --concurrency 2", "Sampling error logs...")
    run_cmd("python scripts/inject_incident.py --scenario api_outage", "Restoring System")

    # 5. Result Verification
    run_cmd("python scripts/validate_logs.py", "Verifying log schema and PII")
    run_cmd("python scripts/audit_report.py", "Generating audit trail report")

    # 6. Dashboard Generation
    run_cmd("python scripts/gen_dashboard.py", "Generating professional dashboard")

    print("\n" + "="*60)
    print(f"{'LAB COMPLETION SUCCESSFUL':^60}")
    print("="*60)
    print("Next steps:")
    print("1. View 'dashboard.html' for visual insights.")
    print("2. Check 'data/logs.jsonl' for raw data.")
    print("3. Review 'audit.jsonl' for security trail.")

if __name__ == "__main__":
    main()
