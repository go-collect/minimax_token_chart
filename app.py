from flask import Flask, render_template_string, request, jsonify
import requests
from datetime import datetime, timedelta
import time
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_URL = "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains"
API_TOKEN = os.environ.get("MINIMAX_API_TOKEN", "")
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token_history.json")

def fetch_token_data():
    try:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        response = requests.get(API_URL, headers=headers, timeout=10)
        return response.json(), None
    except Exception as e:
        return None, str(e)

def format_timestamp(ts_ms):
    if ts_ms <= 0:
        return "N/A"
    return datetime.fromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")

def format_countdown(ts_ms):
    if ts_ms <= 0:
        return "N/A"
    now = int(time.time() * 1000)
    remaining = ts_ms - now
    if remaining <= 0:
        return "Expired"
    seconds = remaining // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"

def calc_percentage(used, total):
    if total == 0:
        return 0
    return min(100, round(used / total * 100, 1))

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def record_token_data():
    data, error = fetch_token_data()
    if error:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "timestamp": timestamp,
        "timestamp_unix": int(time.time() * 1000),
        "models": []
    }
    
    for m in data.get("model_remains", []):
        total = m.get("current_interval_total_count", 0)
        if total == 0:
            continue
        remaining = m.get("current_interval_usage_count", 0)
        used = total - remaining
        
        weekly_total = m.get("current_weekly_total_count", 0)
        weekly_remaining = m.get("current_weekly_usage_count", 0)
        weekly_used = weekly_total - weekly_remaining
        
        record["models"].append({
            "model_name": m.get("model_name", "Unknown"),
            "total": total,
            "used": used,
            "remaining": remaining,
            "percentage": (used / total * 100) if total > 0 else 0,
            "weekly_total": weekly_total,
            "weekly_used": weekly_used,
            "weekly_remaining": weekly_remaining,
            "weekly_percentage": (weekly_used / weekly_total * 100) if weekly_total > 0 else 0
        })
    
    history = load_history()
    history.append(record)
    
    one_year_ago = datetime.now() - timedelta(days=365)
    history = [r for r in history if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") >= one_year_ago]
    
    save_history(history)

def run_scheduler():
    while True:
        now = datetime.now()
        minute = now.minute
        second = now.second
        
        if minute == 58 and second < 60:
            record_token_data()
            time.sleep(60)
        
        time.sleep(30)

import threading
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiniMax Token Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            color: #ffffff;
            padding: 2rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .header-left h1 {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #00d4ff, #7b68ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }

        .header-left .subtitle {
            color: #a0a0a0;
            font-size: 0.95rem;
        }

        .header-right {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.75rem;
        }

        .last-update {
            color: #a0a0a0;
            font-size: 0.85rem;
            font-family: 'JetBrains Mono', monospace;
        }

        .refresh-btn {
            background: linear-gradient(135deg, #00d4ff 0%, #7b68ee 100%);
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,212,255,0.3);
        }

        .refresh-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .refresh-icon {
            width: 18px;
            height: 18px;
            transition: transform 0.5s ease;
        }

        .refresh-btn:hover .refresh-icon {
            transform: rotate(180deg);
        }

        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15,15,35,0.9);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }

        .loading-overlay.active {
            display: flex;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid rgba(0,212,255,0.2);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
        }

        .card {
            background: rgba(15,15,35,0.7);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--glow-color, #4ecdc4), transparent);
            opacity: 0.8;
        }

        .card:hover {
            transform: translateY(-4px);
            border-color: rgba(0,212,255,0.3);
            box-shadow: 0 12px 40px rgba(0,212,255,0.15);
        }

        .card.available { --glow-color: #4ecdc4; }
        .card.warning { --glow-color: #ffb347; }
        .card.exhausted { --glow-color: #ff6b6b; }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.25rem;
        }

        .model-name {
            font-size: 1.15rem;
            font-weight: 600;
            color: #fff;
            line-height: 1.4;
        }

        .status-badge {
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .status-badge.available {
            background: rgba(78,205,196,0.2);
            color: #4ecdc4;
        }

        .status-badge.warning {
            background: rgba(255,179,71,0.2);
            color: #ffb347;
        }

        .status-badge.exhausted {
            background: rgba(255,107,107,0.2);
            color: #ff6b6b;
        }

        .usage-bar-container {
            background: rgba(255,255,255,0.08);
            border-radius: 8px;
            height: 10px;
            margin-bottom: 1.25rem;
            overflow: hidden;
        }

        .usage-bar {
            height: 100%;
            border-radius: 8px;
            transition: width 0.8s ease;
            background: linear-gradient(90deg, var(--glow-color, #4ecdc4), var(--glow-color, #4ecdc4));
        }

        .card.exhausted .usage-bar {
            background: linear-gradient(90deg, #ff6b6b, #ff8e8e);
        }

        .card.warning .usage-bar {
            background: linear-gradient(90deg, #ffb347, #ffc870);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 1.25rem;
        }

        .stat-item {
            text-align: center;
            padding: 0.75rem;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
        }

        .stat-label {
            font-size: 0.7rem;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.35rem;
        }

        .stat-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            color: #fff;
        }

        .stat-value.remaining {
            color: #4ecdc4;
        }

        .time-info {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.06);
        }

        .time-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .time-label {
            font-size: 0.8rem;
            color: #a0a0a0;
        }

        .time-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #00d4ff;
        }

        .countdown {
            color: #ffb347 !important;
            font-weight: 600;
        }

        .error-container {
            text-align: center;
            padding: 4rem 2rem;
            background: rgba(255,107,107,0.1);
            border: 1px solid rgba(255,107,107,0.3);
            border-radius: 16px;
        }

        .error-container h2 {
            color: #ff6b6b;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }

        .error-container p {
            color: #a0a0a0;
            margin-bottom: 1.5rem;
        }

        .retry-btn {
            background: #ff6b6b;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            font-size: 1rem;
        }

        .chart-section {
            margin-top: 2.5rem;
            background: rgba(15,15,35,0.7);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 1.5rem;
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .chart-title {
            font-size: 1.3rem;
            font-weight: 600;
        }

        .chart-controls {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .date-input {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }

        .date-input:focus {
            outline: none;
            border-color: #00d4ff;
        }

        .chart-btn {
            background: linear-gradient(135deg, #00d4ff 0%, #7b68ee 100%);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.85rem;
        }

        .chart-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 15px rgba(0,212,255,0.3);
        }

        .chart-container {
            position: relative;
            height: 350px;
        }

        .chart-empty {
            text-align: center;
            padding: 3rem;
            color: #a0a0a0;
        }

        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }

            .header {
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }

            .header-right {
                align-items: flex-start;
                width: 100%;
            }

            .grid {
                grid-template-columns: 1fr;
            }

            .stats-grid {
                grid-template-columns: repeat(3, 1fr);
            }

            .chart-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-left">
                <h1>MiniMax Token Dashboard</h1>
                <p class="subtitle">API Token Usage & Remaining Quotas</p>
            </div>
            <div class="header-right">
                <div class="last-update" id="lastUpdate">--</div>
                <button class="refresh-btn" id="refreshBtn" onclick="fetchData()">
                    <svg class="refresh-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
                    </svg>
                    Refresh
                </button>
            </div>
        </header>

        <div id="content">
            <div class="grid" id="cardGrid"></div>
        </div>

        <div class="chart-section">
            <div class="chart-header">
                <div class="chart-title">Token Usage Trend</div>
                <div class="chart-controls">
                    <input type="date" class="date-input" id="startDate" />
                    <span style="color: #a0a0a0;">to</span>
                    <input type="date" class="date-input" id="endDate" />
                    <button class="chart-btn" onclick="loadTrendChart()">Apply</button>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="trendChart"></canvas>
                <div class="chart-empty" id="chartEmpty" style="display: none;">No data available for the selected period</div>
            </div>
        </div>
    </div>

    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
    </div>

    <script>
        let trendChart = null;

        async function fetchData() {
            const btn = document.getElementById('refreshBtn');
            const overlay = document.getElementById('loadingOverlay');

            btn.disabled = true;
            overlay.classList.add('active');

            try {
                const response = await fetch('/api/tokens');
                const data = await response.json();

                if (data.error) {
                    showError(data.error);
                } else {
                    renderCards(data);
                    document.getElementById('lastUpdate').textContent = 'Last update: ' + data.timestamp;
                }
            } catch (err) {
                showError(err.message);
            } finally {
                btn.disabled = false;
                overlay.classList.remove('active');
            }
        }

        function showError(msg) {
            document.getElementById('cardGrid').innerHTML = `
                <div class="error-container" style="grid-column: 1/-1;">
                    <h2>Failed to Load Data</h2>
                    <p>${msg}</p>
                    <button class="retry-btn" onclick="fetchData()">Retry</button>
                </div>
            `;
        }

        function getStatusClass(percentage) {
            if (percentage >= 100) return 'exhausted';
            if (percentage >= 80) return 'warning';
            return 'available';
        }

        function getStatusText(percentage) {
            if (percentage >= 100) return 'Exhausted';
            if (percentage >= 80) return 'Low';
            return 'Available';
        }

        function formatNumber(num) {
            if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
            return num.toString();
        }

        function renderCards(data) {
            const grid = document.getElementById('cardGrid');

            if (!data.models || data.models.length === 0) {
                grid.innerHTML = '<p style="color:#a0a0a0;text-align:center;padding:2rem;">No data available</p>';
                return;
            }

            grid.innerHTML = data.models.map(model => {
                const intervalPct = model.interval_percentage;
                const weeklyPct = model.weekly_percentage;
                const statusClass = getStatusClass(intervalPct);
                const statusText = getStatusText(intervalPct);

                return `
                    <div class="card ${statusClass}">
                        <div class="card-header">
                            <div class="model-name">${model.model_name}</div>
                            <span class="status-badge ${statusClass}">${statusText}</span>
                        </div>

                        <div class="usage-bar-container">
                            <div class="usage-bar" style="width: ${intervalPct}%"></div>
                        </div>

                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-label">Total</div>
                                <div class="stat-value">${formatNumber(model.current_interval_total_count)}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Used</div>
                                <div class="stat-value">${formatNumber(model.current_interval_usage_count)}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Remaining</div>
                                <div class="stat-value remaining">${formatNumber(model.remains_time)}</div>
                            </div>
                        </div>

                        ${model.current_weekly_total_count > 0 ? `
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-label">Weekly Total</div>
                                    <div class="stat-value">${formatNumber(model.current_weekly_total_count)}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Weekly Used</div>
                                    <div class="stat-value">${formatNumber(model.current_weekly_usage_count)}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Weekly Left</div>
                                    <div class="stat-value remaining">${formatNumber(model.weekly_remains_time)}</div>
                                </div>
                            </div>
                        ` : ''}

                        <div class="time-info">
                            <div class="time-row">
                                <span class="time-label">Interval Reset</span>
                                <span class="time-value">${model.interval_end}</span>
                            </div>
                            <div class="time-row">
                                <span class="time-label">Countdown</span>
                                <span class="time-value countdown">${model.countdown}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function loadTrendChart() {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            let url = '/api/trend';
            const params = [];
            if (startDate) params.push('start=' + startDate);
            if (endDate) params.push('end=' + endDate);
            if (params.length > 0) url += '?' + params.join('&');

            try {
                const response = await fetch(url);
                const data = await response.json();
                renderTrendChart(data.history);
            } catch (err) {
                console.error('Failed to load trend data:', err);
            }
        }

        function renderTrendChart(history) {
            const canvas = document.getElementById('trendChart');
            const chartEmpty = document.getElementById('chartEmpty');
            
            if (!history || history.length === 0) {
                canvas.style.display = 'none';
                chartEmpty.style.display = 'block';
                if (trendChart) {
                    trendChart.destroy();
                    trendChart = null;
                }
                return;
            }

            canvas.style.display = 'block';
            chartEmpty.style.display = 'none';

            const groupedData = {};
            history.forEach(record => {
                const hour = record.timestamp.substring(0, 13) + ':00';
                record.models.forEach(m => {
                    if (!groupedData[m.model_name]) {
                        groupedData[m.model_name] = {};
                    }
                    if (!groupedData[m.model_name][hour]) {
                        groupedData[m.model_name][hour] = { used: 0, total: 0 };
                    }
                    groupedData[m.model_name][hour].used += m.used;
                    groupedData[m.model_name][hour].total += m.total;
                });
            });

            const allHours = [...new Set(history.map(r => r.timestamp.substring(0, 13) + ':00'))].sort();
            
            const colors = [
                { border: 'rgb(0, 212, 255)', bg: 'rgba(0, 212, 255, 0.1)' },
                { border: 'rgb(123, 104, 238)', bg: 'rgba(123, 104, 238, 0.1)' },
                { border: 'rgb(78, 205, 196)', bg: 'rgba(78, 205, 196, 0.1)' },
                { border: 'rgb(255, 179, 71)', bg: 'rgba(255, 179, 71, 0.1)' },
                { border: 'rgb(255, 107, 107)', bg: 'rgba(255, 107, 107, 0.1)' },
            ];

            const datasets = Object.keys(groupedData).map((modelName, idx) => {
                const data = allHours.map(hour => {
                    const record = groupedData[modelName][hour];
                    return record ? Math.round(record.used) : null;
                });
                const color = colors[idx % colors.length];
                return {
                    label: modelName,
                    data: data,
                    borderColor: color.border,
                    backgroundColor: color.bg,
                    tension: 0.3,
                    fill: true,
                    spanGaps: true
                };
            });

            if (trendChart) {
                trendChart.destroy();
            }

            trendChart = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: allHours,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                color: '#a0a0a0',
                                font: { family: 'Inter' }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(15, 15, 35, 0.9)',
                            titleColor: '#fff',
                            bodyColor: '#a0a0a0',
                            borderColor: 'rgba(255,255,255,0.1)',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#a0a0a0', font: { family: 'JetBrains Mono', size: 10 } }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.05)' },
                            ticks: { color: '#a0a0a0', font: { family: 'JetBrains Mono' } },
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        function initDateInputs() {
            const today = new Date();
            const thirtyDaysAgo = new Date(today);
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            
            document.getElementById('endDate').value = today.toISOString().split('T')[0];
            document.getElementById('startDate').value = thirtyDaysAgo.toISOString().split('T')[0];
        }

        fetchData();
        setInterval(fetchData, 60000);
        initDateInputs();
        loadTrendChart();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tokens')
def api_tokens():
    data, error = fetch_token_data()

    if error:
        return {"error": error}, 500

    models = []
    for m in data.get("model_remains", []):
        total = m.get("current_interval_total_count", 0)
        if total == 0:
            continue
        remaining = m.get("current_interval_usage_count", 0)  # API字段名是usage，实际是剩余量
        used = total - remaining
        percentage = (used / total * 100) if total > 0 else 0

        weekly_total = m.get("current_weekly_total_count", 0)
        weekly_remaining = m.get("current_weekly_usage_count", 0)  # 同上
        weekly_used = weekly_total - weekly_remaining
        weekly_pct = (weekly_used / weekly_total * 100) if weekly_total > 0 else 0

        models.append({
            "model_name": m.get("model_name", "Unknown"),
            "current_interval_total_count": total,
            "current_interval_usage_count": used,  # 修正：现在是实际使用量
            "remains_time": remaining,  # 修正：实际是剩余量
            "interval_percentage": percentage,
            "current_weekly_total_count": weekly_total,
            "current_weekly_usage_count": weekly_used,  # 修正：现在是实际使用量
            "weekly_remains_time": weekly_remaining,  # 修正：实际是剩余量
            "weekly_percentage": weekly_pct,
            "interval_end": format_timestamp(m.get("end_time", 0)),
            "countdown": format_countdown(m.get("end_time", 0))
        })

    return {
        "models": models,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.route('/api/history')
def api_history():
    history = load_history()
    return jsonify({"history": history})

@app.route('/api/trend')
def api_trend():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    history = load_history()
    
    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        history = [r for r in history if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") >= start_dt]
    
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        history = [r for r in history if datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S") < end_dt]
    
    return jsonify({"history": history})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3780, debug=False)
