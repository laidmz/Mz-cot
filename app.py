import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import zipfile
import io
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="MZ.COT",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Premium CSS ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg0:     #03070d;
    --bg1:     #060e18;
    --bg2:     #091525;
    --bg3:     #0d1e33;
    --line:    #112240;
    --line2:   #1a3358;
    --c1:      #00d4ff;
    --c1dim:   #0a4a5c;
    --c2:      #ff6b35;
    --c2dim:   #5c2a14;
    --c3:      #00ff88;
    --c3dim:   #005c30;
    --warn:    #ffcc00;
    --danger:  #ff3355;
    --text:    #c8dff0;
    --text2:   #6b8fad;
    --text3:   #334d66;
    --mono:    'Space Mono', monospace;
    --display: 'Bebas Neue', sans-serif;
    --body:    'DM Sans', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: var(--body) !important;
    background: var(--bg0) !important;
    color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.main > div { padding: 0 !important; }

/* ── Top Bar ── */
.topbar {
    background: var(--bg1);
    border-bottom: 1px solid var(--line);
    padding: 0.6rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
}
.topbar-logo {
    font-family: var(--display);
    font-size: 1.6rem;
    letter-spacing: 0.12em;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.topbar-logo span { color: var(--c1); }
.topbar-logo sub {
    font-family: var(--mono);
    font-size: 0.55rem;
    color: var(--text2);
    letter-spacing: 0.15em;
    vertical-align: middle;
    margin-left: 0.3rem;
}
.topbar-status {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--text2);
}
.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--c3);
    box-shadow: 0 0 6px var(--c3);
    animation: pulse 2s infinite;
    display: inline-block;
    margin-right: 0.3rem;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Main Layout ── */
.main-wrapper {
    display: flex;
    min-height: calc(100vh - 48px);
}
.content-area {
    flex: 1;
    padding: 1.5rem 1.8rem;
    overflow-x: hidden;
}

/* ── Market Header ── */
.mkt-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 1.4rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--line);
}
.mkt-name {
    font-family: var(--display);
    font-size: 2.8rem;
    letter-spacing: 0.06em;
    color: #fff;
    line-height: 1;
}
.mkt-name span { color: var(--c1); }
.mkt-meta {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--text2);
    margin-top: 0.2rem;
    letter-spacing: 0.1em;
}
.report-date {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--c1);
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.15);
    padding: 0.4rem 0.9rem;
    border-radius: 4px;
    letter-spacing: 0.08em;
}

/* ── Stats Grid ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.5rem;
}
.stat-cell {
    background: var(--bg1);
    padding: 1.1rem 1.3rem;
    position: relative;
    transition: background 0.15s;
}
.stat-cell:hover { background: var(--bg2); }
.stat-cell::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
}
.stat-cell.c1::after { background: var(--c1); }
.stat-cell.c2::after { background: var(--c2); }
.stat-cell.c3::after { background: var(--c3); }
.stat-tag {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    color: var(--text3);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.stat-val {
    font-family: var(--mono);
    font-size: 1.5rem;
    font-weight: 700;
    color: #fff;
    line-height: 1;
    margin-bottom: 0.35rem;
    letter-spacing: -0.02em;
}
.stat-chg {
    font-family: var(--mono);
    font-size: 0.68rem;
    font-weight: 700;
}
.up   { color: var(--c3); }
.down { color: var(--danger); }
.neu  { color: var(--text2); }

/* ── COT Index Bar inside stat cell ── */
.idx-bar-wrap {
    margin-top: 0.7rem;
    padding-top: 0.6rem;
    border-top: 1px solid var(--line);
}
.idx-bar-label {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 0.6rem;
    color: var(--text2);
    margin-bottom: 0.3rem;
}
.idx-bar-track {
    height: 3px;
    background: var(--line2);
    border-radius: 2px;
    position: relative;
}
.idx-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.6s ease;
}

/* ── Section label ── */
.sec-label {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: var(--text2);
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.4rem 0 0.7rem;
}
.sec-label::before {
    content: '';
    width: 16px; height: 1px;
    background: var(--c1);
}
.sec-label::after {
    content: '';
    flex: 1; height: 1px;
    background: var(--line);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg1) !important;
    border-right: 1px solid var(--line) !important;
    min-width: 220px !important;
    max-width: 240px !important;
}
[data-testid="stSidebar"] > div {
    padding: 1.2rem 1rem !important;
}
.sb-logo {
    font-family: var(--mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: var(--text3);
    text-transform: uppercase;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--line);
}
.sb-logo b { color: var(--c1); }

