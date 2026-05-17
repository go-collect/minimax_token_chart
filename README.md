# MiniMax Token Dashboard

实时监控 MiniMax API Token 余量，支持每小时自动记录和趋势图表查看。

## Features

- **实时余量查看** - 查看各模型的当前使用量和剩余额度
- **每小时自动记录** - 后台线程在每小时的 58 分自动获取并保存数据
- **趋势图表** - 选择日期范围，直观展示 Token 消耗趋势
- **自动刷新** - 每 60 秒自动更新当前数据

## Quick Start

```bash
pip install requests python-dotenv
python app.py
```

访问 http://localhost:3780

## Configuration

在项目根目录创建 `.env` 文件：

```
MINIMAX_API_TOKEN=your_api_token_here
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | 主页面 |
| `/api/tokens` | GET | 获取当前 Token 余量 |
| `/api/history` | GET | 获取历史记录 |
| `/api/trend?start=YYYY-MM-DD&end=YYYY-MM-DD` | GET | 按日期范围获取趋势数据 |

## Data Storage

历史记录保存在 `token_history.json` 文件中（自动创建），保留近一年数据。

## Tech Stack

- Python Flask
- Chart.js
- Inter + JetBrains Mono 字体