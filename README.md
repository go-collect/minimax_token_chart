# MiniMax Token Dashboard / MiniMax Token 监控面板

[English](#english) | [中文](#中文)

---

## English

### Overview

Real-time monitoring of MiniMax API Token usage with automatic hourly recording and trend visualization.

### Features

- **Real-time Status** - View current usage and remaining quotas for all models
- **Scheduled Recording** - Automatically records at 04:58, 09:58, 14:58, 19:58, and 23:58 daily to capture peak usage
- **Trend Chart** - Hourly token consumption trends with date range filtering
- **Auto Refresh** - Updates every 60 seconds

### Quick Start

```bash
pip install requests python-dotenv
python app.py
```

Visit http://localhost:3780

### Configuration

Create a `.env` file in the project root:

```
MINIMAX_API_TOKEN=your_api_token_here
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/tokens` | GET | Get current token remaining |
| `/api/history` | GET | Get all historical records |
| `/api/trend?start=YYYY-MM-DD&end=YYYY-MM-DD` | GET | Get trend data by date range |

### Data Storage

History is stored in `token_history.json` (auto-created), kept for 1 year.

### Tech Stack

- Python Flask
- Chart.js
- Inter + JetBrains Mono fonts

---

## 中文

### 概述

实时监控 MiniMax API Token 余量，支持定时记录和趋势图表查看。

### 功能特点

- **实时状态** - 查看各模型的当前使用量和剩余额度
- **定时记录** - 每天 4、9、14、19、23 点的 58 分自动记录，准确反映日用量峰值
- **趋势图表** - 按小时查看 Token 消耗趋势，支持日期范围筛选
- **自动刷新** - 每 60 秒自动更新当前数据

### 快速开始

```bash
pip install requests python-dotenv
python app.py
```

访问 http://localhost:3780

### 配置

在项目根目录创建 `.env` 文件：

```
MINIMAX_API_TOKEN=your_api_token_here
```

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/api/tokens` | GET | 获取当前 Token 余量 |
| `/api/history` | GET | 获取所有历史记录 |
| `/api/trend?start=YYYY-MM-DD&end=YYYY-MM-DD` | GET | 按日期范围获取趋势数据 |

### 数据存储

历史记录保存在 `token_history.json` 文件中（自动创建），保留近一年数据。

### 技术栈

- Python Flask
- Chart.js
- Inter + JetBrains Mono 字体