[data-testid="stSidebar"] label {
    font-family: var(--mono) !important;
    font-size: 0.6rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text2) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--bg2) !important;
    border: 1px solid var(--line2) !important;
    border-radius: 4px !important;
    font-family: var(--mono) !important;
    font-size: 0.75rem !important;
}
.sb-legend {
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
}
.sb-legend-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
    font-size: 0.72rem;
    color: var(--text2);
    line-height: 1.4;
}
.sb-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-top: 3px;
    flex-shrink: 0;
}

/* ── Footer ── */
.app-footer {
    margin-top: 2rem;
    padding: 1rem 0;
    border-top: 1px solid var(--line);
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 0.6rem;
    color: var(--text3);
    letter-spacing: 0.08em;
}

/* ── Streamlit overrides ── */
hr { border-color: var(--line) !important; margin: 0.8rem 0 !important; }
[data-testid="stDataFrame"] {
    border: 1px solid var(--line) !important;
    border-radius: 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Data Config ──────────────────────────────────────────────
MARKETS = {
    "EUR/USD":  "EURO FX",
    "GBP/USD":  "BRITISH POUND",
    "JPY/USD":  "JAPANESE YEN",
    "AUD/USD":  "AUSTRALIAN DOLLAR",
    "CAD/USD":  "CANADIAN DOLLAR",
    "CHF/USD":  "SWISS FRANC",
    "NZD/USD":  "NEW ZEALAND DOLLAR",
    "XAU/USD":  "GOLD",
    "XAG/USD":  "SILVER",
    "CRUDE OIL":"CRUDE OIL",
    "S&P 500":  "S&P 500",
    "NAS 100":  "NASDAQ-100",
}

DATE_COL     = "Report_Date_as_YYYY-MM-DD"
MKT_COL      = "Market_and_Exchange_Names"
LEV_LONG     = "Lev_Money_Positions_Long_All"
LEV_SHORT    = "Lev_Money_Positions_Short_All"
ASSET_LONG   = "Asset_Mgr_Positions_Long_All"
ASSET_SHORT  = "Asset_Mgr_Positions_Short_All"
DEALER_LONG  = "Dealer_Positions_Long_All"
DEALER_SHORT = "Dealer_Positions_Short_All"

# ─── Load Data ─────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="LOADING CFTC DATA...")
def load_cot_data():
    years = [datetime.now().year, datetime.now().year - 1]
    all_dfs = []
    for year in years:
        url = f"https://www.cftc.gov/files/dea/history/fut_fin_txt_{year}.zip"
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                fname = [f for f in z.namelist() if f.endswith('.txt')][0]
                with z.open(fname) as f:
                    all_dfs.append(pd.read_csv(f, low_memory=False))
        except Exception as e:
            st.warning(f"Year {year}: {e}")
    if not all_dfs:
        return None
    data = pd.concat(all_dfs, ignore_index=True)
    data[DATE_COL] = pd.to_datetime(data[DATE_COL], errors='coerce')
    return data.sort_values(DATE_COL)

def cot_index(s, p=52):
    mn = s.rolling(p).min()
    mx = s.rolling(p).max()
    return ((s - mn) / (mx - mn).replace(0, pd.NA) * 100).round(1)

def fmt(n):
    n = int(n)
    if abs(n) >= 1000:
        return f"{n/1000:.1f}K"
    return f"{n:,}"

def chg_fmt(n):
    n = int(n)
    sign = "▲" if n > 0 else "▼"
    cls  = "up" if n > 0 else "down"
    return sign, fmt(abs(n)), cls

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-logo"><b>MZ.COT</b> · CONFIG</div>', unsafe_allow_html=True)
    mkt_key  = st.selectbox("MARKET", list(MARKETS.keys()), label_visibility="visible")
    weeks    = st.slider("LOOKBACK WKS", 26, 156, 52, step=13)
    show_idx = st.toggle("COT INDEX", value=True)
    show_tbl = st.toggle("DATA TABLE", value=False)

    st.markdown("""
    <div class="sb-legend">
        <div class="sb-legend-item">
            <div class="sb-dot" style="background:#00d4ff"></div>
            <div><b style="color:#c8dff0">Leveraged Money</b><br>Hedge funds · large specs</div>
        </div>
        <div class="sb-legend-item">
            <div class="sb-dot" style="background:#ff6b35"></div>
            <div><b style="color:#c8dff0">Asset Manager</b><br>Institutional · commercial</div>
        </div>
        <div class="sb-legend-item">
            <div class="sb-dot" style="background:#00ff88"></div>
            <div><b style="color:#c8dff0">Dealer / Banks</b><br>Prime brokers · banks</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Top Bar ───────────────────────────────────────────────────
now_str = datetime.now().strftime("%d %b %Y · %H:%M UTC")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-logo">MZ<span>.</span>COT<sub>COMMITMENT OF TRADERS</sub></div>
    <div class="topbar-status">
        <span><span class="status-dot"></span>LIVE</span>
        <span>{now_str}</span>
        <span>CFTC · FIN TRADERS</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Load & Filter ─────────────────────────────────────────────
data = load_cot_data()
if data is None:
    st.error("FAILED TO LOAD DATA")
    st.stop()

mask = data[MKT_COL].str.upper().str.contains(MARKETS[mkt_key].upper(), na=False)
df   = data[mask].copy().tail(weeks)
if df.empty:
    st.error(f"NO DATA: {mkt_key}")
    st.stop()

df['Net_Lev']    = pd.to_numeric(df[LEV_LONG],    errors='coerce') - pd.to_numeric(df[LEV_SHORT],    errors='coerce')
df['Net_Asset']  = pd.to_numeric(df[ASSET_LONG],  errors='coerce') - pd.to_numeric(df[ASSET_SHORT],  errors='coerce')
df['Net_Dealer'] = pd.to_numeric(df[DEALER_LONG], errors='coerce') - pd.to_numeric(df[DEALER_SHORT], errors='coerce')
df['IDX_Lev']    = cot_index(df['Net_Lev'])
df['IDX_Asset']  = cot_index(df['Net_Asset'])

latest = df.iloc[-1]
prev   = df.iloc[-2]

# ─── Market Header ─────────────────────────────────────────────
pair_parts = mkt_key.split("/") if "/" in mkt_key else [mkt_key, ""]
st.markdown(f"""
<div class="mkt-header">
    <div>
        <div class="mkt-name">{pair_parts[0]}<span>/{pair_parts[1] if len(pair_parts)>1 else ''}</span></div>
        <div class="mkt-meta">CFTC FINANCIAL TRADERS REPORT · {weeks}W LOOKBACK</div>
    </div>
    <div class="report-date">LATEST REPORT · {latest[DATE_COL].strftime('%d %b %Y').upper()}</div>
</div>
""", unsafe_allow_html=True)

# ─── Stats Grid ────────────────────────────────────────────────
def idx_bar(val, color):
    if pd.isna(val):
        return ""
    bar_color = "#00ff88" if val > 75 else ("#ff3355" if val < 25 else "#ffcc00")
    label = "EXTREME LONG" if val > 75 else ("EXTREME SHORT" if val < 25 else "NEUTRAL")
    return f"""
    <div class="idx-bar-wrap">
        <div class="idx-bar-label"><span>COT INDEX</span><span style="color:{bar_color}">{val:.0f}/100 · {label}</span></div>
        <div class="idx-bar-track"><div class="idx-bar-fill" style="width:{val}%;background:{bar_color}"></div></div>
    </div>"""

lev_s, lev_v, lev_c   = chg_fmt(latest['Net_Lev']    - prev['Net_Lev'])
ast_s, ast_v, ast_c   = chg_fmt(latest['Net_Asset']   - prev['Net_Asset'])
dlr_s, dlr_v, dlr_c   = chg_fmt(latest['Net_Dealer']  - prev['Net_Dealer'])

st.markdown(f"""
<div class="stats-grid">
    <div class="stat-cell c1">
        <div class="stat-tag">LEVERAGED MONEY</div>
        <div class="stat-val">{fmt(latest['Net_Lev'])}</div>
        <div class="stat-chg {lev_c}">{lev_s} {lev_v} contracts WoW</div>
        {idx_bar(latest['IDX_Lev'], '#00d4ff') if show_idx else ''}
    </div>
    <div class="stat-cell c2">
        <div class="stat-tag">ASSET MANAGER</div>
        <div class="stat-val">{fmt(latest['Net_Asset'])}</div>
        <div class="stat-chg {ast_c}">{ast_s} {ast_v} contracts WoW</div>
        {idx_bar(latest['IDX_Asset'], '#ff6b35') if show_idx else ''}
    </div>
    <div class="stat-cell c3">
        <div class="stat-tag">DEALER / BANKS</div>
        <div class="stat-val">{fmt(latest['Net_Dealer'])}</div>
        <div class="stat-chg {dlr_c}">{dlr_s} {dlr_v} contracts WoW</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Chart Theme ───────────────────────────────────────────────
LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Space Mono, monospace', color='#6b8fad', size=10),
    margin=dict(l=8, r=8, t=8, b=8),
    xaxis=dict(showgrid=False, zeroline=False, linecolor='#112240',
               tickfont=dict(size=9), color='#334d66'),
    yaxis=dict(showgrid=True, gridcolor='rgba(17,34,64,0.9)',
               zeroline=False, tickfont=dict(size=9), color='#334d66'),
    hovermode='x unified',
    hoverlabel=dict(bgcolor='#060e18', bordercolor='#1a3358',
                    font=dict(color='#c8dff0', family='Space Mono', size=11)),
    legend=dict(orientation="h", y=1.08, font=dict(size=10),
                bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
)

# ─── Net Positions Chart ───────────────────────────────────────
st.markdown('<div class="sec-label">NET POSITIONS OVER TIME</div>', unsafe_allow_html=True)

fig = go.Figure()
for col, name, color, fill in [
    ('Net_Lev',    'Leveraged Money', '#00d4ff', 'rgba(0,212,255,0.06)'),
    ('Net_Asset',  'Asset Manager',   '#ff6b35', 'rgba(255,107,53,0.06)'),
    ('Net_Dealer', 'Dealer/Banks',    '#00ff88', 'rgba(0,255,136,0.04)'),
]:
    fig.add_trace(go.Scatter(
        x=df[DATE_COL], y=df[col], name=name,
        line=dict(color=color, width=1.8),
        fill='tozeroy', fillcolor=fill,
        hovertemplate=f'<b>{name}</b>: %{{y:,.0f}}<extra></extra>'
    ))
fig.add_hline(y=0, line_color='#1a3358', line_width=1)
fig.update_layout(**LAYOUT, height=360)
st.plotly_chart(fig, use_container_width=True)

# ─── COT Index Chart ───────────────────────────────────────────
if show_idx:
    st.markdown('<div class="sec-label">COT INDEX · POSITIONING EXTREMES</div>', unsafe_allow_html=True)

    fig2 = go.Figure()
    fig2.add_hrect(y0=75, y1=100, fillcolor="rgba(0,255,136,0.04)", line_width=0)
    fig2.add_hrect(y0=0,  y1=25,  fillcolor="rgba(255,51,85,0.04)", line_width=0)
    fig2.add_trace(go.Scatter(
        x=df[DATE_COL], y=df['IDX_Lev'],
        name="Lev. Money Index",
        line=dict(color='#00d4ff', width=2),
        fill='tozeroy', fillcolor='rgba(0,212,255,0.04)',
        hovertemplate='<b>Lev. Index</b>: %{y:.1f}<extra></extra>'
    ))
    fig2.add_trace(go.Scatter(
        x=df[DATE_COL], y=df['IDX_Asset'],
        name="Asset Mgr Index",
        line=dict(color='#ff6b35', width=1.5, dash='dash'),
        hovertemplate='<b>Asset Index</b>: %{y:.1f}<extra></extra>'
    ))
    for y_val, color, label in [(75,'#00ff88','EXTREME LONG'), (25,'#ff3355','EXTREME SHORT')]:
        fig2.add_hline(y=y_val, line_color=color, line_width=0.8, line_dash='dot',
                       annotation_text=label, annotation_position="top left",
                       annotation_font=dict(color=color, size=9, family='Space Mono'))
    fig2.update_layout(
    **LAYOUT,
    height=260,
    yaxis=dict(range=[0, 100])
)
    st.plotly_chart(fig2, use_container_width=True)

# ─── Data Table ────────────────────────────────────────────────
if show_tbl:
    st.markdown('<div class="sec-label">HISTORICAL DATA</div>', unsafe_allow_html=True)
    disp = df[[DATE_COL,'Net_Lev','Net_Asset','Net_Dealer','IDX_Lev','IDX_Asset']].copy()
    disp.columns = ['Date','Lev. Money','Asset Mgr','Dealer','Index Lev.','Index Asset']
    disp['Date'] = disp['Date'].dt.strftime('%Y-%m-%d')
    st.dataframe(disp.sort_values('Date', ascending=False),
                 use_container_width=True, hide_index=True)

# ─── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    <span>MZ.COT · BUILT WITH PYTHON + STREAMLIT</span>
    <span>DATA SOURCE · CFTC.GOV</span>
    <span>UPDATED EVERY FRIDAY</span>
</div>
""", unsafe_allow_html=True)
