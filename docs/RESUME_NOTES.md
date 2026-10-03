# Resume and interview notes

## Chinese resume

**Financial Research Assistant｜個人專案**  
以 FastAPI、vanilla JavaScript 建立市場研究網頁；串接公開市場資料、正規化 OHLC 欄位並以 Pydantic 驗證固定 JSON schema。實作健康檢查、invalid symbol / timeout / rate-limit 錯誤處理與 pytest，提供股票及 XAUUSD 對應查詢的研究資訊介面。

## English bullet points

- Built a Financial Research Assistant with FastAPI and vanilla JavaScript to present latest available prices, percent changes, and recent OHLC data.
- Designed a provider abstraction and normalized public market-data responses into a Pydantic-validated API contract.
- Added safe error handling and pytest coverage; kept the product scoped to descriptive research rather than trading signals.

## 30-second introduction

我做了一個 Financial Research Assistant，讓使用者輸入 AAPL、NVDA 或 XAUUSD 後，網頁透過 FastAPI 取得公開市場資料，再把 OHLC 與價格變動以固定 JSON 顯示。我刻意沒有做交易訊號，而是把重點放在資料流程：provider 資料先正規化、再由 Pydantic 驗證，最後才交給前端，讓我能清楚處理外部資料不穩定的問題。

## 2-minute introduction

這個專案的目標不是預測市場，而是把我平常的金融研究工作流程做成可驗證的小型工具。使用者在瀏覽器輸入商品代號，JavaScript 用 `fetch()` 呼叫我們自己的 FastAPI。後端不讓前端直接碰市場資料來源，而是透過 `MarketDataProvider`。目前的 Yahoo provider 取回每日資料後，把供應商原本欄位式的 JSON 轉成一筆一筆 OHLC candle，再交給 Pydantic `ResearchResponse` 檢查資料型態與必要欄位。這樣前端只需要理解一種資料格式。

我選 Yahoo 的公開 endpoint 是因為 V1 不需 API key，方便重現；代價是有 rate limit 或服務變動的風險，所以程式會回傳可讀錯誤而不是 Python traceback。測試方面，我用 fake provider 驗證 schema，不讓單元測試依賴網路。下一步我會先加上有引用來源的新聞，再把 LLM summary 接在目前的 deterministic summary 後面。

## 15 likely questions and reference answers

1. **Why separate frontend and backend?** The browser handles interaction; the backend protects provider details and creates one stable data contract.
2. **What does `fetch()` do?** It sends an HTTP request from JavaScript and gives back the JSON response asynchronously.
3. **Why FastAPI?** It is concise, validates models naturally with Pydantic, and generates `/docs`.
4. **Why Pydantic?** It checks that outgoing research data has expected types and required fields before the browser receives it.
5. **Why a provider abstraction?** Provider payloads and terms differ; only the provider module should change when replacing Yahoo.
6. **How do you handle bad symbols?** The backend validates symbol characters, then converts a provider “not found” response into a safe 400 error.
7. **How do you handle rate limits?** It returns a readable 503 response and the UI shows it instead of a traceback.
8. **Why not call Yahoo from JavaScript?** A backend centralizes validation, avoids CORS/provider coupling, and leaves a safe place for future secrets.
9. **Is the displayed price real-time?** No guarantee. It is the latest value the provider made available.
10. **Why map XAUUSD?** Yahoo uses `XAUUSD=X`; the app makes that translation explicit rather than pretending all providers use the same ticker.
11. **What is OHLC?** Open, high, low, and close for a time period; here one day.
12. **How is percent change calculated?** `(latest price - previous close) / previous close * 100`.
13. **Why fake the provider in tests?** Unit tests should be fast and deterministic; live availability is tested separately.
14. **Where would an LLM go?** Replace or extend `build_market_summary` after source data is normalized and schema validation remains in place.
15. **What would you improve?** Add cited news, caching, provider fallbacks, and explicit market-session metadata.

## Do not overclaim

Do not describe this as an AI Engineer system, a real-time feed, a trading bot, financial advice, or an institutional-grade data platform. Say it is a personal financial + AI-workflow application project using public data and a deliberately scoped V1.

