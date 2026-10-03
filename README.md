# Financial Research Assistant

一個小型的金融市場研究工具。使用者輸入 `AAPL`、`NVDA` 或 `XAUUSD` 後，前端會呼叫 FastAPI backend；backend 再向外部市場資料來源取得資料，整理成固定格式、驗證後回傳給網頁。

目前版本重點是把一條完整的資料流程做通：

```text
Browser (HTML / CSS / JavaScript)
        ↓ GET /api/research/{symbol}
FastAPI backend
        ↓
MarketDataProvider
        ↓
Yahoo Finance public chart endpoint
        ↓
Normalize market data
        ↓
Pydantic validation
        ↓
JSON response
        ↓
Browser
```

這個專案是研究工具，不會產生 Buy / Sell、進場價、停損或目標價。

## Demo

<img src="https://raw.githubusercontent.com/xunnnn0417/financial-research-assistant/main/docs/images/03-result.png" alt="Financial Research Assistant result" width="900">

## 目前功能

- 查詢最新可取得的市場價格與漲跌幅
- 顯示最近 5 根日線 OHLC
- 以固定格式回傳 JSON
- 使用 Pydantic 驗證 API response
- 處理 invalid symbol、provider failure、rate limit 等錯誤
- 透過 `MarketDataProvider` 隔離外部資料來源
- `XAUUSD` 會轉成 Yahoo 使用的 `XAUUSD=X`
- GitHub Actions 自動執行 lint 與 tests

## Tech Stack

- Python / FastAPI / Uvicorn
- Pydantic / HTTPX
- HTML / CSS / Vanilla JavaScript
- pytest / Ruff / GitHub Actions

## API

| Method | Endpoint | 用途 |
| --- | --- | --- |
| `GET` | `/health` | 確認 backend 是否正常運作 |
| `GET` | `/api/research/{symbol}` | 查詢並回傳整理後的市場資料 |

成功回應會包含：

```json
{
  "symbol": "AAPL",
  "provider_symbol": "AAPL",
  "price": 123.45,
  "change_percent": 1.2,
  "ohlc": [],
  "summary": "...",
  "source": "Yahoo Finance (public chart endpoint)",
  "fetched_at": "..."
}
```

## Project Structure

```text
backend/
  main.py              FastAPI routes
  schemas.py           Pydantic response models
  providers/           外部市場資料來源
  services/            資料整理與 research logic

frontend/
  index.html
  styles.css
  app.js

tests/
  API / schema / error-path tests
```

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

打開：`http://127.0.0.1:8000`

FastAPI 文件：`http://127.0.0.1:8000/docs`

## Tests

```powershell
pytest
ruff check .
```

單元測試使用 fake provider，避免每次測試都依賴外部網路；live market data 則另外做 integration check。

## Limitations

- Yahoo Finance public endpoint 可能延遲、限流或改變格式。
- `XAUUSD=X` 是 Yahoo 的 ticker convention，不代表 institutional-grade spot feed。
- 目前沒有新聞、LLM summary、登入、資料庫或交易功能。

## Next

下一版預計加入：

- 有來源引用的 financial news
- LLM research summary
- Prompt testing / version comparison
- AI response schema validation
