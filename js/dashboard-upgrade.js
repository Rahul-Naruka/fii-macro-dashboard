/**
 * FII Macro Dashboard Upgrade Module
 * Includes:
 * 1. 1M, 3M, 1YAbsolute & 3Y, 5Y Annualized CAGR Calculation Engine
 * 2. Daily FII/DII & Macro Feed Parser
 * 3. MoM Dynamic Asset Allocation & Suggested Mutual Funds by Risk Profile
 */

let globalDashboardData = null;

/**
 * Calculates 1M, 3M, 1Y, 3Y, and 5Y CAGR/Returns from a sorted [{date, value}] array
 */
function calculateHorizonsCAGR(historicalData) {
  if (!historicalData || historicalData.length < 2) return null;

  const latest = historicalData[historicalData.length - 1];
  const latestDate = new Date(latest.date);
  const latestVal = parseFloat(latest.value);

  const findClosestValue = (targetDate) => {
    let closest = historicalData[0];
    let minDiff = Math.abs(new Date(closest.date) - targetDate);
    for (let i = 0; i < historicalData.length; i++) {
      const row = historicalData[i];
      const diff = Math.abs(new Date(row.date) - targetDate);
      if (diff < minDiff) {
        minDiff = diff;
        closest = row;
      }
    }
    return parseFloat(closest.value);
  };

  const getPastDate = (months = 0, years = 0) => {
    const d = new Date(latestDate);
    if (months) d.setMonth(d.getMonth() - months);
    if (years) d.setFullYear(d.getFullYear() - years);
    return d;
  };

  const val1M = findClosestValue(getPastDate(1, 0));
  const val3M = findClosestValue(getPastDate(3, 0));
  const val1Y = findClosestValue(getPastDate(0, 1));
  const val3Y = findClosestValue(getPastDate(0, 3));
  const val5Y = findClosestValue(getPastDate(0, 5));

  const calcAbs = (curr, prev) => (prev > 0 ? (((curr - prev) / prev) * 100).toFixed(2) : "0.00");
  const calcCAGR = (curr, prev, n) => (prev > 0 ? ((Math.pow(curr / prev, 1 / n) - 1) * 100).toFixed(2) : "0.00");

  return {
    asOf: latest.date,
    latestValue: latestVal,
    r1M: calcAbs(latestVal, val1M),
    r3M: calcAbs(latestVal, val3M),
    cagr1Y: calcAbs(latestVal, val1Y),
    cagr3Y: calcCAGR(latestVal, val3Y, 3),
    cagr5Y: calcCAGR(latestVal, val5Y, 5)
  };
}

/**
 * Risk Profile MoM Asset Allocation Definitions & Suggested Funds
 */
