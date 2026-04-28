import os
from collections import deque
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse

# API routes with /api/v1 prefix
router = APIRouter(prefix="/api/v1", tags=["monitor"])

# UI routes without prefix
router_ui = APIRouter(tags=["ui"], include_in_schema=False)


@router.get("/monitor")
def monitor(request: Request) -> JSONResponse:
    app = request.app
    monitor_state = getattr(app.state, "monitor", None) or {}
    requests = list(monitor_state.get("requests", deque()))

    # task stats
    ctx = getattr(app.state, "ctx", None)
    tasks_info: dict[str, Any] = {}
    if ctx is not None:
        try:
            tasks = [t.as_dict() for t in ctx.tasks.list()]
            counts = {"queued": 0, "processing": 0, "done": 0, "failed": 0}
            for t in tasks:
                st = t.get("status")
                counts.setdefault(st, 0)
                counts[st] = counts.get(st, 0) + 1
            tasks_info = {
                "max_workers": ctx.settings.max_workers,
                "total_tasks": len(tasks),
                "counts": counts,
            }
        except Exception:
            tasks_info = {"error": "unable to read task manager"}

    # system load (best-effort)
    sys_info = {}
    try:
        if hasattr(os, "getloadavg"):
            load1, load5, load15 = os.getloadavg()
            sys_info["loadavg"] = {"1m": load1, "5m": load5, "15m": load15}
    except Exception:
        pass

    # process-level metrics via psutil if available
    try:
        import psutil

        proc = psutil.Process()
        mem = proc.memory_info()
        cpu_percent = proc.cpu_percent(interval=0.1)
        sys_info["process"] = {
            "rss_bytes": mem.rss,
            "vms_bytes": mem.vms,
            "cpu_percent": cpu_percent,
        }
    except Exception:
        pass

    payload = {
        "recent_requests": list(reversed(requests))[:200],
        "tasks": tasks_info,
        "system": sys_info,
    }
    return JSONResponse(payload)


