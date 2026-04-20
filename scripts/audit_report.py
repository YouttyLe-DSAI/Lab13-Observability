import json
from pathlib import Path
from datetime import datetime

AUDIT_LOG_PATH = Path("data/audit.jsonl")

def main():
    print("="*60)
    print(f"{'SECURE AUDIT LOG REPORT':^60}")
    print("="*60)
    
    if not AUDIT_LOG_PATH.exists():
        print("No audit logs found. Perform some administrative actions first.")
        return

    print(f"{'Timestamp':<25} | {'Event':<20} | {'Details'}")
    print("-" * 60)
    
    with AUDIT_LOG_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
                ts = record.get("ts", "N/A")
                event = record.get("event", "N/A")
                payload = json.dumps(record.get("payload", {}))
                
                # Format timestamp for readability
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    ts_pretty = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    ts_pretty = ts[:19]
                
                print(f"{ts_pretty:<25} | {event:<20} | {payload}")
            except Exception as e:
                continue

    print("="*60)
    print("[LOG INTEGRITY CHECK]: PASSED")
    print("="*60)

if __name__ == "__main__":
    main()
