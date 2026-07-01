from __future__ import annotations
import os
import threading
import time
import webbrowser
import json
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

_CRITICAL_EVENTS = {"debug_detected", "audit_tamper", "challenge_fail"}
_HIGH_EVENTS = {"license_reject", "license_fail", "tpm_mismatch", "behavior_anomaly", "tpm_policy_fail"}
_MEDIUM_EVENTS = {"behavior_check", "boot_counter_regression", "heartbeat_stale"}

def _classify_severity(event: str) -> str:
    e = event.lower().replace("-", "_")
    if e in _CRITICAL_EVENTS or any(k in e for k in ("debug", "tamper", "clone")):
        return "critical"
    if e in _HIGH_EVENTS or any(k in e for k in ("reject", "fail", "mismatch", "anomaly", "policy_fail")):
        return "high"
    if e in _MEDIUM_EVENTS or any(k in e for k in ("behavior", "drift", "counter", "heartbeat_stale", "stale")):
        return "medium"
    return "info"


def review_audit_logs(audit_log_path: str, port: int = 8080) -> None:
    """
    Vendor Dashboard Server.
    Serves the React UI and provides an API to read real audit logs.
    """
    app = Flask(__name__, static_folder=None)
    CORS(app)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ui_dist_dir = os.path.join(current_dir, 'ui', 'dist')

    @app.route("/api/logs")
    def get_logs():
        path = Path(audit_log_path)
        if not path.exists():
            return jsonify([])
        
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            logs = []
            for i, line in enumerate(lines):
                try:
                    entry = json.loads(line)
                    # Flatten for easier UI consumption
                    logs.append({
                        "id": i,
                        "timestamp": entry.get("ts", ""),
                        "event": entry.get("event", ""),
                        "payload": entry.get("payload", {}),
                        "hash": entry.get("entry_hash", ""),
                        "severity": _classify_severity(entry.get("event", ""))
                    })
                except Exception:
                    continue
            return jsonify(logs[::-1]) # Return newest first
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/logs/ingest", methods=["POST"])
    def ingest_logs():
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        logs = data.get("logs", [])
        if not isinstance(logs, list):
            return jsonify({"error": "logs must be a list"}), 400

        machine_id = data.get("machine_id")
        path = Path(audit_log_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        written = 0
        with path.open("a", encoding="utf-8") as f:
            for log in logs:
                if not isinstance(log, dict):
                    continue
                if machine_id:
                    pl = dict(log.get("payload") or {})
                    pl.setdefault("_sync_machine", machine_id)
                    log = {**log, "payload": pl}
                f.write(json.dumps(log, sort_keys=False) + "\n")
                written += 1

        return jsonify({"status": "ok", "count": written})

    def _load_logs():
        path = Path(audit_log_path)
        if not path.exists():
            return []
        lines = path.read_text(encoding="utf-8").splitlines()
        result = []
        for line in lines:
            try:
                result.append(json.loads(line))
            except Exception:
                continue
        return result

    @app.route("/api/overview")
    def get_overview():
        logs = _load_logs()
        counts = {"critical": 0, "high": 0, "medium": 0, "info": 0}
        by_hour: dict[str, int] = {}
        by_day: dict[str, int] = {}
        events_feed = []
        for entry in logs:
            sev = _classify_severity(entry.get("event", ""))
            counts[sev] = counts.get(sev, 0) + 1
            ts = entry.get("ts", "")
            if ts:
                try:
                    from datetime import datetime, timezone
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    hour_label = dt.strftime("%H:00")
                    day_label = dt.strftime("%b %d")
                    by_hour[hour_label] = by_hour.get(hour_label, 0) + 1
                    by_day[day_label] = by_day.get(day_label, 0) + 1
                except Exception:
                    pass
            events_feed.append({
                "id": len(events_feed),
                "message": entry.get("event", ""),
                "severity": _classify_severity(entry.get("event", "")),
                "timestamp": ts,
                "payload": entry.get("payload", {}),
            })
        total = len(logs)
        blacklisted = counts.get("critical", 0)
        suspicious = counts.get("high", 0)
        safe = max(0, total - blacklisted - suspicious)
        return jsonify({
            "stats": {
                "total_events": total,
                "blacklisted": blacklisted,
                "suspicious": suspicious,
                "safe": safe,
            },
            "activity_by_hour": [{"time": k, "activity": v} for k, v in sorted(by_hour.items())],
            "threat_by_day": [{"date": k, "count": v} for k, v in sorted(by_day.items())],
            "recent_events": events_feed[::-1][:20],
        })

    @app.route("/api/clients")
    def get_clients():
        logs = _load_logs()
        # Build a per-fingerprint summary from log payloads
        clients: dict[str, dict] = {}
        for entry in logs:
            payload = entry.get("payload", {})
            fp = payload.get("hardware_fingerprint") or payload.get("license_id")
            if not fp:
                continue
            if fp not in clients:
                clients[fp] = {
                    "id": fp[:8].upper(),
                    "license": payload.get("license_id", "N/A"),
                    "hardware_fingerprint": fp,
                    "events": 0,
                    "critical_events": 0,
                    "last_seen": entry.get("ts", ""),
                    "status": "safe",
                }
            c = clients[fp]
            c["events"] += 1
            sev = _classify_severity(entry.get("event", ""))
            if sev == "critical":
                c["critical_events"] += 1
            c["last_seen"] = entry.get("ts", c["last_seen"])
            if c["critical_events"] >= 2:
                c["status"] = "blacklisted"
            elif c["critical_events"] >= 1:
                c["status"] = "suspicious"
            c["risk"] = min(100, c["critical_events"] * 30 + (c["events"] - c["critical_events"]) * 5)
        return jsonify(list(clients.values()))

    @app.route("/api/blacklist")
    def get_blacklist():
        logs = _load_logs()
        blacklist: dict[str, dict] = {}
        for entry in logs:
            sev = _classify_severity(entry.get("event", ""))
            if sev not in ("critical", "high"):
                continue
            payload = entry.get("payload", {})
            fp = payload.get("hardware_fingerprint") or payload.get("license_id") or "unknown"
            if fp not in blacklist:
                blacklist[fp] = {
                    "id": fp[:8].upper(),
                    "hardware_fingerprint": fp,
                    "license": payload.get("license_id", "N/A"),
                    "reason": entry.get("event", ""),
                    "events": 0,
                    "first_seen": entry.get("ts", ""),
                    "last_seen": entry.get("ts", ""),
                }
            blacklist[fp]["events"] += 1
            blacklist[fp]["last_seen"] = entry.get("ts", "")
        return jsonify(list(blacklist.values()))

    @app.route("/api/risk")
    def get_risk():
        logs = _load_logs()
        category_map = {
            "Tampering": ["tamper", "reject", "fail"],
            "Debugger": ["debug"],
            "VM/Clone": ["clone", "counter"],
            "Hardware": ["mismatch", "hardware"],
            "Anomaly": ["anomaly", "drift", "behavior"],
        }
        categories: dict[str, int] = {k: 0 for k in category_map}
        by_day: dict[str, int] = {}
        for entry in logs:
            ev = entry.get("event", "").lower()
            for cat, keywords in category_map.items():
                if any(k in ev for k in keywords):
                    categories[cat] += 1
            ts = entry.get("ts", "")
            if ts:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    day = dt.strftime("%b %d")
                    by_day[day] = by_day.get(day, 0) + 1
                except Exception:
                    pass
        total = len(logs)
        critical = sum(1 for e in logs if _classify_severity(e.get("event", "")) == "critical")
        risk_score = min(100, int((critical / max(total, 1)) * 100 * 3 + len(logs) * 0.1))
        return jsonify({
            "stats": {
                "global_risk_score": risk_score,
                "total_threats": total,
                "critical_count": critical,
            },
            "threat_categories": [{"category": k, "count": v} for k, v in categories.items()],
            "risk_trend": [{"date": k, "score": v} for k, v in sorted(by_day.items())],
        })

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if not os.path.exists(ui_dist_dir):
            return f"Error: UI dist directory not found at {ui_dist_dir}. Please run 'npm run build' in the UI folder.", 404
            
        if path != "" and os.path.exists(os.path.join(ui_dist_dir, path)):
            return send_from_directory(ui_dist_dir, path)
        else:
            return send_from_directory(ui_dist_dir, 'index.html')

    print(f"[*] Starting CertiGuard Dashboard on http://localhost:{port}")
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=port, debug=False)
