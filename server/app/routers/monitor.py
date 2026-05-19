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
        import importlib

        psutil = importlib.import_module("psutil")

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
        "database": {
            "employees": len(ctx.calls.list_employees()) if ctx is not None else 0,
            "clients": len(ctx.calls.list_clients()) if ctx is not None else 0,
            "calls": len(ctx.calls.list_calls(include_deleted=True)) if ctx is not None else 0,
        },
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
        <title>ResoCall Server Monitor</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background:
                    radial-gradient(circle at top left, rgba(102, 126, 234, 0.24), transparent 30%),
                    radial-gradient(circle at top right, rgba(14, 165, 233, 0.18), transparent 26%),
                    linear-gradient(135deg, #0f172a 0%, #172554 45%, #312e81 100%);
                min-height: 100vh;
                padding: 20px;
                color: #0f172a;
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
                letter-spacing: -0.03em;
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
                align-items: start;
            }
            .storage-card {
                grid-column: span 2;
            }
            .card {
                background: white;
                border-radius: 18px;
                padding: 24px;
                box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
                transition: transform 0.25s ease, box-shadow 0.25s ease;
                border: 1px solid rgba(148, 163, 184, 0.18);
            }
            .card:hover {
                transform: translateY(-4px);
                box-shadow: 0 22px 48px rgba(15, 23, 42, 0.24);
            }
            .card h2 {
                color: #0f172a;
                margin-bottom: 20px;
                font-size: 1.3em;
                border-bottom: 2px solid #1d4ed8;
                padding-bottom: 10px;
            }
            .subsection {
                margin-bottom: 18px;
                padding: 16px;
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                background: #f8fafc;
            }
            .subsection:last-child {
                margin-bottom: 0;
            }
            .subsection h3 {
                font-size: 0.98em;
                color: #0f172a;
                margin-bottom: 12px;
            }
            .inline-form {
                display: grid;
                gap: 8px;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                margin-bottom: 10px;
            }
            .inline-form input,
            .inline-form select,
            .inline-form textarea {
                width: 100%;
                padding: 9px 10px;
                border-radius: 10px;
                border: 1px solid #cbd5e1;
                background: white;
                color: #0f172a;
            }
            .inline-form textarea {
                min-height: 96px;
                grid-column: 1 / -1;
                resize: vertical;
            }
            .inline-actions {
                display: flex;
                gap: 8px;
                align-items: center;
                flex-wrap: wrap;
                margin-top: 4px;
            }
            .inline-actions button {
                padding: 8px 12px;
                border-radius: 10px;
                border: 0;
                background: #1d4ed8;
                color: white;
                font-weight: 600;
                cursor: pointer;
            }
            .inline-actions button.secondary {
                background: #e2e8f0;
                color: #0f172a;
            }
            .inline-actions button.danger {
                background: #dc2626;
            }
            .inline-actions button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .storage-auth-row {
                display: flex;
                gap: 8px;
                width: 100%;
                flex-wrap: wrap;
            }
            .storage-auth-row input {
                flex: 1 1 220px;
                min-width: 0;
                padding: 8px;
            }
            .storage-auth-row button {
                flex: 0 0 auto;
                white-space: nowrap;
            }
            .storage-card table {
                width: 100%;
                table-layout: fixed;
            }
            .storage-card th,
            .storage-card td {
                overflow-wrap: anywhere;
            }
            .storage-card td:last-child {
                white-space: nowrap;
            }
            .storage-card .download-file-btn,
            .storage-card .delete-file-btn,
            .storage-card .soft-delete-btn,
            .storage-card .restore-call-btn {
                white-space: nowrap;
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
            .muted {
                color: #64748b;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>ResoCall Server Monitor</h1>
                <p>Real-time server metrics & request tracking</p>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>Tasks Queue</h2>
                    <div id="tasks-stats"></div>
                </div>
                <div class="card">
                    <h2>System Load</h2>
                    <div id="system-stats"></div>
                </div>
                <div class="card">
                    <h2>Process Info</h2>
                    <div id="process-stats"></div>
                </div>
                <div class="card storage-card">
                    <h2>Storage</h2>
                    <div class="metric" style="gap:8px; align-items:flex-start; flex-direction:column;">
                        <div class="storage-auth-row">
                            <input id="auth-login" placeholder="login" />
                            <input id="auth-password" type="password" placeholder="password" />
                            <button type="button" id="auth-apply">Apply</button>
                        </div>
                        <div style="font-size:12px; color:#555;">Storage/admin APIs now require auth (admin or engineer).</div>
                    </div>
                    <div id="storage-list"></div>
                    <div style="margin-top:12px">
                        <form id="upload-form">
                            <input type="file" id="upload-file" />
                            <select id="upload-area">
                                <option value="uploads">uploads</option>
                                <option value="results">results</option>
                            </select>
                            <button type="button" id="upload-btn">Upload</button>
                        </form>
                    </div>
                    <div style="margin-top:12px">
                        <h3 style="margin:8px 0">Uploads Metadata</h3>
                        <div id="uploads-meta"></div>
                    </div>
                    <div style="margin-top:12px">
                        <h3 style="margin:8px 0">Calls Archive</h3>
                        <div id="calls-meta"></div>
                    </div>
                </div>
                <div class="card">
                    <h2>Database Operations</h2>

                    <div class="subsection">
                        <h3>Workers</h3>
                        <div class="inline-form">
                            <input id="employee-name" placeholder="Full name" />
                            <input id="employee-position" placeholder="Position" />
                            <input id="employee-hire-date" placeholder="Hire date (YYYY-MM-DD)" />
                        </div>
                        <div class="inline-actions">
                            <button type="button" id="employee-add">Create worker</button>
                            <span class="muted">Add or remove employees without leaving the monitor.</span>
                        </div>
                        <div id="employees-list"></div>
                    </div>

                    <div class="subsection">
                        <h3>Counterparties</h3>
                        <div class="inline-form">
                            <input id="client-name" placeholder="Company or person name" />
                            <input id="client-phone" placeholder="Phone or contact" />
                        </div>
                        <div class="inline-actions">
                            <button type="button" id="client-add">Create counterparty</button>
                            <span class="muted">This list is used by the call archive and future imports.</span>
                        </div>
                        <div id="clients-list"></div>
                    </div>

                    <div class="subsection">
                        <h3>New Call Record</h3>
                        <div class="inline-form">
                            <select id="call-employee"></select>
                            <select id="call-client"></select>
                            <input id="call-date" placeholder="2026-05-19T12:30:00+00:00" />
                            <input id="call-duration" type="number" min="0" placeholder="Duration, sec" />
                            <input id="call-category" placeholder="Category" />
                            <input id="call-sentiment" placeholder="positive / neutral / negative" />
                            <input id="call-compliance" type="number" min="0" max="100" placeholder="Script compliance" />
                            <input id="call-audio-url" placeholder="/api/calls/audio/call-xxx.mp3" />
                            <textarea id="call-transcript" placeholder='Transcript JSON array, e.g. [{"speaker":"operator","text":"...","timestamp":"00:00"}]'></textarea>
                        </div>
                        <div class="inline-actions">
                            <button type="button" id="call-create">Create call history</button>
                            <button type="button" class="secondary" id="call-reset">Reset</button>
                            <label class="muted" style="display:flex; align-items:center; gap:6px;">
                                <input id="call-processed" type="checkbox" />
                                Mark as processed
                            </label>
                        </div>
                        <div class="muted" style="margin-top:8px;">This endpoint is ready for automatic ML imports once the model starts writing call results.</div>
                    </div>
                </div>
            </div>

            <div class="requests-section">
                <h2>Recent Requests (auto-refresh every 2s)</h2>
                <div id="requests-table"></div>
            </div>

            <div class="refresh-info">
                Last updated: <span id="last-update">--:--:--</span>
            </div>
        </div>

        <script>
            const monitorAuth = {
                login: localStorage.getItem('monitor_login') || '',
                password: localStorage.getItem('monitor_password') || ''
            };

            document.getElementById('auth-login').value = monitorAuth.login;
            document.getElementById('auth-password').value = monitorAuth.password;

            function getAuthHeaders() {
                if (!monitorAuth.login || !monitorAuth.password) return {};
                const basic = btoa(monitorAuth.login + ':' + monitorAuth.password);
                return { 'Authorization': 'Basic ' + basic };
            }

            function fillSelectOptions(selectId, items, placeholder) {
                const select = document.getElementById(selectId);
                if (!select) return;
                select.innerHTML = '';
                if (placeholder) {
                    const opt = document.createElement('option');
                    opt.value = '';
                    opt.textContent = placeholder;
                    select.appendChild(opt);
                }
                items.forEach(item => {
                    const opt = document.createElement('option');
                    opt.value = item.id;
                    opt.textContent = `${item.name} (${item.id})`;
                    select.appendChild(opt);
                });
            }

            function safeJsonParse(value) {
                if (!value || !value.trim()) return [];
                const parsed = JSON.parse(value);
                if (!Array.isArray(parsed)) throw new Error('Transcript must be a JSON array');
                return parsed;
            }

            document.getElementById('auth-apply').addEventListener('click', () => {
                monitorAuth.login = document.getElementById('auth-login').value.trim();
                monitorAuth.password = document.getElementById('auth-password').value;
                localStorage.setItem('monitor_login', monitorAuth.login);
                localStorage.setItem('monitor_password', monitorAuth.password);
                updateStorage();
                updateUploadsMeta();
                updateEmployees();
                updateClients();
            });

            document.getElementById('employee-add').addEventListener('click', async () => {
                const name = document.getElementById('employee-name').value.trim();
                const position = document.getElementById('employee-position').value.trim();
                const hire_date = document.getElementById('employee-hire-date').value.trim();
                if (!name || !position) {
                    alert('Worker name and position are required');
                    return;
                }
                try {
                    const res = await fetch('/api/employees', {
                        method: 'POST',
                        headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, position, hire_date: hire_date || null }),
                    });
                    if (!res.ok) {
                        const detail = await res.json().catch(() => ({}));
                        throw new Error(detail.detail || 'create employee failed');
                    }
                    document.getElementById('employee-name').value = '';
                    document.getElementById('employee-position').value = '';
                    document.getElementById('employee-hire-date').value = '';
                    updateEmployees();
                } catch (err) {
                    alert(err instanceof Error ? err.message : 'Create employee failed');
                }
            });

            document.getElementById('client-add').addEventListener('click', async () => {
                const name = document.getElementById('client-name').value.trim();
                const phone = document.getElementById('client-phone').value.trim();
                if (!name) {
                    alert('Counterparty name is required');
                    return;
                }
                try {
                    const res = await fetch('/api/clients', {
                        method: 'POST',
                        headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name, phone: phone || null }),
                    });
                    if (!res.ok) {
                        const detail = await res.json().catch(() => ({}));
                        throw new Error(detail.detail || 'create client failed');
                    }
                    document.getElementById('client-name').value = '';
                    document.getElementById('client-phone').value = '';
                    updateClients();
                } catch (err) {
                    alert(err instanceof Error ? err.message : 'Create client failed');
                }
            });

            document.getElementById('call-create').addEventListener('click', async () => {
                const employee_id = document.getElementById('call-employee').value;
                const client_id = document.getElementById('call-client').value;
                const date = document.getElementById('call-date').value.trim();
                const duration = Number(document.getElementById('call-duration').value || 0);
                const category = document.getElementById('call-category').value.trim();
                const sentiment = document.getElementById('call-sentiment').value.trim() || 'neutral';
                const script_compliance = Number(document.getElementById('call-compliance').value || 0);
                const audio_url = document.getElementById('call-audio-url').value.trim();
                const is_processed = document.getElementById('call-processed').checked;
                let transcript = [];
                try {
                    transcript = safeJsonParse(document.getElementById('call-transcript').value);
                } catch (err) {
                    alert(err instanceof Error ? err.message : 'Invalid transcript JSON');
                    return;
                }
                if (!employee_id || !client_id) {
                    alert('Select employee and counterparty first');
                    return;
                }
                try {
                    const res = await fetch('/api/calls', {
                        method: 'POST',
                        headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            employee_id,
                            client_id,
                            date: date || null,
                            duration,
                            sentiment,
                            script_compliance,
                            category: category || 'Не определено',
                            is_processed,
                            audio_url: audio_url || null,
                            transcript,
                        }),
                    });
                    if (!res.ok) {
                        const detail = await res.json().catch(() => ({}));
                        throw new Error(detail.detail || 'create call failed');
                    }
                    resetCallForm();
                    updateCallsMeta();
                } catch (err) {
                    alert(err instanceof Error ? err.message : 'Create call failed');
                }
            });

            document.getElementById('call-reset').addEventListener('click', () => {
                resetCallForm();
            });

            function resetCallForm() {
                document.getElementById('call-date').value = '';
                document.getElementById('call-duration').value = '';
                document.getElementById('call-category').value = '';
                document.getElementById('call-sentiment').value = 'neutral';
                document.getElementById('call-compliance').value = '';
                document.getElementById('call-audio-url').value = '';
                document.getElementById('call-transcript').value = '';
                document.getElementById('call-processed').checked = false;
            }

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

                    // Update storage listing
                    updateStorage();
                    updateUploadsMeta();
                    updateEmployees();
                    updateClients();

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

            async function updateStorage() {
                try {
                    const res = await fetch('/api/v1/storage/files?which=uploads', { headers: getAuthHeaders() });
                    if (!res.ok) {
                        document.getElementById('storage-list').innerHTML = '<div class="empty">Auth required for storage</div>';
                        return;
                    }
                    const data = await res.json();
                    const files = data.files || [];
                    if (files.length === 0) {
                        document.getElementById('storage-list').innerHTML = '<div class="empty">No files</div>';
                        return;
                    }
                    let html = '<table><thead><tr><th>Name</th><th>Size</th><th>Action</th></tr></thead><tbody>';
                    files.forEach(f => {
                        html += `<tr><td>${f.name}</td><td>${(f.size/1024).toFixed(1)} KB</td><td><button type="button" data-name="${f.name}" class="download-file-btn">Download</button> | <button type="button" data-name="${f.name}" class="delete-file-btn">Delete</button></td></tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('storage-list').innerHTML = html;

                    document.querySelectorAll('.download-file-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const name = btn.getAttribute('data-name');
                            if (!name) return;
                            try {
                                const r = await fetch('/api/v1/storage/download?which=uploads&name=' + encodeURIComponent(name), {
                                    headers: getAuthHeaders(),
                                });
                                if (!r.ok) throw new Error('download failed');
                                const blob = await r.blob();
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url;
                                a.download = name;
                                document.body.appendChild(a);
                                a.click();
                                a.remove();
                                window.URL.revokeObjectURL(url);
                            } catch (err) {
                                alert('Download failed');
                            }
                        });
                    });

                    document.querySelectorAll('.delete-file-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const name = btn.getAttribute('data-name');
                            if (!name) return;
                            if (!confirm('Delete file ' + name + '?')) return;
                            try {
                                const del = await fetch('/api/v1/storage/file?which=uploads&name=' + encodeURIComponent(name), {
                                    method: 'DELETE',
                                    headers: getAuthHeaders(),
                                });
                                if (!del.ok) throw new Error('delete failed');
                                updateStorage();
                                updateUploadsMeta();
                            } catch (err) {
                                alert('Delete failed');
                            }
                        });
                    });
                } catch (err) {
                    console.error('storage error', err);
                    document.getElementById('storage-list').innerHTML = '<div class="empty">Error loading storage</div>';
                }
            }

            async function updateUploadsMeta() {
                try {
                    const res = await fetch('/api/v1/storage/uploads?include_deleted=true&limit=50', { headers: getAuthHeaders() });
                    if (!res.ok) {
                        document.getElementById('uploads-meta').innerHTML = '<div class="empty">Auth required for metadata</div>';
                        return;
                    }
                    const data = await res.json();
                    const rows = data.uploads || [];
                    if (rows.length === 0) {
                        document.getElementById('uploads-meta').innerHTML = '<div class="empty">No upload metadata</div>';
                        return;
                    }
                    let html = '<table><thead><tr><th>ID</th><th>Name</th><th>User</th><th>Uploaded</th><th>Deleted</th><th>Action</th></tr></thead><tbody>';
                    rows.forEach(r => {
                        const deleted = r.deleted_at ? 'yes' : 'no';
                        const action = r.deleted_at ? '-' : `<button type="button" class="soft-delete-btn" data-id="${r.id}">Soft delete</button>`;
                        html += `<tr><td>${r.id}</td><td>${r.name}</td><td>${r.uploader || '-'}</td><td>${r.uploaded_at || '-'}</td><td>${deleted}</td><td>${action}</td></tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('uploads-meta').innerHTML = html;

                    document.querySelectorAll('.soft-delete-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const id = btn.getAttribute('data-id');
                            if (!id) return;
                            try {
                                const r = await fetch('/api/v1/storage/uploads/' + encodeURIComponent(id) + '/soft-delete', {
                                    method: 'POST',
                                    headers: getAuthHeaders(),
                                });
                                if (!r.ok) throw new Error('soft delete failed');
                                updateUploadsMeta();
                            } catch (err) {
                                alert('Soft delete failed');
                            }
                        });
                    });
                } catch (err) {
                    console.error('uploads meta error', err);
                    document.getElementById('uploads-meta').innerHTML = '<div class="empty">Error loading metadata</div>';
                }
            }

            async function updateCallsMeta() {
                try {
                    const res = await fetch('/api/calls?include_deleted=true', { headers: getAuthHeaders() });
                    if (!res.ok) {
                        document.getElementById('calls-meta').innerHTML = '<div class="empty">Auth required for call archive</div>';
                        return;
                    }
                    const rows = await res.json();
                    if (!rows.length) {
                        document.getElementById('calls-meta').innerHTML = '<div class="empty">No calls</div>';
                        return;
                    }
                    let html = '<table><thead><tr><th>ID</th><th>Client</th><th>Date</th><th>Deleted</th><th>Action</th></tr></thead><tbody>';
                    rows.forEach(r => {
                        const deleted = r.deleted_at ? 'yes' : 'no';
                        const action = r.deleted_at
                            ? `<button type="button" class="restore-call-btn" data-id="${r.id}">Restore</button>`
                            : `<button type="button" class="delete-call-btn" data-id="${r.id}">Soft delete</button>`;
                        html += `<tr><td>${r.id}</td><td>${r.clientName || r.clientId || '-'}</td><td>${r.date || '-'}</td><td>${deleted}</td><td>${action}</td></tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('calls-meta').innerHTML = html;

                    document.querySelectorAll('.delete-call-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const id = btn.getAttribute('data-id');
                            if (!id) return;
                            if (!confirm('Soft delete call ' + id + '?')) return;
                            try {
                                const r = await fetch('/api/calls/' + encodeURIComponent(id), {
                                    method: 'DELETE',
                                    headers: getAuthHeaders(),
                                });
                                if (!r.ok) throw new Error('soft delete failed');
                                updateCallsMeta();
                            } catch (err) {
                                alert('Soft delete failed');
                            }
                        });
                    });

                    document.querySelectorAll('.restore-call-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const id = btn.getAttribute('data-id');
                            if (!id) return;
                            try {
                                const r = await fetch('/api/calls/' + encodeURIComponent(id) + '/restore', {
                                    method: 'POST',
                                    headers: getAuthHeaders(),
                                });
                                if (!r.ok) throw new Error('restore failed');
                                updateCallsMeta();
                            } catch (err) {
                                alert('Restore failed');
                            }
                        });
                    });
                } catch (err) {
                    console.error('calls meta error', err);
                    document.getElementById('calls-meta').innerHTML = '<div class="empty">Error loading call archive</div>';
                }
            }

            async function updateEmployees() {
                try {
                    const res = await fetch('/api/employees', { headers: getAuthHeaders() });
                    if (!res.ok) {
                        document.getElementById('employees-list').innerHTML = '<div class="empty">Auth required for workers</div>';
                        return;
                    }
                    const data = await res.json();
                    const employees = Array.isArray(data) ? data : (data.employees || []);
                    fillSelectOptions('call-employee', employees, 'Select worker');
                    if (employees.length === 0) {
                        document.getElementById('employees-list').innerHTML = '<div class="empty">No workers</div>';
                        return;
                    }
                    let html = '<table><thead><tr><th>Name</th><th>Position</th><th>Hire date</th><th>Action</th></tr></thead><tbody>';
                    employees.forEach(employee => {
                        html += `<tr><td>${employee.name}</td><td>${employee.position || '-'}</td><td>${employee.hireDate || '-'}</td><td><button type="button" class="delete-employee-btn danger" data-id="${employee.id}">Delete</button></td></tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('employees-list').innerHTML = html;

                    document.querySelectorAll('.delete-employee-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const id = btn.getAttribute('data-id');
                            if (!id) return;
                            if (!confirm('Delete worker ' + id + '?')) return;
                            try {
                                const res = await fetch('/api/employees/' + encodeURIComponent(id), {
                                    method: 'DELETE',
                                    headers: getAuthHeaders(),
                                });
                                if (!res.ok) throw new Error('delete failed');
                                updateEmployees();
                            } catch (err) {
                                alert('Delete worker failed');
                            }
                        });
                    });
                } catch (err) {
                    console.error('employees error', err);
                    document.getElementById('employees-list').innerHTML = '<div class="empty">Error loading workers</div>';
                }
            }

            async function updateClients() {
                try {
                    const res = await fetch('/api/clients', { headers: getAuthHeaders() });
                    if (!res.ok) {
                        document.getElementById('clients-list').innerHTML = '<div class="empty">Auth required for counterparties</div>';
                        return;
                    }
                    const data = await res.json();
                    const clients = Array.isArray(data) ? data : (data.clients || []);
                    fillSelectOptions('call-client', clients, 'Select counterparty');
                    if (clients.length === 0) {
                        document.getElementById('clients-list').innerHTML = '<div class="empty">No counterparties</div>';
                        return;
                    }
                    let html = '<table><thead><tr><th>Name</th><th>Phone</th><th>Action</th></tr></thead><tbody>';
                    clients.forEach(client => {
                        html += `<tr><td>${client.name}</td><td>${client.phone || '-'}</td><td><button type="button" class="delete-client-btn danger" data-id="${client.id}">Delete</button></td></tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('clients-list').innerHTML = html;

                    document.querySelectorAll('.delete-client-btn').forEach(btn => {
                        btn.addEventListener('click', async () => {
                            const id = btn.getAttribute('data-id');
                            if (!id) return;
                            if (!confirm('Delete counterparty ' + id + '?')) return;
                            try {
                                const res = await fetch('/api/clients/' + encodeURIComponent(id), {
                                    method: 'DELETE',
                                    headers: getAuthHeaders(),
                                });
                                if (!res.ok) throw new Error('delete failed');
                                updateClients();
                            } catch (err) {
                                alert('Delete counterparty failed');
                            }
                        });
                    });
                } catch (err) {
                    console.error('clients error', err);
                    document.getElementById('clients-list').innerHTML = '<div class="empty">Error loading counterparties</div>';
                }
            }

            document.getElementById('upload-btn').addEventListener('click', async () => {
                const inp = document.getElementById('upload-file');
            updateEmployees();
            updateClients();
                if (!inp.files || inp.files.length === 0) return alert('Choose a file');
                const file = inp.files[0];
                const fd = new FormData();
                fd.append('file', file);
                fd.append('area', area);
                try {
                    const res = await fetch('/api/v1/storage/upload', { method: 'POST', body: fd, headers: getAuthHeaders() });
                    if (!res.ok) throw new Error('upload failed');
                    const j = await res.json();
                    alert('Uploaded: ' + j.name);
                    inp.value = '';
                    updateStorage();
                    updateUploadsMeta();
                } catch (err) {
                    console.error('upload err', err);
                    alert('Upload failed');
                }
            });

            updateCallsMeta();
            updateParticipants();
        </script>
    </body>
    </html>
    """
    return html

