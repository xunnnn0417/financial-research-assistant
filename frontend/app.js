const input = document.querySelector("#symbol");
const button = document.querySelector("#research-button");
const statusText = document.querySelector("#status");
const result = document.querySelector("#result");

function formatNumber(value) { return new Intl.NumberFormat("en-US", { maximumFractionDigits: 4 }).format(value); }
function formatVolume(value) { return value === null ? "—" : new Intl.NumberFormat("en-US").format(value); }

function showResult(data) {
  document.querySelector("#result-symbol").textContent = data.symbol;
  document.querySelector("#price").textContent = formatNumber(data.price);
  const change = document.querySelector("#change");
  change.textContent = `${data.change_percent >= 0 ? "+" : ""}${data.change_percent.toFixed(2)}%`;
  change.className = data.change_percent >= 0 ? "positive" : "negative";
  document.querySelector("#summary").textContent = data.summary;
  document.querySelector("#source").textContent = `Source: ${data.source} · Provider symbol: ${data.provider_symbol}`;
  document.querySelector("#updated-at").textContent = `Fetched: ${new Date(data.fetched_at).toLocaleString()}`;
  document.querySelector("#ohlc-body").innerHTML = data.ohlc.map(candle => `<tr><td>${candle.date}</td><td>${formatNumber(candle.open)}</td><td>${formatNumber(candle.high)}</td><td>${formatNumber(candle.low)}</td><td>${formatNumber(candle.close)}</td><td>${formatVolume(candle.volume)}</td></tr>`).join("");
  result.classList.remove("hidden");
}

async function runResearch() {
  const symbol = input.value.trim().toUpperCase();
  if (!symbol) { statusText.textContent = "Enter a market symbol first."; return; }
  button.disabled = true; result.classList.add("hidden"); statusText.textContent = `Researching ${symbol}…`;
  try {
    const response = await fetch(`/api/research/${encodeURIComponent(symbol)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Research request failed.");
    showResult(payload); statusText.textContent = "Research data loaded.";
  } catch (error) { statusText.textContent = `Could not load research: ${error.message}`; }
  finally { button.disabled = false; }
}
button.addEventListener("click", runResearch);
input.addEventListener("keydown", event => { if (event.key === "Enter") runResearch(); });