const RISK_PROFILES = {
  conservative: {
    name: "Conservative Profile",
    horizon: "1 to 3 Years",
    baseWeights: { equity: 20, debt: 65, gold: 10, cash: 5 },
    rebalanceNote: "Capital preservation priority. During FII selling months, keep equity restricted to Hybrid/BAF and lock in high corporate bond yields.",
    funds: [
      { name: "HDFC Corporate Bond Fund (Direct-Growth)", category: "Corporate Bond / Debt Core", weight: "35%", code: "119598" },
      { name: "Kotak Equity Arbitrage Fund (Direct-Growth)", category: "Tax-Efficient Arbitrage / Debt Proxy", weight: "25%", code: "119775" },
      { name: "ICICI Prudential Balanced Advantage Fund", category: "Dynamic Asset Allocation (Low Volatility Equity)", weight: "20%", code: "120503" },
      { name: "SBI Conservative Hybrid Fund", category: "Conservative Hybrid", weight: "10%", code: "119828" },
      { name: "Nippon India ETF Gold BeES / Gold FoF", category: "Sovereign / Gold Hedge", weight: "10%", code: "GOLDBEES" }
    ]
  },
  moderate: {
    name: "Moderately Conservative / Income+",
    horizon: "3 to 5 Years",
    baseWeights: { equity: 40, debt: 45, gold: 10, cash: 5 },
    rebalanceNote: "Steady inflation-beating compounding. MoM FII outflows trigger a 5% shift from pure Large Cap into Multi-Asset & Arbitrage.",
    funds: [
      { name: "ICICI Prudential Multi-Asset Fund", category: "Multi-Asset Allocation (Equity + Debt + Gold)", weight: "25%", code: "120323" },
      { name: "Nippon India Large Cap Fund (Direct-Growth)", category: "Core Large Cap Equity", weight: "20%", code: "118778" },
      { name: "HDFC Corporate Bond Fund (Direct-Growth)", category: "High-Grade Corporate Debt", weight: "30%", code: "119598" },
      { name: "Edelweiss Balanced Advantage Fund", category: "Dynamic Equity / Trend Following", weight: "15%", code: "118668" },
      { name: "ICICI Prudential Money Market Fund", category: "Liquid / Tactical Deployment Reserve", weight: "10%", code: "120594" }
    ]
  },
  balanced: {
    name: "Balanced / Moderate Growth",
    horizon: "5+ Years",
    baseWeights: { equity: 60, debt: 25, gold: 10, cash: 5 },
    rebalanceNote: "Optimal risk-adjusted core portfolio. When monthly FII selling exceeds ₹15,000 Cr, deploy tactical cash into Flexi Cap & Large Cap on dips.",
    funds: [
      { name: "Parag Parikh Flexi Cap Fund (Direct-Growth)", category: "Core Flexi Cap Compounder", weight: "25%", code: "122639" },
      { name: "Nippon India Large Cap Fund (Direct-Growth)", category: "Large Cap Institutional Core", weight: "20%", code: "118778" },
      { name: "Mirae Asset Aggressive Hybrid Fund", category: "Aggressive Hybrid (Equity + Debt)", weight: "15%", code: "135793" },
      { name: "HDFC Corporate Bond Fund", category: "Fixed Income Cushion", weight: "25%", code: "119598" },
      { name: "Nippon India Gold Savings Fund", category: "Macro & Currency Hedge", weight: "15%", code: "118834" }
    ]
  },
  aggressive: {
    name: "Aggressive Growth",
    horizon: "7+ Years",
    baseWeights: { equity: 75, debt: 15, gold: 5, cash: 5 },
    rebalanceNote: "High equity beta. Use FII-driven corrections to rebalance MoM from Arbitrage/Debt into Midcap and Flexi Cap leaders.",
    funds: [
      { name: "Parag Parikh Flexi Cap Fund (Direct-Growth)", category: "Core Flexi Cap", weight: "30%", code: "122639" },
      { name: "Motilal Oswal Midcap Fund (Direct-Growth)", category: "High-Growth Mid Cap", weight: "25%", code: "127042" },
      { name: "Nippon India Large Cap Fund (Direct-Growth)", category: "Large Cap Anchor", weight: "20%", code: "118778" },
      { name: "Kotak Equity Arbitrage Fund", category: "Tactical Buy-on-Dip Reserve", weight: "15%", code: "119775" },
      { name: "Nippon India Gold ETF / Silver FoF", category: "Precious Metals Hedge", weight: "10%", code: "GOLDBEES" }
    ]
  },
  very_aggressive: {
    name: "Very Aggressive / Alpha Seeker",
    horizon: "7 to 10+ Years",
    baseWeights: { equity: 90, debt: 5, gold: 5, cash: 0 },
    rebalanceNote: "Maximum wealth creation across market caps. Maintain strict MoM SIP discipline through FII volatility cycles.",
    funds: [
      { name: "Parag Parikh Flexi Cap Fund (Direct-Growth)", category: "Core All-Cap Compounder", weight: "30%", code: "122639" },
      { name: "Motilal Oswal Midcap Fund (Direct-Growth)", category: "Mid Cap Alpha", weight: "25%", code: "127042" },
      { name: "Nippon India Small Cap Fund (Direct-Growth)", category: "Small Cap Multibagger Basket", weight: "20%", code: "125497" },
      { name: "HDFC Large and Mid Cap Fund", category: "Large & Mid Cap Core", weight: "15%", code: "118989" },
      { name: "ICICI Pru Multi-Asset / Gold ETF", category: "Downside Hedge & Dry Powder", weight: "10%", code: "120323" }
    ]
  }
};