@router_ui.get("/docs", response_class=HTMLResponse)
def monitor_docs() -> str:
    """Serve custom monitor dashboard instead of Swagger UI."""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ResoCall Monitor</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                color: white;
                margin-bottom: 30px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.3s ease;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .card h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.3em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .metric {
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
            }
            .metric-label {
                font-weight: 600;
                color: #333;
            }
            .metric-value {
                color: #667eea;
                font-weight: 700;
                font-size: 1.1em;
            }
            .status-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 0.85em;
                font-weight: 600;
            }
            .status-queued { background: #ffc107; color: #333; }
            .status-processing { background: #17a2b8; color: white; }
            .status-done { background: #28a745; color: white; }
            .status-failed { background: #dc3545; color: white; }
            .requests-section {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .requests-section h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.3em;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.9em;
            }
            th {
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }
            tr:hover {
                background: #f8f9fa;
            }
            .method-get { color: #28a745; font-weight: 600; }
            .method-post { color: #007bff; font-weight: 600; }
            .method-put { color: #fd7e14; font-weight: 600; }
            .method-delete { color: #dc3545; font-weight: 600; }
            .status-2xx { color: #28a745; font-weight: 600; }
            .status-4xx { color: #fd7e14; font-weight: 600; }
            .status-5xx { color: #dc3545; font-weight: 600; }
            .refresh-info {
                text-align: center;
                color: white;
                margin-top: 20px;
                font-size: 0.9em;
            }
            .empty {
                text-align: center;
                color: #999;
                padding: 20px;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 ResoCall Monitor</h1>
                <p>Real-time server metrics & request tracking</p>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>📊 Tasks Queue</h2>
                    <div id="tasks-stats"></div>
                </div>
                <div class="card">
                    <h2>💻 System Load</h2>
                    <div id="system-stats"></div>
                </div>
                <div class="card">
                    <h2>⚙️ Process Info</h2>
                    <div id="process-stats"></div>
                </div>
            </div>

            <div class="requests-section">
                <h2>📝 Recent Requests (auto-refresh every 2s)</h2>
                <div id="requests-table"></div>
            </div>

            <div class="refresh-info">
                Last updated: <span id="last-update">--:--:--</span>
            </div>
        </div>

        <script>
            async function updateMonitor() {
                try {
                    const res = await fetch('/api/v1/monitor');
                    const data = await res.json();

                    // Update tasks stats
                    const tasksHtml = `
                        <div class="metric">
                            <span class="metric-label">Max Workers</span>
                            <span class="metric-value">${data.tasks.max_workers || 0}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Total Tasks</span>
                            <span class="metric-value">${data.tasks.total_tasks || 0}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Queued</span>
                            <span class="metric-value"><span class="status-badge status-queued">${data.tasks.counts.queued}</span></span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Processing</span>
                            <span class="metric-value"><span class="status-badge status-processing">${data.tasks.counts.processing}</span></span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Done</span>
                            <span class="metric-value"><span class="status-badge status-done">${data.tasks.counts.done}</span></span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Failed</span>
                            <span class="metric-value"><span class="status-badge status-failed">${data.tasks.counts.failed}</span></span>
                        </div>
                    `;
                    document.getElementById('tasks-stats').innerHTML = tasksHtml;

                    // Update system stats
                    const systemHtml = data.system.loadavg ? `
                        <div class="metric">
                            <span class="metric-label">Load 1m</span>
                            <span class="metric-value">${data.system.loadavg['1m'].toFixed(2)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Load 5m</span>
                            <span class="metric-value">${data.system.loadavg['5m'].toFixed(2)}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Load 15m</span>
                            <span class="metric-value">${data.system.loadavg['15m'].toFixed(2)}</span>
                        </div>
                    ` : '<div class="empty">No system data available</div>';
                    document.getElementById('system-stats').innerHTML = systemHtml;

                    // Update process stats
                    const processHtml = data.system.process ? `
                        <div class="metric">
                            <span class="metric-label">RSS Memory</span>
                            <span class="metric-value">${(data.system.process.rss_bytes / 1024 / 1024).toFixed(1)} MB</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">VMS Memory</span>
                            <span class="metric-value">${(data.system.process.vms_bytes / 1024 / 1024).toFixed(1)} MB</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">CPU Usage</span>
                            <span class="metric-value">${data.system.process.cpu_percent.toFixed(1)}%</span>
                        </div>
                    ` : '<div class="empty">No process data available</div>';
                    document.getElementById('process-stats').innerHTML = processHtml;

                    // Update requests table
                    const requests = data.recent_requests || [];
                    let requestsHtml = '<table><thead><tr><th>Time</th><th>Method</th><th>Path</th><th>Client</th><th>Status</th><th>Duration (ms)</th></tr></thead><tbody>';
                    if (requests.length === 0) {
                        requestsHtml += '<tr><td colspan="6" class="empty">No requests yet</td></tr>';
                    } else {
                        requests.forEach(req => {
                            const methodClass = 'method-' + req.method.toLowerCase();
                            const statusClass = req.status < 400 ? 'status-2xx' : (req.status < 500 ? 'status-4xx' : 'status-5xx');
                            const time = req.ts ? new Date(req.ts * 1000).toLocaleTimeString() : '--:--:--';
                            requestsHtml += `
                                <tr>
                                    <td>${time}</td>
                                    <td class="${methodClass}">${req.method}</td>
                                    <td>${req.path}</td>
                                    <td>${req.client || 'unknown'}</td>
                                    <td class="${statusClass}">${req.status}</td>
                                    <td>${(req.duration_s * 1000).toFixed(1)}</td>
                                </tr>
                            `;
                        });
                    }
                    requestsHtml += '</tbody></table>';
                    document.getElementById('requests-table').innerHTML = requestsHtml;

                    // Update timestamp
                    const now = new Date().toLocaleTimeString();
                    document.getElementById('last-update').textContent = now;
                } catch (err) {
                    console.error('Error fetching monitor data:', err);
                    document.getElementById('requests-table').innerHTML = '<div class="empty">Error loading data</div>';
                }
            }

            // Update immediately and then every 2 seconds
            updateMonitor();
            setInterval(updateMonitor, 2000);
        </script>
    </body>
    </html>
    """
    return html