function formatBadge(val) {
  const num = parseFloat(val);
  const cls = num >= 0 ? "val-pos" : "val-neg";
  const sign = num > 0 ? "+" : "";
  return `<span class="val-badge ${cls}">${sign}${num.toFixed(2)}%</span>`;
}

function renderCAGRTable(filterType = "all") {
  if (!globalDashboardData) return;
  const tbody = document.getElementById("cagr-table-body");
  tbody.innerHTML = "";

  const rows = [];

  if (filterType === "all" || filterType === "indices") {
    const indices = globalDashboardData.indices || {};
    Object.keys(indices).forEach((key) => {
      const item = indices[key];
      const metrics = calculateHorizonsCAGR(item.history);
      if (metrics) {
        rows.push({
          name: item.name,
          category: item.category,
          metrics
        });
      }
    });
  }

  if (filterType === "all" || filterType === "funds") {
    const funds = globalDashboardData.funds || {};
    Object.keys(funds).forEach((key) => {
      const item = funds[key];
      const metrics = calculateHorizonsCAGR(item.history);
      if (metrics) {
        rows.push({
          name: item.name,
          category: item.category,
          metrics
        });
      }
    });
  }

  rows.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${r.name}</strong></td>
      <td><span class="cat-tag">${r.category}</span></td>
      <td><strong>${r.metrics.latestValue.toLocaleString("en-IN")}</strong> <small style="color:#64748b;display:block;font-size:0.72rem;">as of ${r.metrics.asOf}</small></td>
      <td>${formatBadge(r.metrics.r1M)}</td>
      <td>${formatBadge(r.metrics.r3M)}</td>
      <td>${formatBadge(r.metrics.cagr1Y)}</td>
      <td>${formatBadge(r.metrics.cagr3Y)}</td>
      <td>${formatBadge(r.metrics.cagr5Y)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderRiskAllocation(profileKey) {
  const profile = RISK_PROFILES[profileKey];
  if (!profile) return;

  // Toggle active button state
  document.querySelectorAll(".risk-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.profile === profileKey);
  });

  // Apply tactical MoM FII tilt
  const tilt = globalDashboardData?.macroRegime?.tacticalEquityTiltPct || 0;
  const eqWeight = Math.max(5, Math.min(95, profile.baseWeights.equity + tilt));
  const debtWeight = Math.max(5, Math.min(90, profile.baseWeights.debt - tilt));
  const goldWeight = profile.baseWeights.gold;
  const cashWeight = profile.baseWeights.cash;

  const barsContainer = document.getElementById("alloc-bars-container");
  barsContainer.innerHTML = `
    <div style="margin-bottom: 1rem;">
      <h3 style="font-size: 1.05rem; color: #fff;">${profile.name}</h3>
      <span style="font-size: 0.8rem; color: #94a3b8;">Recommended Horizon: ${profile.horizon}</span>
    </div>

    <div class="alloc-bar-row">
      <div class="alloc-bar-label">
        <span><strong>Equity</strong> (Base ${profile.baseWeights.equity}% ${tilt !== 0 ? `| MoM Tactical ${tilt > 0 ? '+' : ''}${tilt}%` : ''})</span>
        <span style="color: #38bdf8; font-weight: 700;">${eqWeight}%</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width: ${eqWeight}%; background: #38bdf8;"></div></div>
    </div>

    <div class="alloc-bar-row">
      <div class="alloc-bar-label">
        <span><strong>Debt & Arbitrage</strong> (Base ${profile.baseWeights.debt}% ${tilt !== 0 ? `| MoM Tactical ${-tilt > 0 ? '+' : ''}${-tilt}%` : ''})</span>
        <span style="color: #10b981; font-weight: 700;">${debtWeight}%</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width: ${debtWeight}%; background: #10b981;"></div></div>
    </div>

    <div class="alloc-bar-row">
      <div class="alloc-bar-label">
        <span><strong>Gold / Precious Metals</strong></span>
        <span style="color: #f59e0b; font-weight: 700;">${goldWeight}%</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width: ${goldWeight}%; background: #f59e0b;"></div></div>
    </div>

    <div class="alloc-bar-row">
      <div class="alloc-bar-label">
        <span><strong>Tactical Liquid / Cash</strong></span>
        <span style="color: #a855f7; font-weight: 700;">${cashWeight}%</span>
      </div>
      <div class="progress-track"><div class="progress-fill" style="width: ${cashWeight}%; background: #a855f7;"></div></div>
    </div>

    <div class="mom-note-box">
      <strong>MoM Rebalancing Guidance:</strong> ${profile.rebalanceNote}
    </div>
  `;

  const fundsContainer = document.getElementById("suggested-funds-container");
  fundsContainer.innerHTML = profile.funds
    .map(
      (f) => `
    <div class="fund-item">
      <div class="fund-info">
        <h4>${f.name}</h4>
        <p>${f.category} &bull; Scheme Ref: ${f.code}</p>
      </div>
      <div class="fund-weight">${f.weight}</div>
    </div>
  `
    )
    .join("");
}

function renderTopKPIs(data) {
  const fiiLatest = data.latestFiiDii?.FII || { netValue: 0, date: "N/A" };
  const diiLatest = data.latestFiiDii?.DII || { netValue: 0, date: "N/A" };
  const regime = data.macroRegime || {};

  document.getElementById("last-updated-text").textContent = `Last Daily Sync: ${data.lastUpdated}`;

  const fiiEl = document.getElementById("kpi-fii-net");
  fiiEl.textContent = `₹${fiiLatest.netValue.toLocaleString("en-IN")} Cr`;
  fiiEl.style.color = fiiLatest.netValue >= 0 ? "var(--pos-green)" : "var(--neg-red)";
  document.getElementById("kpi-fii-date").textContent = `Cash Provisional (${fiiLatest.date})`;

  const diiEl = document.getElementById("kpi-dii-net");
  diiEl.textContent = `₹${diiLatest.netValue.toLocaleString("en-IN")} Cr`;
  diiEl.style.color = diiLatest.netValue >= 0 ? "var(--pos-green)" : "var(--neg-red)";
  document.getElementById("kpi-dii-date").textContent = `Institutional Domestic (${diiLatest.date})`;

  const momEl = document.getElementById("kpi-mom-fii");
  momEl.textContent = `₹${(regime.trailingMonthlyFiiNetCr || 0).toLocaleString("en-IN")} Cr`;
  momEl.style.color = (regime.trailingMonthlyFiiNetCr || 0) >= 0 ? "var(--pos-green)" : "var(--neg-red)";

  document.getElementById("kpi-regime-status").textContent = regime.regimeStatus || "Balanced";
}

async function initDashboard() {
  try {
    const res = await fetch("./data/daily-fii-macro.json");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    globalDashboardData = await res.json();

    renderTopKPIs(globalDashboardData);
    renderCAGRTable("all");
    renderRiskAllocation("balanced");
  } catch (err) {
    console.error("Failed loading daily-fii-macro.json:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();

  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      e.target.classList.add("active");
      renderCAGRTable(e.target.dataset.filter);
    });
  });

  document.querySelectorAll(".risk-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      renderRiskAllocation(e.target.dataset.profile);
    });
  });
});
