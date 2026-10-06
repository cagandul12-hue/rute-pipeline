# ======================================
# CONFIG + Library Imports
# ======================================
import streamlit as st
import pandas as pd
import numpy as np
import math
import folium
import re
import io
import requests
import datetime
import os
import json
import time
import base64
import unicodedata
from urllib.parse import unquote, quote
from xml.sax.saxutils import escape as xml_escape
from sklearn.cluster import KMeans
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Routing & Extractor System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================================
# STYLING
# ==========================================================================================
ACCENT_GRADIENT = "linear-gradient(135deg, #2563EB 0%, #0D9488 100%)"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, .main, p, div, span, h1, h2, h3, h4, h5, h6, label, button, textarea, input {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    .block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px;}

    /* ---------- Hero header ---------- */
    .hero-header {
        background:
            radial-gradient(circle at 15% -20%, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 55%),
            linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
        border-radius: 18px;
        padding: 26px 32px;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(37,99,235,0.28);
    }
    .hero-header h1 {
        color: #ffffff !important;
        margin: 0 !important;
        font-size: 1.7rem;
        font-weight: 800;
        line-height: 1.3;
    }
    .hero-header p {
        color: #ffffff !important;
        margin: 6px 0 0 0 !important;
        font-size: 0.95rem;
    }

    /* ---------- Metric cards ---------- */
    .metric-card {
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.18);
        border-top: 3px solid #2563EB;
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
    }
    .metric-card .metric-icon {font-size: 1.4rem; line-height: 1;}
    .metric-card .metric-label {
        font-size: 0.78rem; opacity: 0.82; margin-top: 8px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.03em;
    }
    .metric-card .metric-value {font-size: 1.5rem; font-weight: 800; margin-top: 2px;}

    /* ---------- Sidebar ---------- */
    .sidebar-brand {display: flex; align-items: center; gap: 10px;}
    .sidebar-brand .emoji {font-size: 1.9rem; line-height: 1;}
    .sidebar-brand .title {font-weight: 800; font-size: 1.08rem; line-height: 1.2;}
    .sidebar-brand .subtitle {font-size: 0.78rem; opacity: 0.82;}
    section[data-testid="stSidebar"] button {border-radius: 10px !important;}

    /* ---------- Buttons ---------- */
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    /* tombol sekunder (termasuk menu yang tidak aktif): batas & latar terlihat di tema terang maupun gelap */
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stDownloadButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]),
    .stLinkButton > a:not([data-testid="stBaseLinkButton-primary"]) {
        border: 1.5px solid rgba(128,128,128,0.8) !important;
        border: 1.5px solid color-mix(in srgb, currentColor 55%, transparent) !important;
        background: rgba(128,128,128,0.08) !important;
        background: color-mix(in srgb, currentColor 6%, transparent) !important;
    }
    .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover,
    .stDownloadButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover,
    .stLinkButton > a:not([data-testid="stBaseLinkButton-primary"]):hover {
        border-color: #2563EB !important;
        background: rgba(37,99,235,0.10) !important;
    }
    .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"],
    .stDownloadButton > button[kind="primary"], .stDownloadButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%) !important;
        border: none !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37,99,235,0.32);
    }
    .stButton > button[kind="primary"] *, .stButton > button[data-testid="stBaseButton-primary"] *,
    .stDownloadButton > button[kind="primary"] *, .stDownloadButton > button[data-testid="stBaseButton-primary"] * {
        color: #ffffff !important;
    }

    /* ---------- Expanders (route cards) ---------- */
    div[data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid rgba(128,128,128,0.18) !important;
        margin-bottom: 14px;
        overflow: hidden;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }

    /* ---------- Section headers ---------- */
    .section-header {
        display: flex; align-items: center; gap: 12px;
        margin: 30px 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid rgba(128,128,128,0.15);
    }
    .section-header .badge {
        width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
    }
    .section-header .title {font-weight: 800; font-size: 1.08rem; line-height: 1.3;}
    .section-header .subtitle {font-size: 0.82rem; opacity: 0.82; margin-top: 1px;}

    /* ---------- Empty state ---------- */
    .empty-state {
        border: 1.5px dashed rgba(37,99,235,0.35);
        border-radius: 16px;
        padding: 36px 24px;
        text-align: center;
        background: rgba(37,99,235,0.04);
        margin-top: 8px;
    }
    .empty-state .emoji {font-size: 2.3rem;}
    .empty-state .title {font-weight: 700; font-size: 1.05rem; margin-top: 12px;}
    .empty-state .desc {
        font-size: 0.86rem; opacity: 0.82; margin-top: 4px;
        max-width: 440px; margin-left: auto; margin-right: auto; line-height: 1.5;
    }

    div[data-testid="stSidebarNav"] {display: none;}

    /* ---------- Penanda langkah ---------- */
    .stepper {display: flex; align-items: center; gap: 8px; margin: 4px 0 18px 0;}
    .stepper .step {display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 0.9rem; opacity: 0.75;}
    .stepper .step .dot {
        width: 26px; height: 26px; border-radius: 50%; display: inline-flex; align-items: center;
        justify-content: center; font-size: 0.8rem; border: 2px solid rgba(128,128,128,0.5);
    }
    .stepper .step.active, .stepper .step.done {opacity: 1;}
    .stepper .step.active .dot {background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%); border-color: transparent; color: #fff; box-shadow: 0 0 0 4px rgba(37,99,235,0.22);}
    .stepper .step.done .dot {background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%); border-color: transparent; color: #fff;}
    .stepper .bar {flex: 1 1 16px; height: 2px; background: rgba(128,128,128,0.3); min-width: 12px;}

    /* ---------- Footer ---------- */
    .app-footer {
        margin-top: 56px; padding: 26px 0 8px 0; text-align: center;
        border-top: 1px solid rgba(128,128,128,0.18);
        position: relative;
    }
    .app-footer::before {
        content: ""; position: absolute; top: -2px; left: 50%; transform: translateX(-50%);
        width: 120px; height: 3px; border-radius: 3px;
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
    }
    .app-footer .f-brand {font-weight: 800; font-size: 1rem; letter-spacing: 0.01em;}
    .app-footer .f-bolt {display: inline-block; animation: boltPulse 2.4s ease-in-out infinite;}
    @keyframes boltPulse {
        0%, 100% {transform: scale(1); filter: drop-shadow(0 0 0 rgba(14,165,233,0));}
        50% {transform: scale(1.18); filter: drop-shadow(0 0 6px rgba(14,165,233,0.75));}
    }
    .app-footer .f-dev {font-size: 0.88rem; margin-top: 8px; opacity: 0.85;}
    .app-footer .f-name {
        font-weight: 800; color: inherit; padding-bottom: 2px;
        background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%) no-repeat 0 100% / 100% 3px;
    }
    .app-footer .f-heart {color: #ef4444; display: inline-block; animation: heartBeat 1.8s ease-in-out infinite;}
    @keyframes heartBeat {0%, 100% {transform: scale(1);} 50% {transform: scale(1.25);}}
    .app-footer .f-tech {
        display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 12px;
    }
    .app-footer .f-chip {
        font-size: 0.7rem; font-weight: 600; padding: 3px 10px; border-radius: 999px;
        background: rgba(128,128,128,0.10); border: 1px solid rgba(128,128,128,0.2);
        opacity: 0.85;
    }
    .app-footer .f-copy {font-size: 0.72rem; opacity: 0.75; margin-top: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(icon, label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(icon, title, subtitle=None):
    subtitle_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="badge">{icon}</div>
            <div>
                <div class="title">{title}</div>
                {subtitle_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon, title, desc):
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="emoji">{icon}</div>
            <div class="title">{title}</div>
            <div class="desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    year = datetime.date.today().year
    chips = ["Streamlit", "scikit-learn", "OR-Tools", "OSRM", "OpenStreetMap"]
    chips_html = "".join(f'<span class="f-chip">{c}</span>' for c in chips)
    st.markdown(
        f"""
        <div class="app-footer">
            <div class="f-brand"><span class="f-bolt">⚡</span> Routing &amp; Extractor</div>
            <div class="f-dev">Developed with <span class="f-heart">♥</span> by <span class="f-name">Abdillah</span></div>
            <div class="f-tech">{chips_html}</div>
            <div class="f-copy">© {year} Abdillah · All rights reserved</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


ROUTE_COLORS = [
    "#e6194B", "#3cb44b", "#4363d8", "#f58231", "#911eb4",   # 🔴 🟢 🔵 🟠 🟣
    "#ffe119", "#9A6324", "#2b2b2b", "#aab2bd",               # 🟡 🟤 ⚫ ⚪
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#800000", "#aaffc3", "#000075",
]
ROUTE_EMOJIS = ["🔴", "🟢", "🔵", "🟠", "🟣", "🟡", "🟤", "⚫", "⚪"]

# ==========================================================================================
# HELPER FUNCTIONS
# ==========================================================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def create_distance_matrix(df):
    """Straight-line (haversine) distance matrix in meters — used as the
    fallback when real road data (OSRM) isn't available."""
    n = len(df)
    lat = df["latitude"].to_numpy()
    lon = df["longitude"].to_numpy()
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = int(haversine(lat[i], lon[i], lat[j], lon[j]) * 1000)
    return matrix


OSRM_DEFAULT_URL = "https://router.project-osrm.org"
OSRM_DEFAULT_MAX_TABLE = 100  # batas jumlah titik per permintaan di server demo OSRM
FALLBACK_SPEED_KMH = 30  # used only if OSRM is unreachable


def _setting(name, default=None):
    """Baca pengaturan dari st.secrets, lalu environment variable, lalu default."""
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.environ.get(name) or default


def _osrm_url():
    # Untuk pemakaian serius, arahkan ke server OSRM sendiri lewat Secrets / env var OSRM_BASE_URL.
    return str(_setting("OSRM_BASE_URL", OSRM_DEFAULT_URL)).rstrip("/")


def _osrm_max_table():
    try:
        return max(4, int(_setting("OSRM_MAX_TABLE", OSRM_DEFAULT_MAX_TABLE)))
    except (TypeError, ValueError):
        return OSRM_DEFAULT_MAX_TABLE


def _osrm_request(coords, base_url, sources=None, destinations=None, retries=3):
    """Satu permintaan /table ke OSRM, dengan retry untuk gangguan sementara (429/5xx/timeout)."""
    path = ";".join(f"{lon},{lat}" for lon, lat in coords)
    params = {"annotations": "distance,duration"}
    if sources is not None:
        params["sources"] = ";".join(str(i) for i in sources)
    if destinations is not None:
        params["destinations"] = ";".join(str(i) for i in destinations)

    last_error = None
    for attempt in range(retries):
        try:
            resp = requests.get(f"{base_url}/table/v1/driving/{path}", params=params, timeout=20)
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"HTTP {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != "Ok":
                # Kesalahan permintaan (mis. TooBig) — tidak ada gunanya diulang.
                raise ValueError(data.get("message") or data.get("code") or "OSRM mengembalikan error")
            return data["distances"], data["durations"]
        except requests.RequestException as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
    raise last_error


@st.cache_data(ttl=3600, show_spinner=False, max_entries=64)
def _osrm_matrices_cached(coords, base_url, max_table):
    """Matriks jarak (m) & durasi (detik) dari OSRM, dipecah per blok kalau titiknya melebihi batas server.

    Kegagalan melempar exception, sehingga TIDAK ikut tersimpan di cache.
    """
    n = len(coords)
    dist = [[0] * n for _ in range(n)]
    dur = [[0] * n for _ in range(n)]

    def put(rows, cols, raw_d, raw_t):
        for a, i in enumerate(rows):
            for b, j in enumerate(cols):
                d, t = raw_d[a][b], raw_t[a][b]
                # null = pasangan titik yang tidak bisa dirutekan -> anggap "sangat jauh"
                dist[i][j] = int(d) if d is not None else 10_000_000
                dur[i][j] = t if t is not None else 0

    if n <= max_table:
        raw_d, raw_t = _osrm_request(coords, base_url)
        put(range(n), range(n), raw_d, raw_t)
        return dist, dur

    block = max(2, max_table // 2)
    starts = list(range(0, n, block))
    for i0 in starts:
        rows = list(range(i0, min(i0 + block, n)))
        for j0 in starts:
            cols = list(range(j0, min(j0 + block, n)))
            if i0 == j0:
                raw_d, raw_t = _osrm_request([coords[k] for k in rows], base_url)
            else:
                sub = [coords[k] for k in rows] + [coords[k] for k in cols]
                src = list(range(len(rows)))
                dst = list(range(len(rows), len(rows) + len(cols)))
                raw_d, raw_t = _osrm_request(sub, base_url, src, dst)
            put(rows, cols, raw_d, raw_t)
    return dist, dur


def get_route_matrices(df):
    """Returns (distance_matrix_meters, duration_matrix_seconds, used_real_roads, error_message).

    Memakai OSRM (jalan asli): hasilnya di-cache, titik yang banyak dipecah per blok
    agar tidak melewati batas server, dan gangguan sementara dicoba ulang.
    Kalau tetap gagal, jatuh ke estimasi garis lurus (haversine) dengan kecepatan
    rata-rata tetap, dan alasan kegagalannya ikut dikembalikan supaya bisa ditampilkan.
    """
    n = len(df)
    if n < 2:
        return [[0]], [[0]], True, None

    coords = tuple((round(float(r.longitude), 6), round(float(r.latitude), 6)) for r in df.itertuples())
    try:
        distance_matrix, duration_matrix = _osrm_matrices_cached(coords, _osrm_url(), _osrm_max_table())
        return distance_matrix, duration_matrix, True, None
    except Exception as e:
        distance_matrix = create_distance_matrix(df)
        duration_matrix = [
            [
                (distance_matrix[i][j] / 1000) / FALLBACK_SPEED_KMH * 3600 if i != j else 0
                for j in range(n)
            ]
            for i in range(n)
        ]
        return distance_matrix, duration_matrix, False, str(e)[:160]


def parse_coordinate_text(text):
    """Baca koordinat yang ditempel, mis. '-7.5665, 110.8167' atau '-7,5665; 110,8167'.

    Mengembalikan (lat, lon, pesan_error). pesan_error None kalau berhasil.
    """
    nums = re.findall(r"-?\d+(?:[.,]\d+)?", str(text or ""))
    if len(nums) != 2:
        return None, None, "Tidak terbaca. Tempel dua angka saja, contoh: -7.5665, 110.8167"
    lat, lon = (float(x.replace(",", ".")) for x in nums)
    if not (-90 <= lat <= 90) and (-90 <= lon <= 90) and (-180 <= lat <= 180):
        return None, None, "Latitude di luar rentang. Mungkin urutannya tertukar — format yang benar: latitude, longitude."
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None, None, "Koordinat di luar rentang valid (latitude -90 s/d 90, longitude -180 s/d 180)."
    return lat, lon, None


def make_sample_csv():
    """Data contoh: 12 merchant fiktif di dua area di sekitar Surakarta."""
    rng = np.random.default_rng(7)
    centers = [(-7.5560, 110.8000), (-7.5700, 110.8350)]
    rows = []
    for i in range(12):
        c = centers[i % 2]
        rows.append(
            {
                "merchant_name": f"Toko Contoh {i + 1:02d}",
                "latitude": round(c[0] + float(rng.normal(0, 0.006)), 6),
                "longitude": round(c[1] + float(rng.normal(0, 0.006)), 6),
            }
        )
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")


STEP_LABELS = ["Data", "Pengaturan", "Hasil"]


def render_stepper(slot, done):
    """Penanda langkah. done = jumlah langkah yang sudah selesai (0-3)."""
    items = []
    for i, label in enumerate(STEP_LABELS):
        state = "done" if i < done else ("active" if i == done else "todo")
        mark = "✓" if state == "done" else str(i + 1)
        items.append(f'<div class="step {state}"><span class="dot">{mark}</span><span class="lbl">{label}</span></div>')
    bar = '<div class="bar"></div>'
    slot.markdown('<div class="stepper">' + bar.join(items) + '</div>', unsafe_allow_html=True)


def format_duration(seconds):
    if seconds is None:
        return "–"
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes} menit"
    hours, rem = divmod(minutes, 60)
    return f"{hours} jam {rem} menit" if rem else f"{hours} jam"


def solve_tsp(distance_matrix, round_trip=False, fixed_start=False):
    """Urutan kunjungan optimal dengan OR-Tools.

    - round_trip=True : rute melingkar, kembali ke titik pertama (indeks 0).
    - round_trip=False, fixed_start=True : mulai di indeks 0 (titik awal), selesai di mana saja.
    - round_trip=False, fixed_start=False: mulai & selesai di mana saja (titik terbaik).

    Untuk rute satu arah dipakai node "dummy" berjarak 0 ke/dari semua titik, supaya
    solver tidak menghitung perjalanan pulang yang sebenarnya tidak dilakukan.
    Mengembalikan daftar indeks node asli (tanpa dummy, tanpa titik kembali).
    """
    n = len(distance_matrix)
    if n <= 2:
        return list(range(n))

    if round_trip:
        matrix = distance_matrix
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    else:
        # tambah node dummy (indeks n) dengan jarak 0 ke/dari semua node
        matrix = [list(row) + [0] for row in distance_matrix] + [[0] * (n + 1)]
        if fixed_start:
            manager = pywrapcp.RoutingIndexManager(n + 1, 1, [0], [n])
        else:
            manager = pywrapcp.RoutingIndexManager(n + 1, 1, n)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.time_limit.seconds = 5
    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        return list(range(n))

    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node < n:  # lewati node dummy
            route.append(node)
        index = solution.Value(routing.NextVar(index))
    return route


def route_leg_sum(matrix, order, round_trip=False):
    """Jumlah jarak/waktu sepanjang urutan; kalau round_trip, termasuk kaki pulang ke titik pertama."""
    path = list(order) + ([order[0]] if round_trip and len(order) > 1 else [])
    return sum(matrix[path[i]][path[i + 1]] for i in range(len(path) - 1))


# ---------- Merchant prioritas ----------
TRUTHY_STRINGS = {"ya", "yes", "y", "true", "1", "benar", "prioritas", "penting", "high"}


def is_truthy(val):
    """Dipakai untuk kolom opsional 'prioritas' — menerima berbagai cara orang
    menulis "ya" (termasuk angka 1, True, 'Yes', dst) di Excel/CSV."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val == 1
    return str(val).strip().lower() in TRUTHY_STRINGS


def _submatrix(matrix, indices):
    return [[matrix[i][j] for j in indices] for i in indices]


def solve_tsp_with_priority(distance_matrix, priority_idx, other_idx, has_start, round_trip):
    """Urutan kunjungan yang mengunjungi SEMUA titik `priority_idx` lebih dulu
    (diurutkan efisien di antara sesamanya), baru lanjut ke titik lainnya.

    Pendekatan dua-tahap (bukan pemrograman batasan penuh): tahap 1
    menyelesaikan TSP kecil untuk [titik awal]+prioritas, tahap 2 melanjutkan
    dari titik prioritas terakhir ke sisa titik. round_trip (kembali ke
    titik awal) hanya diterapkan di tahap akhir. Mengembalikan daftar indeks
    asli, format sama seperti hasil solve_tsp() biasa — jadi kompatibel
    langsung dengan finalize_route().
    """
    n = len(distance_matrix)
    if not priority_idx or n <= 2:
        return solve_tsp(distance_matrix, round_trip=round_trip, fixed_start=has_start)

    start_part = [0] if has_start else []
    phase1_idx = start_part + list(priority_idx)
    if len(phase1_idx) <= 1:
        phase1_order = phase1_idx
    else:
        sub_order = solve_tsp(_submatrix(distance_matrix, phase1_idx), round_trip=False, fixed_start=has_start)
        phase1_order = [phase1_idx[i] for i in sub_order]

    if not other_idx:
        return phase1_order

    last_priority = phase1_order[-1] if phase1_order else 0
    phase2_idx = [last_priority] + list(other_idx)
    sub_order2 = solve_tsp(_submatrix(distance_matrix, phase2_idx), round_trip=round_trip, fixed_start=True)
    phase2_order = [phase2_idx[i] for i in sub_order2]

    return (phase1_order[:-1] + phase2_order) if phase1_order else phase2_order


# ---------- Multi-depot ----------
def parse_depot_list(text):
    """Parse beberapa titik awal, satu per baris: 'Nama|link_atau_koordinat'.
    Nama boleh dikosongkan (pakai '|link' saja, atau link/koordinat polos).
    Mengembalikan (list_depot_dict, list_pesan_error)."""
    depots, errors = [], []
    for lineno, raw_line in enumerate(str(text or "").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if "|" in line:
            name_part, loc_part = line.split("|", 1)
        else:
            name_part, loc_part = "", line
        loc_part, name = loc_part.strip(), name_part.strip()
        lat = lon = None
        if "http" not in loc_part.lower():
            lat, lon, _err = parse_coordinate_text(loc_part)
        if lat is None:
            parsed_name, lat, lon = extract_google_maps_data(loc_part)
            if not name:
                name = parsed_name or f"Titik Awal {lineno}"
        if not name:
            name = f"Titik Awal {lineno}"
        if lat is None or lon is None:
            errors.append(f"Baris {lineno}: tidak bisa dibaca sebagai link/koordinat — dilewati.")
            continue
        depots.append({"name": name, "lat": lat, "lon": lon})
    return depots, errors


def nearest_depot(depots, lat, lon):
    best, best_dist = None, float("inf")
    for d in depots:
        dist = haversine(lat, lon, d["lat"], d["lon"])
        if dist < best_dist:
            best, best_dist = d, dist
    return best


# ---------- Jam operasional (time windows) ----------
def _parse_hhmm(val):
    """Baca 'HH:MM' (atau datetime.time/Timestamp) jadi datetime.time; None kalau gagal/kosong."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, datetime.time):
        return val
    if isinstance(val, datetime.datetime):
        return val.time()
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None
    m = re.match(r"^(\d{1,2})[:.](\d{2})", s)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if 0 <= h <= 23 and 0 <= mi <= 59:
        return datetime.time(h, mi)
    return None


def check_time_window(arrival_dt, jam_buka, jam_tutup):
    """Bandingkan jam tiba dengan jam operasional. Mengembalikan status pendek
    ("" kalau tidak ada jam operasional / tepat waktu) untuk ditampilkan di
    tabel, PDF, dan WhatsApp."""
    open_t, close_t = _parse_hhmm(jam_buka), _parse_hhmm(jam_tutup)
    if open_t is None and close_t is None:
        return ""
    t = arrival_dt.time()
    if open_t and t < open_t:
        return f"⚠️ tiba sebelum buka ({open_t.strftime('%H:%M')})"
    if close_t and t > close_t:
        return f"⚠️ tiba setelah tutup ({close_t.strftime('%H:%M')})"
    return "✅"


# Batas titik singgah (waypoints) di link Google Maps menurut dokumentasi resmi:
# maks. 9 di desktop/aplikasi, tapi hanya 3 di browser HP. Kalau lebih, titik
# singgah berlebih DIBUANG diam-diam oleh Google Maps — makanya rute dipecah.
MAPS_MAX_WAYPOINTS_DESKTOP = 9
MAPS_MAX_WAYPOINTS_MOBILE = 3


def generate_google_maps_links(df, max_waypoints):
    """Pecah rute jadi beberapa link Google Maps.

    Tiap link berisi origin + maksimal `max_waypoints` titik singgah + destination.
    Link berikutnya dimulai dari titik akhir link sebelumnya, sehingga urutan tetap
    tersambung. Mengembalikan list (indeks_awal, indeks_akhir, url) — indeks 0-based
    pada baris df.
    """
    coords = [f"{row.latitude},{row.longitude}" for _, row in df.iterrows()]
    if len(coords) < 2:
        return []
    step = max_waypoints + 1
    links = []
    start = 0
    while start < len(coords) - 1:
        end = min(start + step, len(coords) - 1)
        seg = coords[start:end + 1]
        url = (
            f"https://www.google.com/maps/dir/?api=1&origin={seg[0]}&destination={seg[-1]}"
        )
        if len(seg) > 2:
            url += "&waypoints=" + "%7C".join(seg[1:-1])
        url += "&travelmode=driving"
        links.append((start, end, url))
        start = end
    return links


SHORT_LINK_DOMAINS = ("maps.app.goo.gl", "goo.gl/maps", "app.goo.gl")


def search_nominatim(query, limit=8):
    """Free OpenStreetMap place search — no API key needed. Coverage of
    small/local merchants in Indonesia is thinner than Google, so this is
    best used with a specific name plus a city/area hint.

    Returns (results, error_message). error_message is None on a normal
    request (even if it legitimately found zero places) and is set only
    when the request itself failed — e.g. the public Nominatim server
    rate-limited us (it's free but usage-capped) or the network timed out
    — so the UI can tell "genuinely no match" apart from "couldn't even
    ask", which previously both looked like a plain empty result.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "namedetails": 1,  # gives the place's own OSM "name" tag — needed to
                           # tell apart results that share a generic search
                           # term (e.g. several "SPBU" with different codes)
        "limit": limit,
        "countrycodes": "id",
    }
    # Nominatim's usage policy requires a real identifying User-Agent.
    headers = {"User-Agent": "RutePipelineOptimizerApp/1.0 (streamlit-community-app)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        if resp.status_code == 429:
            return [], "Layanan pencarian sedang dibatasi (terlalu banyak permintaan). Coba lagi dalam beberapa detik."
        if resp.status_code == 403:
            return [], "Layanan pencarian menolak permintaan ini (kemungkinan dibatasi sementara). Coba lagi nanti."
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.Timeout:
        return [], "Layanan pencarian tidak merespons (timeout). Coba lagi."
    except requests.exceptions.RequestException:
        return [], "Gagal menghubungi layanan pencarian — periksa koneksi internet, lalu coba lagi."
    except Exception:
        return [], "Terjadi kesalahan tak terduga saat mencari. Coba lagi."


def nominatim_result_name(result, fallback_query=""):
    """Picks the most specific name available for a Nominatim result, so
    that results sharing a generic search term (e.g. several "SPBU") stay
    distinguishable instead of all being saved under the same name.

    Priority: the place's own OSM name tag > the first segment of its full
    address string (usually the specific place name) > the search term the
    user typed > a generic placeholder.
    """
    namedetails = result.get("namedetails") or {}
    specific_name = namedetails.get("name") or namedetails.get("name:id")
    if specific_name:
        return specific_name.strip()

    display_name = result.get("display_name", "")
    if display_name:
        first_segment = display_name.split(",")[0].strip()
        if first_segment:
            return first_segment

    return fallback_query.strip() or "Lokasi"


def resolve_short_link(link):
    """maps.app.goo.gl / goo.gl links don't contain coordinates in the text
    itself — the real URL only appears after following the redirect."""
    if not any(domain in link for domain in SHORT_LINK_DOMAINS):
        return link
    try:
        resp = requests.head(link, allow_redirects=True, timeout=6)
        if resp.url and resp.url != link:
            return resp.url
    except Exception:
        pass
    try:
        resp = requests.get(link, allow_redirects=True, timeout=6)
        return resp.url or link
    except Exception:
        return link


def extract_google_maps_data(link):
    """Returns (place_name_or_None, latitude_or_None, longitude_or_None)."""
    try:
        link = resolve_short_link(link.strip())

        # --- Coordinates -----------------------------------------------
        # A "data=" segment can hold MULTIPLE "!8m2!3d<lat>!4d<lon>" pairs:
        # when Google can't pin an unofficial/small place precisely, it
        # first embeds a nearby *landmark's* own block — recognizable by an
        # explicit "!2s<Landmark Name>" right before its "!8m2" — purely to
        # anchor the search, then appends the actual target's block last
        # (with no "!2sName", since the target's name is already in the
        # URL path). Taking the FIRST match (or the "@lat,lng" viewport,
        # which mirrors that same landmark) grabs the wrong location, so we
        # take the LAST pair instead — that's always the real target.
        all_pin_pairs = re.findall(r"!8m2!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", link)
        # Priority 2: a bare "q=lat,lng" or "query=lat,lng" parameter.
        query_coord_match = re.search(r"[?&](?:q|query)=(-?\d+\.\d+),(-?\d+\.\d+)", link)
        # Priority 3: any generic "!3d...!4d..." pair (same last-wins logic).
        all_generic_pairs = re.findall(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", link)
        # Priority 4 (least reliable): the "@lat,lng,zoom" viewport center —
        # as shown above this can actually be a disambiguation landmark's
        # coordinates rather than the place itself, so it's only used when
        # nothing else in the link gives us a coordinate at all.
        view_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", link)

        latitude = longitude = None
        if all_pin_pairs:
            latitude, longitude = float(all_pin_pairs[-1][0]), float(all_pin_pairs[-1][1])
        elif query_coord_match:
            latitude, longitude = float(query_coord_match.group(1)), float(query_coord_match.group(2))
        elif all_generic_pairs:
            latitude, longitude = float(all_generic_pairs[-1][0]), float(all_generic_pairs[-1][1])
        elif view_match:
            latitude, longitude = float(view_match.group(1)), float(view_match.group(2))

        # --- Place name --------------------------------------------------
        place_name = None
        place_match = re.search(r"/place/([^/@]+)", link)
        if place_match:
            place_name = unquote(place_match.group(1)).replace("+", " ").strip()
        else:
            query_name_match = re.search(r"[?&]query=([^&]+)", link)
            if query_name_match:
                candidate = unquote(query_name_match.group(1)).replace("+", " ").strip()
                # Skip it if it's actually just coordinates, not a name.
                if not re.fullmatch(r"-?\d+\.\d+,-?\d+\.\d+", candidate):
                    place_name = candidate

        return place_name, latitude, longitude
    except Exception:
        return None, None, None


def balance_clusters(df, max_points_per_route):
    df = df.copy()
    for _guard in range(1000):  # pengaman supaya tidak pernah macet
        cluster_sizes = df["route"].value_counts().to_dict()
        oversized_clusters = [c for c, size in cluster_sizes.items() if size > max_points_per_route]
        if not oversized_clusters:
            break

        for big_cluster in oversized_clusters:
            excess_points = cluster_sizes[big_cluster] - max_points_per_route
            big_cluster_df = df[df["route"] == big_cluster]
            candidate_clusters = [c for c, size in cluster_sizes.items() if size < max_points_per_route]
            if not candidate_clusters:
                break

            for _ in range(excess_points):
                candidate_clusters = [c for c, size in cluster_sizes.items() if size < max_points_per_route]
                if not candidate_clusters:
                    break
                best_point_index, best_target_cluster = None, None
                best_distance = float("inf")
                for idx, row in big_cluster_df.iterrows():
                    for target_cluster in candidate_clusters:
                        target_df = df[df["route"] == target_cluster]
                        target_centroid_lat = target_df["latitude"].mean()
                        target_centroid_lon = target_df["longitude"].mean()
                        dist = haversine(row["latitude"], row["longitude"], target_centroid_lat, target_centroid_lon)
                        if dist < best_distance:
                            best_distance = dist
                            best_point_index = idx
                            best_target_cluster = target_cluster
                if best_point_index is not None:
                    df.loc[best_point_index, "route"] = best_target_cluster
                    cluster_sizes[big_cluster] -= 1
                    cluster_sizes[best_target_cluster] += 1
                    big_cluster_df = df[df["route"] == big_cluster]
    return df


def fill_clusters(df, max_points_per_route):
    """Bagi titik jadi rute yang diisi PENUH sesuai maksimal (mis. 16 titik, maks 10 -> 10 + 6).

    Tiap rute dibangun dengan cara: ambil titik terluar dari sisa titik sebagai
    awal, lalu tambahkan terus titik terdekat dari pusat kelompok sampai penuh.
    Rute-rute awal biasanya rapat; rute terakhir berisi sisa (bisa lebih tersebar).
    Mengembalikan array label rute (0, 1, 2, ...) berurutan sesuai indeks df.
    """
    coords = df[["latitude", "longitude"]].to_numpy(dtype=float)
    n = len(coords)
    labels = np.full(n, -1, dtype=int)
    remaining = list(range(n))
    route_id = 0
    while remaining:
        pts = coords[remaining]
        center = pts.mean(axis=0)
        seed_pos = int(np.argmax(((pts - center) ** 2).sum(axis=1)))
        group = [remaining.pop(seed_pos)]
        while len(group) < max_points_per_route and remaining:
            gc = coords[group].mean(axis=0)
            rem_pts = coords[remaining]
            nearest = int(np.argmin(((rem_pts - gc) ** 2).sum(axis=1)))
            group.append(remaining.pop(nearest))
        labels[group] = route_id
        route_id += 1
    return labels


def _max_points_control(df):
    """Slider 'maksimal titik per rute' (dipakai di mode Desktop & Mobile)."""
    slider_max = max(2, len(df))
    if slider_max <= 2:
        # st.slider needs min_value < max_value; with only 2
        # merchants there's only one sensible route anyway.
        metric_card("📍", "Maksimal titik per rute", slider_max)
        return slider_max
    return st.slider(
        "Maksimal titik per rute", min_value=2, max_value=slider_max,
        value=slider_max,
        help="Default = total merchant, sehingga semua muat dalam 1 rute. Geser ke bawah untuk memecah jadi beberapa rute.",
    )


def _plan_control(df, plan_mode):
    """Kontrol penentu jumlah rute. Mengembalikan (maks_titik_per_rute, jumlah_rute_atau_None)."""
    n = len(df)
    if plan_mode == PLAN_COUNT:
        k_max = max(1, n)
        k_val = min(max(1, int(st.session_state.target_routes_flag)), k_max)
        k = st.number_input(
            "Jumlah rute",
            min_value=1, max_value=k_max, value=k_val, step=1,
            key="_target_widget", on_change=_sync_target,
            help="Misalnya 5 sales = 5 rute. Merchant dibagi merata menurut area lokasi.",
        )
        return math.ceil(n / int(k)), int(k)
    return _max_points_control(df), None


def validate_dataframe(df):
    """Returns (is_valid, list_of_error_messages)."""
    errors = []
    required_cols = ["merchant_name", "latitude", "longitude"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        errors.append(f"Kolom wajib hilang: {', '.join(missing)}")
        return False, errors

    if df.empty:
        errors.append("File tidak berisi data.")
        return False, errors

    numeric_lat = pd.to_numeric(df["latitude"], errors="coerce")
    numeric_lon = pd.to_numeric(df["longitude"], errors="coerce")
    bad_rows = df[numeric_lat.isna() | numeric_lon.isna()]
    if not bad_rows.empty:
        errors.append(
            f"{len(bad_rows)} baris memiliki latitude/longitude yang tidak valid (bukan angka)."
        )

    out_of_range = df[
        (numeric_lat < -90) | (numeric_lat > 90) | (numeric_lon < -180) | (numeric_lon > 180)
    ]
    if not out_of_range.empty:
        errors.append(f"{len(out_of_range)} baris memiliki koordinat di luar rentang valid.")

    empty_names = df[df["merchant_name"].isna() | (df["merchant_name"].astype(str).str.strip() == "")]
    if not empty_names.empty:
        errors.append(f"{len(empty_names)} baris tidak memiliki merchant_name.")

    return len(errors) == 0, errors


REQUIRED_COLS = ("merchant_name", "latitude", "longitude")
# Kolom opsional: kalau ada, dipakai otomatis untuk fitur prioritas & jam operasional.
OPTIONAL_COLS = ("prioritas", "jam_buka", "jam_tutup")
NORMALIZE_COLS = REQUIRED_COLS + OPTIONAL_COLS


def read_table_file(name, data):
    """Baca file .xlsx atau .csv menjadi DataFrame.

    CSV: pemisah (koma / titik koma / tab) dideteksi otomatis, BOM UTF-8 ditangani.
    Nama kolom wajib dinormalkan (huruf kecil, tanpa spasi tepi) dan koma desimal pada
    latitude/longitude (format Indonesia, mis. -7,5665) diubah jadi titik.
    """
    if name.lower().endswith(".csv"):
        df, last_error = None, None
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=enc)
                break
            except Exception as e:
                last_error = e
        if df is None:
            raise last_error
    else:
        df = pd.read_excel(io.BytesIO(data))

    rename = {
        c: str(c).strip().lower()
        for c in df.columns
        if str(c).strip().lower() in NORMALIZE_COLS and c != str(c).strip().lower()
    }
    if rename:
        df = df.rename(columns=rename)

    for col in ("latitude", "longitude"):
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):  # pandas 3: teks bertipe "str", bukan object
            mask = df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].astype(str).str.strip().str.replace(",", ".", regex=False)
    return df


def _clock(dt, base_date):
    """Format jam 'HH:MM'; kalau lewat tengah malam tambahkan '(+N hari)'."""
    days = (dt.date() - base_date).days
    text = dt.strftime("%H:%M")
    return text + (f" (+{days} hari)" if days > 0 else "")


def build_schedule(duration_matrix, order, start_dt, visit_sec, first_is_start, round_trip):
    """Jam tiba/selesai tiap titik sepanjang urutan kunjungan.

    Titik awal (kalau ada) tidak dihitung durasi kunjungan. Mengembalikan
    (jam_tiba, jam_selesai, jam_kembali_atau_None, jam_selesai_rute) sebagai datetime.
    """
    arrivals, departs = [], []
    t = start_dt
    for k, node in enumerate(order):
        if k > 0:
            t = departs[-1] + datetime.timedelta(seconds=duration_matrix[order[k - 1]][node])
        arrivals.append(t)
        stay = 0 if (k == 0 and first_is_start) else visit_sec
        departs.append(t + datetime.timedelta(seconds=stay))
    back = None
    if round_trip and len(order) > 1:
        back = departs[-1] + datetime.timedelta(seconds=duration_matrix[order[-1]][order[0]])
    return arrivals, departs, back, (back or departs[-1])


def build_whatsapp_text(r, map_links):
    """Teks siap kirim (format WhatsApp) untuk satu rute."""
    df = r["df"]
    total_sec = r["duration_sec"] + r.get("visit_sec", 0)
    lines = [
        f"*Rute {r['route_id'] + 1}* — {len(df)} titik · ~{r['distance_km']:.1f} km · ~{format_duration(total_sec)}"
    ]
    if r.get("driver"):
        lines.append(f"🧑‍✈️ Kurir: {r['driver']}")
    if r.get("depot_name"):
        lines.append(f"🏭 Titik awal: {r['depot_name']}")
    if r.get("finish_label"):
        lines.append(f"🏁 Estimasi selesai ±{r['finish_label']}")
    lines.append("")
    for _, row in df.iterrows():
        eta = f" ({row['jam_tiba']})" if "jam_tiba" in df.columns else ""
        star = "⭐ " if row.get("prioritas_flag") else ""
        warn = f" {row['jadwal_status']}" if row.get("jadwal_status", "").startswith("⚠️") else ""
        lines.append(f"{int(row['sequence'])}. {star}{row['merchant_name']}{eta}{warn}")
    if r.get("round_trip"):
        lines.append("↩️ Lalu kembali ke titik awal")
    lines.append("")
    if len(map_links) == 1:
        lines.append(f"🗺️ Google Maps: {map_links[0][2]}")
    else:
        for i, (_, _, url) in enumerate(map_links, start=1):
            lines.append(f"🗺️ Google Maps bagian {i}: {url}")
    return "\n".join(lines)


# ==========================================================================================
# HASIL RUTE: finalisasi, ubah urutan manual, peta gabungan, lembar PDF
# ==========================================================================================
def finalize_route(route_df, order, distance_matrix, duration_matrix, route_id,
                   start_dt, visit_sec, has_start, round_trip, base_date):
    """Bangun tabel rute + jadwal + total jarak/waktu dari sebuah URUTAN.

    Dipakai saat rute pertama kali dibuat (urutan dari TSP) dan saat pengguna
    mengubah urutan secara manual — matriks jarak/waktu dipakai ulang, jadi
    tidak perlu memanggil OSRM lagi.
    """
    optimized_df = route_df.iloc[order].reset_index(drop=True)
    optimized_df["sequence"] = optimized_df.index + 1
    optimized_df["route_name"] = f"Rute {route_id + 1}"
    arrivals, departs, back_dt, finish_dt = build_schedule(
        duration_matrix, order, start_dt, visit_sec, has_start, round_trip
    )
    optimized_df["jam_tiba"] = [_clock(t, base_date) for t in arrivals]
    if visit_sec:
        optimized_df["jam_selesai"] = [_clock(t, base_date) for t in departs]

    if "prioritas" in optimized_df.columns:
        optimized_df["prioritas_flag"] = optimized_df["prioritas"].apply(is_truthy)

    n_late = 0
    if "jam_buka" in optimized_df.columns or "jam_tutup" in optimized_df.columns:
        statuses = []
        for k, dt in enumerate(arrivals):
            is_start_row = k == 0 and has_start
            jb = optimized_df["jam_buka"].iloc[k] if "jam_buka" in optimized_df.columns else None
            jt = optimized_df["jam_tutup"].iloc[k] if "jam_tutup" in optimized_df.columns else None
            status = "" if is_start_row else check_time_window(dt, jb, jt)
            if status.startswith("⚠️"):
                n_late += 1
            statuses.append(status)
        optimized_df["jadwal_status"] = statuses

    n_visits = len(order) - (1 if has_start else 0)
    return {
        "df": optimized_df,
        "distance_km": route_leg_sum(distance_matrix, order, round_trip) / 1000,
        "duration_sec": route_leg_sum(duration_matrix, order, round_trip),
        "visit_sec": visit_sec * n_visits,
        "finish_label": _clock(finish_dt, base_date),
        "back_label": _clock(back_dt, base_date) if back_dt else None,
        "n_outside_hours": n_late,
    }


def build_excel_bytes(route_summaries):
    """Driver/depot ditambahkan sebagai kolom di sini (saat export), bukan
    disimpan permanen di r['df'] — supaya nilainya selalu yang terbaru
    walau diubah user setelah rute pertama kali dibuat."""
    parts = []
    for r in route_summaries:
        d = r["df"].copy()
        if r.get("driver"):
            d["kurir"] = r["driver"]
        if r.get("depot_name"):
            d["titik_awal"] = r["depot_name"]
        parts.append(d)
    final_df = pd.concat(parts, ignore_index=True)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        final_df.to_excel(writer, index=False, sheet_name="Semua Rute")
        for r, d in zip(route_summaries, parts):
            sheet_name = f"Rute {r['route_id'] + 1}"[:31]
            d.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()


def route_links_info(r, max_waypoints):
    """Link Google Maps + nomor urut titik untuk sebuah rute (termasuk kaki pulang bila pulang-pergi)."""
    df = r["df"]
    is_round = bool(r.get("round_trip"))
    link_df = pd.concat([df, df.iloc[[0]]], ignore_index=True) if is_round else df
    seq_nums = list(df["sequence"]) + ([df["sequence"].iloc[0]] if is_round else [])
    return generate_google_maps_links(link_df, max_waypoints), seq_nums, link_df


def _move_stop(route_id, action):
    """Callback tombol ubah-urutan: up / down / top / bottom / reset."""
    res = st.session_state.get("route_result")
    if not res:
        return
    r = next((x for x in res["route_summaries"] if x["route_id"] == route_id), None)
    if r is None:
        return
    order = list(r["order"])
    min_pos = 1 if r["has_start"] else 0  # titik awal (kalau ada) terkunci di urutan pertama
    if action == "reset":
        new_order = list(r["optimal_order"])
    else:
        node = st.session_state.get(f"mv_sel_{route_id}")
        if node not in order:
            return
        p = order.index(node)
        if p < min_pos:
            return
        if action == "up" and p > min_pos:
            order[p - 1], order[p] = order[p], order[p - 1]
        elif action == "down" and p < len(order) - 1:
            order[p + 1], order[p] = order[p], order[p + 1]
        elif action == "top":
            order.insert(min_pos, order.pop(p))
        elif action == "bottom":
            order.append(order.pop(p))
        new_order = order
    r.update(
        finalize_route(
            r["route_df"], new_order, r["distance_matrix"], r["duration_matrix"], route_id,
            r["start_dt"], r["visit_sec_each"], r["has_start"], r["round_trip"], r["base_date"],
        )
    )
    r["order"] = new_order
    r["manual"] = new_order != r["optimal_order"]
    res["excel_bytes"] = build_excel_bytes(res["route_summaries"])


def render_reorder_controls(r):
    """Pilih satu merchant lalu geser naik/turun — sederhana dan nyaman di HP."""
    rid = r["route_id"]
    order, route_df = r["order"], r["route_df"]
    min_pos = 1 if r["has_start"] else 0
    movable = order[min_pos:]
    if len(movable) < 2:
        st.caption("Rute ini hanya punya satu merchant, tidak ada yang perlu diurutkan ulang.")
        return
    key = f"mv_sel_{rid}"
    if st.session_state.get(key) not in movable:
        st.session_state.pop(key, None)
    st.selectbox(
        "Pilih merchant yang mau dipindah",
        movable,
        format_func=lambda n, _o=order, _d=route_df: f"{_o.index(n) + 1}. {_d.loc[n, 'merchant_name']}",
        key=key,
    )
    with st.container(key=f"mvrow_a_{rid}"):
        b1, b2 = st.columns(2)
        with b1:
            st.button("⬆️ Naik", key=f"mv_up_{rid}", on_click=_move_stop, args=(rid, "up"), width='stretch')
        with b2:
            st.button("⬇️ Turun", key=f"mv_down_{rid}", on_click=_move_stop, args=(rid, "down"), width='stretch')
    with st.container(key=f"mvrow_b_{rid}"):
        b3, b4 = st.columns(2)
        with b3:
            st.button("⏫ Ke awal", key=f"mv_top_{rid}", on_click=_move_stop, args=(rid, "top"), width='stretch')
        with b4:
            st.button("⏬ Ke akhir", key=f"mv_bottom_{rid}", on_click=_move_stop, args=(rid, "bottom"), width='stretch')
    st.button(
        "↩️ Kembalikan ke urutan optimal", key=f"mv_reset_{rid}", on_click=_move_stop,
        args=(rid, "reset"), disabled=not r.get("manual"), width='stretch',
    )
    if r.get("manual"):
        dk = r["distance_km"] - r["optimal_distance_km"]
        dm = (r["duration_sec"] - r["optimal_duration_sec"]) / 60
        st.caption(f"✏️ Urutan diubah manual: {dk:+.1f} km · {dm:+.0f} menit dibanding urutan optimal.")
    if r["has_start"]:
        st.caption("Titik awal selalu di urutan pertama dan tidak bisa dipindah.")


def _text_color_for(hex_color):
    """Hitam/putih mana yang lebih terbaca di atas warna latar ini."""
    h = hex_color.lstrip("#")
    rr, gg, bb = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in (rr, gg, bb)]
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return "#1f2937" if lum > 0.40 else "#ffffff"


def numbered_icon(label, color, is_start=False):
    """Penanda bulat bernomor berwarna sesuai rute (S = titik awal)."""
    bg = "#111827" if is_start else color
    fg = "#ffffff" if is_start else _text_color_for(color)
    size = 28 if len(str(label)) >= 3 else 24
    html = (
        f'<div style="background:{bg};color:{fg};border:2px solid #fff;border-radius:50%;'
        f'width:{size}px;height:{size}px;line-height:{size - 4}px;text-align:center;'
        f'font:700 12px/{size - 4}px sans-serif;box-shadow:0 1px 5px rgba(0,0,0,.45);">{label}</div>'
    )
    return folium.DivIcon(html=html, icon_size=(size, size), icon_anchor=(size // 2, size // 2))


def build_combined_map(route_summaries):
    """Satu peta untuk semua rute: warna berbeda per rute, bisa dinyalakan/dimatikan."""
    lats = [v for r in route_summaries for v in r["df"]["latitude"]]
    lons = [v for r in route_summaries for v in r["df"]["longitude"]]
    fmap = folium.Map(
        location=[sum(lats) / len(lats), sum(lons) / len(lons)], zoom_start=11, control_scale=True
    )
    start_drawn = False
    for r in route_summaries:
        rid = r["route_id"]
        df = r["df"]
        color = ROUTE_COLORS[rid % len(ROUTE_COLORS)]
        dot = (
            f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
            f'background:{color};margin-right:6px;vertical-align:middle;"></span>'
        )
        n_stops = len(df) - (1 if r.get("has_start") else 0)
        group = folium.FeatureGroup(
            name=f"{dot}Rute {rid + 1} · {n_stops} titik · {r['distance_km']:.1f} km", show=True
        )
        coords = [[row["latitude"], row["longitude"]] for _, row in df.iterrows()]
        line = coords + ([coords[0]] if r.get("round_trip") else [])
        folium.PolyLine(line, weight=4, color=color, opacity=0.85).add_to(group)
        for idx, row in df.iterrows():
            is_start = bool(r.get("has_start")) and idx == 0
            if is_start:
                if start_drawn:
                    continue  # titik awal sama untuk semua rute: gambar sekali saja
                start_drawn = True
            eta = row["jam_tiba"] if "jam_tiba" in df.columns else ""
            tip = ("Titik awal" if is_start else f"Rute {rid + 1} · {int(row['sequence'])}") + f" · {row['merchant_name']}"
            folium.Marker(
                [row["latitude"], row["longitude"]],
                icon=numbered_icon("S" if is_start else int(row["sequence"]), color, is_start),
                tooltip=tip,
                popup=folium.Popup(f"{tip}" + (f"<br>Tiba ±{eta}" if eta else ""), max_width=260),
            ).add_to(group)
        group.add_to(fmap)
    folium.LayerControl(collapsed=False).add_to(fmap)
    fmap.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=(30, 30))
    return fmap


# --- PDF-START ---
try:
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, KeepTogether, Flowable,
    )
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics.shapes import Drawing

    PDF_OK = True
except Exception:  # reportlab belum terpasang -> fitur PDF disembunyikan, aplikasi tetap jalan
    PDF_OK = False

PDF_BRAND = "#2563EB"
_ID_MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
              "Agustus", "September", "Oktober", "November", "Desember"]


def _pdf_safe(text):
    """Font bawaan PDF hanya mengenal Latin-1: samakan tanda baca umum, buang karakter yang tak didukung."""
    t = str(text if text is not None else "")
    for a, b in (("\u2013", "-"), ("\u2014", "-"), ("\u2018", "'"), ("\u2019", "'"),
                 ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " "), ("\u2022", "-")):
        t = t.replace(a, b)
    out = []
    for ch in t:
        try:
            ch.encode("latin-1")
            out.append(ch)
        except UnicodeEncodeError:
            plain = "".join(c for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c))
            try:
                plain.encode("latin-1")
                out.append(plain)
            except UnicodeEncodeError:
                pass  # emoji dsb. dibuang
    return "".join(out).strip()


def _fmt_date_id(iso):
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.day} {_ID_MONTHS[d.month - 1]} {d.year}"
    except Exception:
        return ""


def _pdf_payload(r, links, seq_nums, result):
    """Ringkas satu rute jadi data polos (mudah di-cache) untuk dibuat PDF-nya."""
    df = r["df"]
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "seq": int(row["sequence"]), "name": str(row["merchant_name"]),
            "lat": float(row["latitude"]), "lon": float(row["longitude"]),
            "tiba": str(row["jam_tiba"]) if "jam_tiba" in df.columns else "",
            "selesai": str(row["jam_selesai"]) if "jam_selesai" in df.columns else "",
            "priority": bool(row.get("prioritas_flag", False)),
            "note": str(row["jadwal_status"]) if row.get("jadwal_status") else "",
        })
    return {
        "route_no": int(r["route_id"]) + 1, "rows": rows,
        "has_start": bool(r.get("has_start")), "round_trip": bool(r.get("round_trip")),
        "back_label": r.get("back_label") or "", "manual": bool(r.get("manual")),
        "distance_km": float(r["distance_km"]), "duration_sec": float(r["duration_sec"]),
        "visit_sec": float(r.get("visit_sec", 0)), "finish_label": r.get("finish_label") or "",
        "show_selesai": "jam_selesai" in df.columns,
        "links": [(int(a), int(b), u) for a, b, u in links],
        "seq_nums": [int(x) for x in seq_nums],
        "date": result.get("base_date", ""), "start_label": result.get("start_label", ""),
        "driver": r.get("driver") or "", "depot_name": r.get("depot_name") or "",
    }


if PDF_OK:
    class _SetRoute(Flowable):
        """Penanda tak terlihat: memberi tahu footer halaman ini milik rute yang mana."""
        def __init__(self, label):
            super().__init__()
            self.label = label
            self.width = self.height = 0

        def draw(self):
            self.canv._route_label = self.label

    class _CheckBox(Flowable):
        """Kotak kosong untuk dicentang kurir dengan pena."""
        def __init__(self, size=5.0 * mm):
            super().__init__()
            self.size = size
            self.width = self.height = size

        def draw(self):
            self.canv.setStrokeColor(rl_colors.HexColor("#6B7280"))
            self.canv.setLineWidth(1)
            self.canv.roundRect(0, 0, self.size, self.size, 1.2 * mm, stroke=1, fill=0)


def _qr_shorten(url):
    """Perpendek URL untuk QR supaya kodenya tidak terlalu padat (lebih mudah dipindai):
    koordinat dibulatkan ke 5 desimal (~1 m) dan travelmode dibuang (Maps default-nya mobil)."""
    url = url.replace("&travelmode=driving", "")
    return re.sub(r"-?\d+\.\d{6,}", lambda m: f"{float(m.group(0)):.5f}", url)


def _qr_drawing(url, size):
    widget = QrCodeWidget(_qr_shorten(url), barLevel="L")
    x0, y0, x1, y1 = widget.getBounds()
    w, h = x1 - x0, y1 - y0
    d = Drawing(size, size, transform=[size / w, 0, 0, size / h, 0, 0])
    d.add(widget)
    return d


def build_routes_pdf(payloads):
    """Satu PDF; tiap rute mulai di halaman baru. Untuk satu rute = lembar cetak per kurir."""
    buf = io.BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm,
        topMargin=14 * mm, bottomMargin=18 * mm,
        title="Lembar Rute", author="Routing & Extractor",
    )
    state = {"label": None, "page": 0}

    def footer(canvas, _doc):
        label = getattr(canvas, "_route_label", "")
        state["page"] = 1 if label != state["label"] else state["page"] + 1
        state["label"] = label
        canvas.saveState()
        canvas.setStrokeColor(rl_colors.HexColor("#D1D5DB"))
        canvas.line(14 * mm, 13 * mm, A4[0] - 14 * mm, 13 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(rl_colors.HexColor("#6B7280"))
        canvas.drawString(14 * mm, 8.5 * mm, f"{label}  -  Halaman {state['page']}")
        canvas.drawRightString(A4[0] - 14 * mm, 8.5 * mm, "Routing & Extractor")
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPageEnd=footer)])

    st_title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=rl_colors.white)
    st_kicker = ParagraphStyle("k", fontName="Helvetica", fontSize=8.5, leading=11, textColor=rl_colors.HexColor("#DBEAFE"))
    st_right = ParagraphStyle("r", fontName="Helvetica", fontSize=9.5, leading=13, textColor=rl_colors.white, alignment=2)
    st_meta = ParagraphStyle("m", fontName="Helvetica", fontSize=9.5, leading=14, textColor=rl_colors.HexColor("#111827"))
    st_cell = ParagraphStyle("c", fontName="Helvetica", fontSize=9.5, leading=12, textColor=rl_colors.HexColor("#111827"))
    st_head = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=rl_colors.white)
    st_small = ParagraphStyle("s", fontName="Helvetica", fontSize=8, leading=10, textColor=rl_colors.HexColor("#6B7280"))
    st_h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=rl_colors.HexColor("#111827"))

    story = []
    for pi, p in enumerate(payloads):
        if pi > 0:
            story.append(PageBreak())
        label = f"Rute {p['route_no']}"
        story.append(_SetRoute(label))

        band = Table(
            [[[Paragraph("LEMBAR RUTE", st_kicker), Paragraph(label, st_title)],
              Paragraph(
                  xml_escape(_fmt_date_id(p["date"]))
                  + (f"<br/>Mulai {xml_escape(p['start_label'])}" if p["start_label"] else ""), st_right)]],
            colWidths=[doc.width * 0.62, doc.width * 0.38],
        )
        band.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), rl_colors.HexColor(PDF_BRAND)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story += [band, Spacer(1, 4 * mm)]

        n_stops = len(p["rows"]) - (1 if p["has_start"] else 0)
        parts = [f"<b>{n_stops}</b> merchant", f"<b>~{p['distance_km']:.1f} km</b>",
                 f"Perjalanan {xml_escape(format_duration(p['duration_sec']))}"]
        if p["visit_sec"]:
            parts.append(f"Kunjungan {xml_escape(format_duration(p['visit_sec']))}")
        if p["finish_label"]:
            parts.append(f"Selesai +/-{xml_escape(p['finish_label'])}" + (" (sudah pulang)" if p["round_trip"] else ""))
        if p.get("depot_name"):
            parts.append(f"Titik awal: {xml_escape(p['depot_name'])}")
        story.append(Paragraph("  |  ".join(parts), st_meta))
        story.append(Spacer(1, 2 * mm))
        kurir_val = f"<b>{xml_escape(p['driver'])}</b>" if p.get("driver") else "________________________________"
        story.append(Paragraph(
            f"Kurir: {kurir_val} &nbsp;&nbsp;&nbsp; Kendaraan / Plat: ____________________", st_meta))
        if p["manual"]:
            story.append(Spacer(1, 1.5 * mm))
            story.append(Paragraph("Urutan kunjungan telah disesuaikan secara manual.", st_small))
        story.append(Spacer(1, 4 * mm))

        # tabel kunjungan
        head = ["No", "Merchant", "Tiba"] + (["Selesai"] if p["show_selesai"] else []) + ["Cek", "Catatan"]
        data = [[Paragraph(h, st_head) for h in head]]

        def row_cells(no, name_html, tiba, selesai, note=""):
            cells = [Paragraph(no, st_cell), Paragraph(name_html, st_cell), Paragraph(xml_escape(tiba), st_cell)]
            if p["show_selesai"]:
                cells.append(Paragraph(xml_escape(selesai), st_cell))
            note_color = "#DC2626" if note.startswith("⚠️") else "#111827"
            cells += [_CheckBox(), Paragraph(f"<font color='{note_color}'>{xml_escape(_pdf_safe(note))}</font>", st_cell)]
            return cells

        for i, row in enumerate(p["rows"]):
            is_start = p["has_start"] and i == 0
            name = xml_escape(_pdf_safe(row["name"])) or "-"
            # "⭐" bukan karakter Latin-1 dan akan hilang diam-diam di font PDF
            # bawaan, jadi dipakai label teks biasa supaya tetap kelihatan di cetakan.
            star = "<font color='#D97706'><b>[PRIORITAS]</b></font> " if row.get("priority") and not is_start else ""
            prefix = "<font color='#2563EB'><b>[TITIK AWAL]</b></font> " if is_start else star
            coord = f"<br/><font size='7' color='#6B7280'>{row['lat']:.6f}, {row['lon']:.6f}</font>"
            data.append(row_cells("S" if is_start else str(row["seq"]), f"{prefix}<b>{name}</b>{coord}",
                                  row["tiba"], row["selesai"], row.get("note", "")))
        if p["round_trip"] and p["rows"]:
            data.append(row_cells("-", "<i>Kembali ke titik awal</i>", p["back_label"], ""))

        fixed = 11 + 20 + (20 if p["show_selesai"] else 0) + 12
        merch_w = 70
        notes_w = max(30, doc.width / mm - fixed - merch_w)
        widths = [11 * mm, merch_w * mm, 20 * mm] + ([20 * mm] if p["show_selesai"] else []) + [12 * mm, notes_w * mm]
        tbl = Table(data, colWidths=widths, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#1E3A8A")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor("#F3F6FC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (-2, 1), (-2, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(tbl)

        # QR Google Maps: 50 mm (cukup besar untuk dipindai kamera HP), maks. 3 per baris, maks. 6 bagian
        if p["links"]:
            story.append(Spacer(1, 6 * mm))
            total = len(p["links"])
            qr_cells = []
            for i, (ia, ib, url) in enumerate(p["links"][:6], start=1):
                cap = ("Buka seluruh rute di Google Maps" if total == 1
                       else f"Bagian {i}/{total}: titik {p['seq_nums'][ia]} - {p['seq_nums'][ib]}")
                qr_cells.append([_qr_drawing(url, 50 * mm), Paragraph(xml_escape(cap), st_small)])
            qr_rows = [qr_cells[k:k + 3] for k in range(0, len(qr_cells), 3)]
            qr_tbl = Table(qr_rows, colWidths=[58 * mm] * min(3, len(qr_cells)), hAlign="LEFT")
            qr_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
            block = [Paragraph("Scan dengan kamera HP untuk membuka rute di Google Maps", st_h2),
                     Spacer(1, 2 * mm), qr_tbl]
            if total > 6:
                block.append(Paragraph(f"Rute panjang dibagi {total} bagian; 6 bagian pertama ditampilkan.", st_small))
            story.append(KeepTogether(block))

    doc.build(story)
    return buf.getvalue()


@st.cache_data(show_spinner=False, max_entries=64)
def _routes_pdf_cached(payloads):
    return build_routes_pdf(payloads)
# --- PDF-END ---


def _template_df():
    return pd.DataFrame(
        {
            "merchant_name": ["Toko A", "Toko B", "Toko C"],
            "latitude": [-7.5665, -7.5700, -7.5610],
            "longitude": [110.8167, 110.8200, 110.8100],
        }
    )


def make_template_excel():
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        _template_df().to_excel(writer, index=False)
    return buf.getvalue()


def make_template_csv():
    return _template_df().to_csv(index=False).encode("utf-8-sig")


# ==========================================================================================
# SESSION STATE INIT
# ==========================================================================================
if "page" not in st.session_state:
    st.session_state.page = "Routing"
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = []
if "routing_df" not in st.session_state:
    st.session_state.routing_df = None
# Streamlit membuang state widget yang tidak dirender (mis. saat pindah halaman).
# Karena itu input halaman Routing disimpan di session_state biasa, bukan di widget.
if "uploaded_store" not in st.session_state:
    st.session_state.uploaded_store = {}  # {nama_file: bytes}
if "uploader_nonce" not in st.session_state:
    st.session_state.uploader_nonce = 0  # ganti key uploader supaya kosong setelah file disimpan
if "use_extracted_flag" not in st.session_state:
    st.session_state.use_extracted_flag = False
if "starting_link_saved" not in st.session_state:
    st.session_state.starting_link_saved = ""
if "multi_depot_saved" not in st.session_state:
    st.session_state.multi_depot_saved = ""
if "use_multi_depot_flag" not in st.session_state:
    st.session_state.use_multi_depot_flag = False
if "driver_names" not in st.session_state:
    st.session_state.driver_names = {}  # {route_id: nama}


def _detect_default_mode():
    """Tebak mode awal dari User-Agent: HP -> Mobile, selain itu Desktop."""
    try:
        ua = (st.context.headers.get("User-Agent") or "").lower()
    except Exception:
        return "Desktop"
    return "Mobile" if ("iphone" in ua or "ipod" in ua or "mobile" in ua) else "Desktop"


if "view_mode" not in st.session_state:
    st.session_state.view_mode = _detect_default_mode()
IS_MOBILE = st.session_state.view_mode == "Mobile"

MOBILE_CSS = """
<style>
/* ===== MODE HANDPHONE ===== */
.block-container {padding: 3.4rem 0.8rem 4rem 0.8rem !important; max-width: 100% !important;}
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {display: none !important;}

.hero-header {padding: 16px 16px; border-radius: 14px; margin-bottom: 14px;}
.hero-header h1 {font-size: 1.25rem;}
.hero-header p {font-size: 0.8rem; line-height: 1.4;}
.section-header {margin: 20px 0 10px 0; gap: 10px;}
.section-header .badge {width: 32px; height: 32px;}
.metric-card {padding: 12px 14px;}
.metric-card .metric-value {font-size: 1.25rem;}
.empty-state {padding: 26px 16px;}

/* target sentuh lebih besar + cegah zoom otomatis iOS */
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    min-height: 3rem; font-size: 1rem !important;
}
input, textarea, [data-baseweb="select"] {font-size: 16px !important;}
[data-testid="stFileUploaderDropzone"] {padding: 1rem;}

/* semua kolom ditumpuk ke bawah */
[data-testid="stHorizontalBlock"] {flex-direction: column !important; gap: 0.6rem !important;}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
}

/* pengecualian: baris yang tetap berdampingan */
.st-key-navrow [data-testid="stHorizontalBlock"],
.st-key-moderow [data-testid="stHorizontalBlock"],
[class*="st-key-mvrow"] [data-testid="stHorizontalBlock"],
[class*="st-key-filerow"] [data-testid="stHorizontalBlock"] {
    flex-direction: row !important; flex-wrap: nowrap !important; gap: 0.5rem !important;
}
.st-key-navrow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-moderow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[class*="st-key-mvrow"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-navrow [data-testid="stHorizontalBlock"] > [data-testid="column"],
.st-key-moderow [data-testid="stHorizontalBlock"] > [data-testid="column"],
[class*="st-key-mvrow"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: auto !important; flex: 1 1 0 !important; min-width: 0 !important;
}
.st-key-moderow .stButton > button {min-height: 2.4rem; font-size: 0.85rem !important;}
[class*="st-key-filerow"] [data-testid="stColumn"]:first-child,
[class*="st-key-filerow"] [data-testid="column"]:first-child {
    width: auto !important; flex: 1 1 0 !important; min-width: 0 !important; overflow-wrap: anywhere;
}
[class*="st-key-filerow"] [data-testid="stColumn"]:last-child,
[class*="st-key-filerow"] [data-testid="column"]:last-child {
    width: 3.2rem !important; flex: 0 0 3.2rem !important; min-width: 3.2rem !important;
}

/* kartu metrik: 2 kolom (grid) */
.st-key-grid2 [data-testid="stHorizontalBlock"],
.st-key-grid4 [data-testid="stHorizontalBlock"] {
    flex-direction: row !important; flex-wrap: wrap !important; gap: 0.6rem !important;
}
.st-key-grid2 [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-grid4 [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-grid2 [data-testid="stHorizontalBlock"] > [data-testid="column"],
.st-key-grid4 [data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: calc(50% - 0.3rem) !important; flex: 0 0 calc(50% - 0.3rem) !important;
    min-width: calc(50% - 0.3rem) !important;
}

.stTabs [role="tablist"] {overflow-x: auto;}
.stTabs [data-baseweb="tab"] {padding: 0.5rem 0.7rem;}
div[data-testid="stExpander"] {margin-bottom: 10px; border-radius: 12px !important;}
</style>
"""
if IS_MOBILE:
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

MAP_H = 260 if IS_MOBILE else 350
COMBINED_MAP_H = 380 if IS_MOBILE else 520
# Hanya kirim `height` di mode Mobile; height=None ditolak Streamlit versi baru.
TABLE_KW = {"height": 260} if IS_MOBILE else {}


SPLIT_FULL = "📦 Isi penuh"
SPLIT_AUTO = "🧭 Otomatis (per area)"
if "split_mode_flag" not in st.session_state:
    st.session_state.split_mode_flag = SPLIT_AUTO


def _sync_split():
    st.session_state.split_mode_flag = st.session_state._split_widget


def _fmt_sizes(sizes):
    shown = " + ".join(str(x) for x in sizes[:5])
    return shown + (" + …" if len(sizes) > 5 else "")


if "round_trip_flag" not in st.session_state:
    st.session_state.round_trip_flag = False
if "dedupe_flag" not in st.session_state:
    st.session_state.dedupe_flag = True


def _sync_round_trip():
    # .get() with a fallback — not direct attribute access — because
    # "Buka Sesi" deliberately pops these widget keys to force a refresh,
    # and if that happens to land in the same batch as this callback
    # (e.g. the user edits a field then immediately clicks "Buka Sesi"
    # before it blurs), the key can be briefly missing. Attribute access
    # would crash the whole app in that case; .get() just no-ops safely.
    st.session_state.round_trip_flag = st.session_state.get(
        "_round_trip_widget", st.session_state.round_trip_flag
    )


def _sync_dedupe():
    st.session_state.dedupe_flag = st.session_state.get(
        "_dedupe_widget", st.session_state.dedupe_flag
    )


def _sync_use_extracted():
    st.session_state.use_extracted_flag = st.session_state.get(
        "_use_extracted_widget", st.session_state.use_extracted_flag
    )


def _sync_starting_link():
    st.session_state.starting_link_saved = st.session_state.get(
        "_starting_link_widget", st.session_state.starting_link_saved
    )


def _sync_multi_depot():
    st.session_state.multi_depot_saved = st.session_state.get(
        "_multi_depot_widget", st.session_state.multi_depot_saved
    )


def _sync_use_multi_depot():
    st.session_state.use_multi_depot_flag = st.session_state.get(
        "_use_multi_depot_widget", st.session_state.use_multi_depot_flag
    )


PLAN_MAX = "📏 Maksimal titik per rute"
PLAN_COUNT = "👥 Jumlah rute (mis. jumlah sales)"
for _k, _v in {
    "plan_mode_flag": PLAN_MAX,
    "target_routes_flag": 2,
    "visit_minutes_flag": 0,
    "start_time_flag": datetime.time(8, 0),
    "session_nonce": 0,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def _sync_plan():
    st.session_state.plan_mode_flag = st.session_state.get(
        "_plan_widget", st.session_state.plan_mode_flag
    )


def _sync_target():
    st.session_state.target_routes_flag = int(
        st.session_state.get("_target_widget", st.session_state.target_routes_flag)
    )


def _sync_visit():
    st.session_state.visit_minutes_flag = int(
        st.session_state.get("_visit_widget", st.session_state.visit_minutes_flag)
    )


def _sync_start_time():
    st.session_state.start_time_flag = st.session_state.get(
        "_start_time_widget", st.session_state.start_time_flag
    )


# ---------- Simpan / buka sesi ----------
MAX_SESSION_BYTES = 40 * 1024 * 1024
SESSION_WIDGET_KEYS = (
    "_use_extracted_widget", "_starting_link_widget", "_round_trip_widget", "_dedupe_widget",
    "_split_widget", "_plan_widget", "_target_widget", "_visit_widget", "_start_time_widget",
    "_multi_depot_widget", "_use_multi_depot_widget",
    "extract_editor",
)


def build_session_bytes():
    ss = st.session_state
    extracted = [
        {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in row.items()}
        for row in ss.extracted_data
    ]
    payload = {
        "app": "routing-extractor",
        "version": 1,
        "saved_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "files": {name: base64.b64encode(data).decode("ascii") for name, data in ss.uploaded_store.items()},
        "extracted_data": extracted,
        "settings": {
            "use_extracted_flag": bool(ss.use_extracted_flag),
            "starting_link_saved": ss.starting_link_saved,
            "round_trip_flag": bool(ss.round_trip_flag),
            "dedupe_flag": bool(ss.dedupe_flag),
            "split_mode_flag": ss.split_mode_flag,
            "plan_mode_flag": ss.plan_mode_flag,
            "target_routes_flag": int(ss.target_routes_flag),
            "visit_minutes_flag": int(ss.visit_minutes_flag),
            "start_time_flag": ss.start_time_flag.strftime("%H:%M"),
            "multi_depot_saved": ss.multi_depot_saved,
            "use_multi_depot_flag": bool(ss.use_multi_depot_flag),
            "driver_names": {str(k): str(v) for k, v in ss.driver_names.items()},
        },
    }
    return json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")


def load_session_bytes(raw):
    """Muat file sesi. Isi file diperlakukan sebagai data: divalidasi, bukan dijalankan."""
    if len(raw) > MAX_SESSION_BYTES:
        return False, "File sesi terlalu besar."
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except Exception:
        return False, "File sesi tidak bisa dibaca (bukan JSON yang valid)."
    if not isinstance(data, dict) or data.get("app") != "routing-extractor":
        return False, "File ini bukan file sesi dari aplikasi ini."

    files_raw = data.get("files")
    files = {}
    for name, b64 in (files_raw if isinstance(files_raw, dict) else {}).items():
        if not isinstance(name, str) or not isinstance(b64, str):
            continue
        safe_name = os.path.basename(name) or "data.xlsx"
        try:
            files[safe_name] = base64.b64decode(b64, validate=True)
        except Exception:
            return False, f"File '{safe_name}' di dalam sesi rusak."

    ext_raw = data.get("extracted_data")
    extracted = [
        {str(k): v for k, v in row.items()}
        for row in (ext_raw[:5000] if isinstance(ext_raw, list) else [])
        if isinstance(row, dict)
    ]

    cfg = data.get("settings") if isinstance(data.get("settings"), dict) else {}
    updates = {}
    for key in ("use_extracted_flag", "round_trip_flag", "dedupe_flag"):
        if isinstance(cfg.get(key), bool):
            updates[key] = cfg[key]
    if isinstance(cfg.get("starting_link_saved"), str):
        updates["starting_link_saved"] = cfg["starting_link_saved"][:2000]
    if cfg.get("split_mode_flag") in (SPLIT_AUTO, SPLIT_FULL):
        updates["split_mode_flag"] = cfg["split_mode_flag"]
    if cfg.get("plan_mode_flag") in (PLAN_MAX, PLAN_COUNT):
        updates["plan_mode_flag"] = cfg["plan_mode_flag"]
    if isinstance(cfg.get("target_routes_flag"), int) and 1 <= cfg["target_routes_flag"] <= 10000:
        updates["target_routes_flag"] = cfg["target_routes_flag"]
    if isinstance(cfg.get("visit_minutes_flag"), int) and 0 <= cfg["visit_minutes_flag"] <= 480:
        updates["visit_minutes_flag"] = cfg["visit_minutes_flag"]
    if isinstance(cfg.get("start_time_flag"), str):
        try:
            updates["start_time_flag"] = datetime.datetime.strptime(cfg["start_time_flag"], "%H:%M").time()
        except ValueError:
            pass
    if isinstance(cfg.get("multi_depot_saved"), str):
        updates["multi_depot_saved"] = cfg["multi_depot_saved"][:4000]
    if isinstance(cfg.get("use_multi_depot_flag"), bool):
        updates["use_multi_depot_flag"] = cfg["use_multi_depot_flag"]
    driver_names_raw = cfg.get("driver_names")
    driver_names = {}
    if isinstance(driver_names_raw, dict):
        for k, v in driver_names_raw.items():
            try:
                driver_names[int(k)] = str(v)[:120]
            except (TypeError, ValueError):
                continue

    ss = st.session_state
    ss.uploaded_store = files
    ss.extracted_data = extracted
    ss.driver_names = driver_names
    for k, v in updates.items():
        ss[k] = v
    for wk in SESSION_WIDGET_KEYS:  # supaya nilai baru dipakai oleh widget
        ss.pop(wk, None)
    ss.route_result = None
    ss.uploader_nonce += 1
    return True, f"Sesi dimuat: {len(files)} file dan {len(extracted)} data Maps Extractor."


def render_session_panel(prefix):
    ss = st.session_state
    flash = ss.pop("_session_flash", None)
    with st.expander("💾 Simpan / Buka Sesi", expanded=flash is not None):
        if flash:
            (st.success if flash[0] == "ok" else st.error)(flash[1])
        st.caption(
            "Simpan data & pengaturan ke satu file untuk dilanjutkan nanti, bahkan setelah halaman "
            "di-refresh. Hasil rute tidak ikut disimpan — tinggal tekan Buat Rute lagi. "
            "File berisi data merchant, jadi simpan di tempat yang aman."
        )
        st.download_button(
            "💾 Simpan sesi",
            data=build_session_bytes(),
            file_name=f"sesi-rute-{datetime.datetime.now():%Y%m%d-%H%M}.json",
            mime="application/json",
            key=f"{prefix}_session_dl",
            width='stretch',
            disabled=not (ss.uploaded_store or ss.extracted_data),
        )
        up = st.file_uploader("📂 Buka sesi (.json)", type=["json"], key=f"{prefix}_session_up_{ss.session_nonce}")
        if up is not None:
            ok, msg = load_session_bytes(up.getvalue())
            ss._session_flash = ("ok" if ok else "err", msg)
            ss.session_nonce += 1
            st.rerun()

# ==========================================================================================
# NAVIGASI + PILIHAN MODE TAMPILAN
# ==========================================================================================
def _set_mode(mode):
    st.session_state.view_mode = mode


def render_mode_toggle(prefix):
    """Dua tombol: 🖥️ Desktop | 📱 Mobile."""
    mode = st.session_state.view_mode
    m1, m2 = st.columns(2)
    with m1:
        st.button(
            "🖥️ Desktop", key=f"{prefix}_mode_desktop", width='stretch',
            type="primary" if mode == "Desktop" else "secondary",
            on_click=_set_mode, args=("Desktop",),
        )
    with m2:
        st.button(
            "📱 Mobile", key=f"{prefix}_mode_mobile", width='stretch',
            type="primary" if mode == "Mobile" else "secondary",
            on_click=_set_mode, args=("Mobile",),
        )


def render_nav(prefix, horizontal=False):
    # Plain buttons (not a key-bound widget) so the active page can be set
    # programmatically from anywhere — e.g. the "pakai di Routing Optimizer"
    # button on the Extract page — without hitting Streamlit's restriction
    # on mutating a widget's own session-state key after it's been created.
    nav_routing_active = st.session_state.page == "Routing"
    nav_extract_active = st.session_state.page == "Extract"
    label_routing = "🛣️ Routing" if horizontal else "🛣️  Routing Optimizer"
    label_extract = "📍 Extractor" if horizontal else "📍  Maps Extractor"

    if horizontal:
        n1, n2 = st.columns(2)
    else:
        n1 = n2 = st.container()

    with n1:
        go_routing = st.button(
            label_routing, key=f"{prefix}_nav_routing", width='stretch',
            type="primary" if nav_routing_active else "secondary",
        )
    with n2:
        go_extract = st.button(
            label_extract, key=f"{prefix}_nav_extract", width='stretch',
            type="primary" if nav_extract_active else "secondary",
        )

    if go_routing:
        st.session_state.page = "Routing"
        st.rerun()
    if go_extract:
        st.session_state.page = "Extract"
        st.rerun()


def render_howto():
    # Selalu tertutup saat pertama dibuka — pengguna bisa membukanya sendiri kalau perlu.
    with st.expander("ℹ️ Cara Pakai (3 Langkah)", expanded=False):
        st.markdown(
            "**1. Kumpulkan data** 📍  \n"
            "Di **Maps Extractor**: tempel link Google Maps, cari nama merchant, atau isi manual "
            "(koordinat bisa ditempel sekaligus). Sudah punya file Excel/CSV? Upload langsung di "
            "**Routing Optimizer** — atau klik **🧪 Coba dengan data contoh** untuk melihat cara kerjanya.\n\n"
            "**2. Atur rute** 🛣️  \n"
            "Di **Routing Optimizer**: pilih cara membagi rute (maksimal titik per rute, atau jumlah rute "
            "misalnya jumlah sales), jam mulai, durasi kunjungan per toko, titik awal (opsional, boleh link "
            "Google Maps atau koordinat), dan apakah rute kembali ke titik awal. Lalu klik "
            "**Buat Rute Optimal Sekarang**.\n\n"
            "**3. Pakai hasilnya** 📥  \n"
            "Lihat urutan kunjungan dan perkiraan jam tiba, isi nama kurir per rute, buka di Google Maps, "
            "kirim ke WhatsApp, atau unduh semua rute sebagai Excel/PDF.\n\n"
            "⭐ **Fitur tambahan (opsional):**\n"
            "- **Prioritas** — tambah kolom `prioritas` (ya/tidak) di Excel/CSV, merchant itu dikunjungi lebih dulu.\n"
            "- **Jam operasional** — tambah kolom `jam_buka`/`jam_tutup` (format HH:MM), perkiraan jam tiba "
            "dicek otomatis dan ditandai ⚠️ kalau di luar jam buka.\n"
            "- **Multi-depot** — centang \"Pakai banyak titik awal\" dan isi daftar gudang/toko pusat; "
            "tiap rute otomatis mulai dari yang terdekat.\n"
            "- **Nama kurir** — isi di tiap rute setelah dibuat, ikut masuk ke Excel, WhatsApp, dan PDF.\n\n"
            "💾 **Tips:** data tetap tersimpan selama halaman tidak di-refresh, walau kamu pindah menu. "
            "Untuk melanjutkan di lain waktu, pakai **Simpan / Buka Sesi**."
        )


if IS_MOBILE:
    # Di HP sidebar disembunyikan (susah dibuka) — navigasi & mode pindah ke atas halaman.
    with st.container(key="navrow"):
        render_nav("top", horizontal=True)
    with st.container(key="moderow"):
        render_mode_toggle("top")
    render_howto()
    render_session_panel("top")
else:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <span class="emoji">⚡</span>
                <div>
                    <div class="title">Routing &amp; Extractor</div>
                    <div class="subtitle">Rute otomatis, lebih singkat & rapi</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        render_nav("side")
        st.markdown("---")
        st.caption("Mode tampilan")
        render_mode_toggle("side")
        st.markdown("---")
        render_howto()
        render_session_panel("side")
        st.caption("⚡ Developed by **Abdillah**")


# ================================================================
# HALAMAN 1: ROUTING PIPELINE OPTIMIZER
# ================================================================
if st.session_state.page == "Routing":
    st.markdown(
        """
        <div class="hero-header">
            <h1>🛣️ Routing Pipeline Optimizer</h1>
            <p>Optimalkan rute kunjungan dengan clustering (KMeans) dan penentuan urutan kunjungan (TSP).</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stepper_slot = st.empty()
    render_stepper(stepper_slot, 0)

    section_header(
        "1️⃣", "Siapkan Data Merchant",
        "Upload file Excel/CSV, pakai data dari Maps Extractor, atau gabungan keduanya",
    )

    col_link, col_upload = st.columns([1, 1.3])
    with col_link:
        starting_link = st.text_input(
            "📍 Titik Awal (opsional)",
            value=st.session_state.starting_link_saved,
            key="_starting_link_widget",
            on_change=_sync_starting_link,
            placeholder="Link Google Maps atau koordinat (-7.5665, 110.8167)",
            help=(
                "Misalnya lokasi gudang atau toko pusat. Kalau diisi, titik ini otomatis jadi awal setiap rute. "
                "Cara dapat link: buka lokasinya di Google Maps → Bagikan → Salin link. "
                "Atau tempel koordinatnya langsung."
            ),
        )
    with col_upload:
        new_files = st.file_uploader(
            "📂 Upload Data (Excel / CSV)",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_nonce}",
            help="Format .xlsx atau .csv. Kolom wajib: merchant_name, latitude, longitude (koma desimal seperti -7,56 juga dikenali). Kolom opsional: prioritas (ya/tidak — dikunjungi lebih dulu), jam_buka & jam_tutup (HH:MM — dicek terhadap perkiraan jam tiba). Bisa pilih beberapa file sekaligus — nanti otomatis digabung. File yang sudah diupload tetap tersimpan walau kamu pindah ke Maps Extractor.",
        )
        if new_files:
            for nf in new_files:
                st.session_state.uploaded_store[nf.name] = nf.getvalue()
            st.session_state.uploader_nonce += 1
            st.rerun()

    use_multi_depot = st.checkbox(
        "🏭 Pakai banyak titik awal (multi-depot)",
        value=st.session_state.use_multi_depot_flag,
        key="_use_multi_depot_widget",
        on_change=_sync_use_multi_depot,
        help=(
            "Aktifkan kalau kurir berangkat dari beberapa gudang/toko berbeda. Tiap rute otomatis "
            "memakai titik awal TERDEKAT dari daftar di bawah — menggantikan 'Titik Awal' tunggal di atas."
        ),
    )
    multi_depot_text = ""
    if use_multi_depot:
        multi_depot_text = st.text_area(
            "Daftar titik awal — satu per baris: Nama|link Google Maps atau koordinat",
            value=st.session_state.multi_depot_saved,
            key="_multi_depot_widget",
            on_change=_sync_multi_depot,
            placeholder="Gudang Utara|https://maps.app.goo.gl/xxxx\nGudang Selatan|-7.60, 110.85",
            height=100,
        )
        _depots_preview, _depot_errors_preview = parse_depot_list(multi_depot_text)
        for _err in _depot_errors_preview:
            st.warning(f"⚠️ {_err}")
        if _depots_preview:
            st.caption(
                f"✅ {len(_depots_preview)} titik awal terbaca: "
                + ", ".join(d["name"] for d in _depots_preview)
            )
        else:
            st.caption("Belum ada titik awal yang terbaca — isi minimal satu baris di atas.")

    # Daftar file yang tersimpan (tetap ada setelah pindah halaman)
    if st.session_state.uploaded_store:
        st.caption(f"📎 {len(st.session_state.uploaded_store)} file tersimpan")
        for i, fname in enumerate(list(st.session_state.uploaded_store.keys())):
            with st.container(key=f"filerow_{i}"):
                fc1, fc2 = st.columns([6, 1])
                with fc1:
                    st.markdown(f"📄 `{fname}`")
                with fc2:
                    if st.button("✖", key=f"rm_{fname}", help=f"Hapus {fname}"):
                        st.session_state.uploaded_store.pop(fname, None)
                        st.rerun()

    if not st.session_state.uploaded_store and not st.session_state.extracted_data:
        if st.button("🧪 Coba dengan data contoh (12 merchant)", width='stretch',
                     help="Memuat 12 merchant fiktif di sekitar Surakarta supaya kamu bisa langsung mencoba. Bisa dihapus kapan saja dengan tombol ✖."):
            st.session_state.uploaded_store["data_contoh.csv"] = make_sample_csv()
            st.rerun()

    use_extracted = False
    if st.session_state.extracted_data:
        use_extracted = st.checkbox(
            f"📋 Pakai {len(st.session_state.extracted_data)} data dari Maps Extractor",
            value=st.session_state.use_extracted_flag,
            key="_use_extracted_widget",
            on_change=_sync_use_extracted,
            help="Bisa dicentang bersamaan dengan upload Excel di atas — keduanya akan digabung otomatis.",
        )
    else:
        st.session_state.use_extracted_flag = False

    tpl1, tpl2 = st.columns(2)
    with tpl1:
        st.download_button(
            "⬇️ Template Excel",
            data=make_template_excel(),
            file_name="template_routing.xlsx",
            mime="application/vnd.ms-excel",
            help="Belum punya file? Download contoh formatnya di sini supaya langsung cocok.",
            width='stretch',
        )
    with tpl2:
        st.download_button(
            "⬇️ Template CSV",
            data=make_template_csv(),
            file_name="template_routing.csv",
            mime="text/csv",
            help="Contoh format CSV (kolom: merchant_name, latitude, longitude).",
            width='stretch',
        )

    df = None
    valid_parts = []
    file_errors = []

    for fname, fbytes in st.session_state.uploaded_store.items():
        try:
            file_df = read_table_file(fname, fbytes)
        except Exception as e:
            file_errors.append(f"**{fname}**: gagal dibaca ({e})")
            continue

        is_valid, errors = validate_dataframe(file_df)
        if not is_valid:
            for err in errors:
                file_errors.append(f"**{fname}**: {err}")
            continue

        file_df = file_df.copy()
        file_df["source_file"] = fname
        valid_parts.append(file_df)

    if use_extracted:
        extracted_df = pd.DataFrame(st.session_state.extracted_data)
        is_valid, errors = validate_dataframe(extracted_df)
        if not is_valid:
            for err in errors:
                file_errors.append(f"**Data Ekstraksi (Maps Extractor)**: {err}")
        else:
            extracted_df = extracted_df.copy()
            extracted_df["source_file"] = "Data Ekstraksi (Maps Extractor)"
            valid_parts.append(extracted_df)

    for err in file_errors:
        st.error(f"❌ {err}")

    if valid_parts:
        df = pd.concat(valid_parts, ignore_index=True)
        total_sources = len(st.session_state.uploaded_store) + (1 if use_extracted else 0)
        skipped = total_sources - len(valid_parts)
        msg = f"✅ {len(valid_parts)} sumber data berhasil digabung — total {len(df)} baris."
        if skipped:
            msg += f" ({skipped} sumber dilewati karena error di atas)"
        if len(valid_parts) > 1:
            st.success(msg)
    elif (st.session_state.uploaded_store or use_extracted) and not file_errors:
        # Shouldn't normally happen, but avoid silently doing nothing.
        st.info("Tidak ada data untuk diproses.")
    elif file_errors:
        st.stop()

    if df is not None:
        render_stepper(stepper_slot, 1)
        df["latitude"] = pd.to_numeric(df["latitude"])
        df["longitude"] = pd.to_numeric(df["longitude"])

        # Deteksi duplikat (nama sama + koordinat sama ~1 meter), mis. setelah
        # menggabungkan Excel dengan data Maps Extractor.
        _dup_mask = pd.DataFrame(
            {
                "n": df["merchant_name"].astype(str).str.strip().str.lower(),
                "a": df["latitude"].round(5),
                "o": df["longitude"].round(5),
            }
        ).duplicated()
        n_dup = int(_dup_mask.sum())
        if n_dup:
            remove_dups = st.checkbox(
                f"🧹 Hapus {n_dup} baris duplikat (nama & koordinat sama)",
                value=st.session_state.dedupe_flag,
                key="_dedupe_widget",
                on_change=_sync_dedupe,
                help="Baris pertama dipertahankan. Matikan kalau memang ada merchant kembar yang sengaja dimasukkan dua kali.",
            )
            if remove_dups:
                df = df[~_dup_mask].copy().reset_index(drop=True)

        with st.expander(f"📄 Lihat Data Awal ({len(df)} baris)", expanded=False):
            if "source_file" in df.columns:
                st.caption("💡 Kolom `source_file` menunjukkan file/sumber asal tiap baris setelah digabung.")
            st.dataframe(df, width='stretch', **TABLE_KW)

        _n_priority = int(df["prioritas"].apply(is_truthy).sum()) if "prioritas" in df.columns else 0
        _has_hours = "jam_buka" in df.columns or "jam_tutup" in df.columns
        if _n_priority or _has_hours:
            _notes = []
            if _n_priority:
                _notes.append(f"**{_n_priority} merchant prioritas** (kolom `prioritas`) akan dikunjungi lebih dulu di tiap rute")
            if _has_hours:
                _notes.append("**jam operasional** (kolom `jam_buka`/`jam_tutup`) akan dicek terhadap perkiraan jam tiba")
            st.info("ℹ️ " + " · ".join(_notes) + ".", icon="ℹ️")

        section_header(
            "2️⃣", "Atur Pembagian Rute",
            "Tentukan jumlah rute — lewat maksimal merchant per rute, atau langsung jumlah rute (mis. jumlah sales)",
        )
        plan_mode = st.radio(
            "Cara menentukan jumlah rute",
            [PLAN_MAX, PLAN_COUNT],
            index=0 if st.session_state.plan_mode_flag == PLAN_MAX else 1,
            key="_plan_widget",
            on_change=_sync_plan,
            horizontal=not IS_MOBILE,
        )
        if IS_MOBILE:
            max_points_per_route, target_routes = _plan_control(df, plan_mode)
            n_cluster_default = target_routes or math.ceil(len(df) / max_points_per_route)
            with st.container(key="grid2"):
                c2, c3 = st.columns(2)
                with c2:
                    metric_card("🏪", "Total Merchant", len(df))
                with c3:
                    metric_card("🧭", "Estimasi Jumlah Rute", n_cluster_default)
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                max_points_per_route, target_routes = _plan_control(df, plan_mode)
            n_cluster_default = target_routes or math.ceil(len(df) / max_points_per_route)
            with c2:
                metric_card("🏪", "Total Merchant", len(df))
            with c3:
                metric_card("🧭", "Estimasi Jumlah Rute", n_cluster_default)

        if target_routes is not None:
            split_mode = SPLIT_AUTO
            st.caption(
                f"Merchant dibagi ke {target_routes} rute mengikuti area lokasi, "
                f"maksimal {max_points_per_route} merchant per rute supaya beban merata."
            )
        elif n_cluster_default > 1:
            split_mode = st.radio(
                "Cara membagi rute",
                [SPLIT_AUTO, SPLIT_FULL],
                index=0 if st.session_state.split_mode_flag == SPLIT_AUTO else 1,
                key="_split_widget",
                on_change=_sync_split,
                horizontal=not IS_MOBILE,
                help=(
                    "Otomatis: merchant dikelompokkan menurut area/kedekatan lokasi, jadi jarak tempuh "
                    "lebih pendek, tapi isi tiap rute bisa berbeda (selalu di bawah atau sama dengan maksimal). "
                    "Isi penuh: tiap rute diisi sampai batas maksimal dan sisanya masuk rute terakhir, "
                    "tapi rute bisa lebih melebar karena merchant dari area lain ikut terambil."
                ),
            )
            _n, _k, _m = len(df), n_cluster_default, max_points_per_route
            if split_mode == SPLIT_FULL:
                full_sizes = [_m] * (_k - 1) + [_n - _m * (_k - 1)]
                st.caption(f"Isi tiap rute: {_fmt_sizes(full_sizes)} merchant.")
            else:
                st.caption(
                    f"Pembagian mengikuti area lokasi — {_k} rute, masing-masing maksimal {_m} merchant. "
                    "Pilih **Isi penuh** kalau ingin tiap rute berisi tepat sebanyak maksimal."
                )
        else:
            split_mode = st.session_state.split_mode_flag

        t1, t2 = st.columns(2)
        with t1:
            start_time = st.time_input(
                "⏰ Jam mulai",
                value=st.session_state.start_time_flag,
                key="_start_time_widget",
                on_change=_sync_start_time,
                step=300,
                help="Dipakai untuk menghitung perkiraan jam tiba di tiap merchant.",
            )
        with t2:
            visit_minutes = st.number_input(
                "🏪 Durasi kunjungan per toko (menit)",
                min_value=0, max_value=480, value=int(st.session_state.visit_minutes_flag), step=1,
                key="_visit_widget",
                on_change=_sync_visit,
                help="Waktu yang dihabiskan di tiap merchant. 0 = hanya hitung waktu perjalanan.",
            )

        round_trip = st.checkbox(
            "🔁 Kembali ke titik awal setelah rute selesai",
            value=st.session_state.round_trip_flag,
            key="_round_trip_widget",
            on_change=_sync_round_trip,
            help=(
                "Aktif: rute melingkar dan jarak/waktu sudah termasuk perjalanan pulang. "
                "Nonaktif: rute satu arah, berhenti di merchant terakhir. "
                "Kalau Titik Awal kosong, rute dimulai dari titik yang paling efisien."
            ),
        )

        _plan_txt = (
            f"{target_routes} rute (maks. {max_points_per_route}/rute)" if target_routes is not None
            else f"{n_cluster_default} rute (maks. {max_points_per_route} merchant/rute"
                 + (", isi penuh" if n_cluster_default > 1 and split_mode == SPLIT_FULL else
                    ", otomatis per area" if n_cluster_default > 1 else "") + ")"
        )
        st.info(
            f"**Ringkasan:** {len(df)} merchant → {_plan_txt} · mulai {start_time:%H:%M} · "
            + (f"{int(visit_minutes)} menit/toko" if visit_minutes else "tanpa durasi kunjungan")
            + " · " + ("pulang-pergi" if round_trip else "satu arah")
            + " · titik awal: " + ("sesuai isian" if starting_link else "otomatis (paling efisien)"),
            icon="🧾",
        )

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        run = st.button("🚀 Buat Rute Optimal Sekarang", type="primary", width='stretch')

        # Fingerprint of the current input+settings, so stale results (from a
        # previous file/slider value) don't linger after the inputs change.
        data_fingerprint = (
            len(df), tuple(df["merchant_name"]), max_points_per_route, target_routes, starting_link,
            round_trip, split_mode, int(visit_minutes), start_time.strftime("%H:%M"),
            use_multi_depot, multi_depot_text,
        )

        if run:
            if len(df) < 2:
                st.warning("⚠️ Minimal butuh 2 titik untuk bisa membuat rute.")
                st.stop()

            with st.spinner("🔄 Mengelompokkan titik dan mencari rute tercepat di jalan asli..."):
                n_cluster = target_routes or math.ceil(len(df) / max_points_per_route)
                n_cluster = max(1, min(n_cluster, len(df)))
                if target_routes is None and n_cluster > 1 and split_mode == SPLIT_FULL:
                    df["route"] = fill_clusters(df, max_points_per_route)
                else:
                    coords = df[["latitude", "longitude"]]
                    kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=10)
                    df["route"] = kmeans.fit_predict(coords)
                    df = balance_clusters(df, max_points_per_route)

                # Titik awal tunggal (dipakai kalau multi-depot tidak aktif).
                start_name, start_lat, start_lon = "START POINT", None, None
                if starting_link:
                    coord_lat = coord_lon = None
                    if "http" not in starting_link.lower():
                        coord_lat, coord_lon, _coord_err = parse_coordinate_text(starting_link)
                    if coord_lat is not None:
                        start_name, start_lat, start_lon = "Titik Awal", coord_lat, coord_lon
                    else:
                        parsed_name, start_lat, start_lon = extract_google_maps_data(starting_link)
                        start_name = parsed_name or "START POINT"

                # Daftar depot (kalau multi-depot aktif) — tiap rute nanti pakai yang TERDEKAT
                # dari centroid-nya sendiri, menggantikan titik awal tunggal di atas.
                depots = []
                if use_multi_depot and multi_depot_text.strip():
                    depots, _depot_errs = parse_depot_list(multi_depot_text)

                all_routes = []
                route_summaries = []
                any_fallback_used = False
                osrm_errors = []
                base_date = datetime.date.today()
                start_dt = datetime.datetime.combine(base_date, start_time)
                visit_sec = int(visit_minutes) * 60
                for route_id in sorted(df["route"].unique()):
                    route_df = df[df["route"] == route_id].reset_index(drop=True)

                    if depots:
                        centroid_lat = route_df["latitude"].mean()
                        centroid_lon = route_df["longitude"].mean()
                        chosen_depot = nearest_depot(depots, centroid_lat, centroid_lon)
                        route_start_name = chosen_depot["name"]
                        route_start_lat, route_start_lon = chosen_depot["lat"], chosen_depot["lon"]
                    else:
                        route_start_name, route_start_lat, route_start_lon = start_name, start_lat, start_lon

                    if route_start_lat and route_start_lon:
                        start_df = pd.DataFrame(
                            [{"merchant_name": route_start_name, "latitude": route_start_lat, "longitude": route_start_lon}]
                        )
                        route_df = pd.concat([start_df, route_df], ignore_index=True)

                    distance_matrix, duration_matrix, used_real_roads, osrm_error = get_route_matrices(route_df)
                    any_fallback_used = any_fallback_used or not used_real_roads
                    if osrm_error:
                        osrm_errors.append(osrm_error)

                    has_start = bool(route_start_lat and route_start_lon)

                    # Merchant prioritas (kolom opsional "prioritas"): dikunjungi lebih
                    # dulu, baru lanjut ke sisanya.
                    if "prioritas" in route_df.columns:
                        p_mask = route_df["prioritas"].apply(is_truthy)
                        priority_idx = [i for i in range(len(route_df)) if p_mask.iloc[i] and not (has_start and i == 0)]
                    else:
                        priority_idx = []

                    if priority_idx:
                        other_idx = [
                            i for i in range(len(route_df))
                            if not (has_start and i == 0) and i not in priority_idx
                        ]
                        best_route = solve_tsp_with_priority(
                            distance_matrix, priority_idx, other_idx, has_start, round_trip
                        )
                    else:
                        best_route = solve_tsp(distance_matrix, round_trip=round_trip, fixed_start=has_start)

                    fin = finalize_route(
                        route_df, best_route, distance_matrix, duration_matrix, route_id,
                        start_dt, visit_sec, has_start, round_trip, base_date,
                    )
                    all_routes.append(fin["df"])
                    route_summaries.append(
                        {
                            "route_id": route_id,
                            **fin,
                            "real_roads": used_real_roads,
                            "round_trip": round_trip,
                            "has_start": has_start,
                            "depot_name": route_start_name if has_start else "",
                            "driver": st.session_state.driver_names.get(route_id, ""),
                            # data mentah untuk ubah-urutan manual (tanpa memanggil OSRM lagi)
                            "route_df": route_df,
                            "distance_matrix": distance_matrix,
                            "duration_matrix": duration_matrix,
                            "order": list(best_route),
                            "optimal_order": list(best_route),
                            "optimal_distance_km": fin["distance_km"],
                            "optimal_duration_sec": fin["duration_sec"],
                            "manual": False,
                            "start_dt": start_dt,
                            "visit_sec_each": visit_sec,
                            "base_date": base_date,
                        }
                    )

            excel_bytes = build_excel_bytes(route_summaries)
            n_start_points = sum(1 for r in route_summaries if r["has_start"])

            # Persist everything needed to render the result, so later reruns
            # (e.g. clicking the map or the download button) don't wipe it out.
            st.session_state.route_result = {
                "fingerprint": data_fingerprint,
                "route_summaries": route_summaries,
                "total_points": len(df) + n_start_points,
                "excel_bytes": excel_bytes,
                "base_date": base_date.isoformat(),
                "start_label": start_time.strftime("%H:%M"),
                "start_ok": bool(start_lat and start_lon) or bool(depots),
                "start_link_given": bool(starting_link) and not bool(depots),
                "used_real_roads": not any_fallback_used,
                "osrm_error": osrm_errors[-1] if osrm_errors else None,
                "multi_depot_used": bool(depots),
                "multi_depot_overrode_single": bool(depots) and bool(starting_link),
            }

        result = st.session_state.get("route_result")
        if result and result["fingerprint"] == data_fingerprint:
            if result["start_link_given"] and not result["start_ok"]:
                st.warning("⚠️ Titik awal tidak dikenali (bukan link Google Maps atau koordinat yang valid), jadi dilewati — rute tetap dibuat tanpa titik awal khusus.")
            if result.get("multi_depot_overrode_single"):
                st.caption("ℹ️ Multi-depot aktif — daftar titik awal menggantikan field 'Titik Awal' tunggal untuk pembuatan rute ini.")

            if not result.get("used_real_roads", True):
                reason = result.get("osrm_error")
                st.warning(
                    "⚠️ Layanan rute jalan asli (OSRM) tidak bisa dipakai untuk sebagian/seluruh rute — "
                    "rute bertanda ⚠️ memakai estimasi garis lurus (±30 km/jam), jadi jarak & waktunya bisa "
                    "kurang akurat."
                    + (f" Penyebab terakhir: {reason}." if reason else "")
                    + " Coba tekan **Buat Rute Optimal** lagi, atau arahkan ke server OSRM sendiri lewat "
                    "pengaturan `OSRM_BASE_URL` di Secrets."
                )

            render_stepper(stepper_slot, 3)
            route_summaries = result["route_summaries"]
            st.success(f"🎉 Rute berhasil dibuat! {len(route_summaries)} rute siap dipakai.")

            total_distance = sum(r["distance_km"] for r in route_summaries)
            total_duration = sum(r["duration_sec"] for r in route_summaries)
            total_visit = sum(r.get("visit_sec", 0) for r in route_summaries)
            with st.container(key="grid4"):
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    metric_card("🧭", "Total Rute", len(route_summaries))
                with m2:
                    metric_card("📍", "Total Titik", result["total_points"])
                with m3:
                    metric_card("📏", "Estimasi Total Jarak", f"{total_distance:.1f} km")
                with m4:
                    metric_card(
                        "⏱️",
                        "Waktu Total (jalan + kunjungan)" if total_visit else "Estimasi Waktu Tempuh",
                        format_duration(total_duration + total_visit),
                    )

            if len(route_summaries) >= 2:
                section_header(
                    "🗺️", "Peta Semua Rute",
                    "Gambaran keseluruhan — nyalakan atau matikan tiap rute lewat kontrol di pojok kanan atas peta",
                )
                st_folium(
                    build_combined_map(route_summaries), width=None, height=COMBINED_MAP_H,
                    key="map_all", returned_objects=[],
                )

            section_header(
                "3️⃣", "Rute yang Sudah Dioptimalkan",
                "Klik tiap rute untuk lihat urutan kunjungan dan petanya",
            )
            first_route_id = route_summaries[0]["route_id"]
            for r in route_summaries:
                route_id = r["route_id"]
                optimized_df = r["df"]
                color = ROUTE_COLORS[route_id % len(ROUTE_COLORS)]
                emoji = ROUTE_EMOJIS[route_id % len(ROUTE_EMOJIS)]

                route_total_sec = r["duration_sec"] + r.get("visit_sec", 0)
                warn_mark = "" if r.get("real_roads", True) else " ⚠️ estimasi"
                manual_mark = " ✏️ manual" if r.get("manual") else ""
                with st.expander(
                    f"{emoji} Rute {route_id + 1} — {len(optimized_df)} titik — "
                    f"~{r['distance_km']:.1f} km — ~{format_duration(route_total_sec)}{warn_mark}{manual_mark}",
                    # tetap terbuka saat sedang diedit (judulnya berubah tiap urutan digeser)
                    expanded=(route_id == first_route_id) or bool(st.session_state.get(f"edit_{route_id}", False)),
                ):
                    parts = [f"🚗 Perjalanan {format_duration(r['duration_sec'])}"]
                    if r.get("visit_sec"):
                        parts.append(f"🏪 Kunjungan {format_duration(r['visit_sec'])}")
                    if r.get("finish_label"):
                        parts.append(
                            f"🏁 Selesai ±{r['finish_label']}"
                            + (" (sudah termasuk pulang)" if r.get("round_trip") else "")
                        )
                    if r.get("depot_name"):
                        parts.append(f"🏭 Titik awal: {r['depot_name']}")
                    st.caption(" · ".join(parts))
                    if r.get("n_outside_hours"):
                        st.warning(
                            f"⚠️ {r['n_outside_hours']} merchant diperkirakan dikunjungi di luar jam "
                            "operasional (lihat kolom status di tabel / Catatan di PDF)."
                        )

                    driver_val = st.text_input(
                        "🧑‍✈️ Nama kurir/sopir (opsional)",
                        value=st.session_state.driver_names.get(route_id, ""),
                        key=f"driver_{route_id}",
                        placeholder="Mis. Budi",
                    )
                    st.session_state.driver_names[route_id] = driver_val
                    r["driver"] = driver_val

                    left, right = st.columns([1, 1.4])
                    with left:
                        _display_cols = ["sequence", "merchant_name"]
                        _display_cols += [c for c in ("jam_tiba", "jam_selesai") if c in optimized_df.columns]
                        _show_df = optimized_df[_display_cols + ["latitude", "longitude"]].copy()
                        if "prioritas_flag" in optimized_df.columns:
                            _show_df.insert(2, "⭐ Prioritas", optimized_df["prioritas_flag"].map({True: "⭐", False: ""}))
                        if "jadwal_status" in optimized_df.columns:
                            _show_df["Status Jam"] = optimized_df["jadwal_status"]
                        st.dataframe(
                            _show_df,
                            width='stretch',
                            **TABLE_KW,
                            hide_index=True,
                        )
                        if st.checkbox("✏️ Ubah urutan manual", key=f"edit_{route_id}",
                                       help="Geser merchant naik/turun, misalnya karena toko tutup jam tertentu atau ada janji. "
                                            "Jarak, jam tiba, peta, Excel, WhatsApp, dan PDF ikut diperbarui."):
                            render_reorder_controls(r)
                        map_links, seq_nums, link_df = route_links_info(r, MAPS_MAX_WAYPOINTS_DESKTOP)
                        # Batas 9 titik singgah berlaku untuk aplikasi Google Maps (Android/iOS)
                        # MAUPUN desktop — dan tap link di HP hampir selalu membuka aplikasi
                        # tersebut (deep-link), bukan browser HP. Batas 3 titik singgah menurut
                        # Google hanya berlaku kalau link dibuka di BROWSER HP secara spesifik,
                        # jadi kita pakai 9 sebagai default supaya tidak kepecah link-nya tanpa
                        # alasan untuk kasus paling umum, dan cukup beri catatan untuk skenario
                        # browser-HP yang lebih jarang terjadi.
                        max_wp = MAPS_MAX_WAYPOINTS_DESKTOP
                        link_waypoints = max(0, len(link_df) - 2)
                        if len(map_links) == 1:
                            st.link_button("🚗 Buka di Google Maps", map_links[0][2], width='stretch')
                            if IS_MOBILE and link_waypoints > MAPS_MAX_WAYPOINTS_MOBILE:
                                st.caption(
                                    "ℹ️ Kalau link ini dibuka di **browser HP** (bukan aplikasi Google "
                                    f"Maps), Google Maps mungkin hanya menampilkan {MAPS_MAX_WAYPOINTS_MOBILE} "
                                    "titik singgah pertama. Buka lewat aplikasi Google Maps untuk rute lengkap."
                                )
                        elif len(map_links) > 1:
                            st.caption(
                                f"ℹ️ Google Maps membatasi titik singgah (maks. {max_wp} per link), "
                                f"jadi rute dibagi jadi {len(map_links)} link. Buka berurutan — "
                                "tiap bagian dimulai dari titik akhir bagian sebelumnya."
                            )
                            for i, (ia, ib, url) in enumerate(map_links, start=1):
                                st.link_button(
                                    f"🚗 Bagian {i}/{len(map_links)} · titik {seq_nums[ia]} → {seq_nums[ib]}",
                                    url,
                                    width='stretch',
                                )

                        wa_text = build_whatsapp_text(r, map_links)
                        wa_url = "https://wa.me/?text=" + quote(wa_text, safe="")
                        if len(wa_url) <= 3800:
                            st.link_button("📲 Kirim via WhatsApp", wa_url, width='stretch')
                        else:
                            st.caption(
                                "ℹ️ Teks rute terlalu panjang untuk tombol langsung — "
                                "salin lewat tombol di bawah lalu tempel di WhatsApp."
                            )
                        with st.popover("📋 Salin teks rute"):
                            st.code(wa_text, language=None)
                        if PDF_OK:
                            st.download_button(
                                "🖨️ Unduh PDF (siap cetak)",
                                data=_routes_pdf_cached([_pdf_payload(r, map_links, seq_nums, result)]),
                                file_name=f"lembar_rute_{route_id + 1}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{route_id}",
                                width='stretch',
                            )

                    with right:
                        center_lat = optimized_df["latitude"].mean()
                        center_lon = optimized_df["longitude"].mean()
                        fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12)
                        polyline_coords = []
                        for idx, row in optimized_df.iterrows():
                            coord = [row["latitude"], row["longitude"]]
                            polyline_coords.append(coord)
                            is_start_pt = bool(r.get("has_start")) and idx == 0
                            folium.Marker(
                                coord,
                                popup=f"{idx + 1}. {row['merchant_name']}",
                                tooltip=f"{'Titik awal' if is_start_pt else idx + 1} · {row['merchant_name']}",
                                icon=numbered_icon("S" if is_start_pt else idx + 1, color, is_start_pt),
                            ).add_to(fmap)
                        if r.get("round_trip") and polyline_coords:
                            polyline_coords.append(polyline_coords[0])
                        folium.PolyLine(polyline_coords, weight=4, color=color).add_to(fmap)
                        st_folium(fmap, width=None, height=MAP_H, key=f"map_{route_id}", returned_objects=[])

            section_header(
                "📥", "Unduh Hasil",
                "Excel berisi semua rute per-sheet, dan PDF siap cetak untuk dibawa kurir",
            )
            dl1, dl2 = st.columns(2)
            with dl1:
                # Dibangun ulang di sini (bukan pakai result["excel_bytes"] yang
                # dicache saat generate) supaya nama kurir yang baru diisi ikut
                # terbawa — kolom "kurir" dibaca langsung dari r["driver"].
                st.download_button(
                    label="📥 Excel (semua rute)",
                    data=build_excel_bytes(route_summaries),
                    file_name="hasil_routing.xlsx",
                    mime="application/vnd.ms-excel",
                    type="primary",
                    width='stretch',
                )
            with dl2:
                if PDF_OK:
                    all_payloads = []
                    for _r in route_summaries:
                        _links, _seq, _ = route_links_info(_r, MAPS_MAX_WAYPOINTS_DESKTOP)
                        all_payloads.append(_pdf_payload(_r, _links, _seq, result))
                    st.download_button(
                        label="🖨️ PDF semua rute (1 rute/halaman)",
                        data=_routes_pdf_cached(all_payloads),
                        file_name="lembar_rute_semua.pdf",
                        mime="application/pdf",
                        width='stretch',
                    )
                else:
                    st.caption("PDF belum tersedia: pustaka `reportlab` belum terpasang di server.")
        elif result and result["fingerprint"] != data_fingerprint:
            st.info("ℹ️ Pengaturan atau data berubah — tekan **Buat Rute Optimal Sekarang** lagi untuk memperbarui hasil.")
    else:
        empty_state(
            "📂",
            "Belum ada data untuk diproses",
            "Upload file Excel/CSV di atas, atau centang opsi data dari Maps Extractor untuk mulai membuat rute optimal.",
        )

# ================================================================
# HALAMAN 2: GOOGLE MAPS EXTRACTOR
# ================================================================
elif st.session_state.page == "Extract":
    st.markdown(
        """
        <div class="hero-header">
            <h1>📍 Google Maps Extractor</h1>
            <p>Ubah link Google Maps, pencarian nama merchant, atau input manual jadi tabel (merchant_name, latitude, longitude) siap pakai.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_link, tab_search, tab_manual = st.tabs(
        ["🔗 Link", "🔎 Cari", "✏️ Manual"] if IS_MOBILE
        else ["🔗 Dari Link Google Maps", "🔎 Cari Nama Merchant", "✏️ Input Manual"]
    )

    with tab_link:
        with st.form("extractor_form", clear_on_submit=True):
            new_link = st.text_input("Paste link Google Maps di sini:")
            submitted = st.form_submit_button("➕ Ekstrak & Tambahkan Data", type="primary", width='stretch')

            if submitted:
                if not new_link.strip():
                    st.error("❌ Link tidak boleh kosong.")
                else:
                    with st.spinner("Membaca link..."):
                        name, lat, lon = extract_google_maps_data(new_link)

                    if lat is not None and lon is not None:
                        # Give every entry with an unrecognized name a unique
                        # placeholder — never reuse one fixed label, or every
                        # unparsed entry ends up looking like the same
                        # "duplicate" merchant on the map.
                        if not name:
                            name = f"Lokasi {len(st.session_state.extracted_data) + 1}"
                            st.warning(
                                f"Nama merchant tidak terdeteksi dari link — diberi nama sementara "
                                f"**{name}**. Silakan edit di tabel di bawah."
                            )

                        is_duplicate = any(
                            abs(d["latitude"] - lat) < 1e-5 and abs(d["longitude"] - lon) < 1e-5
                            for d in st.session_state.extracted_data
                        )

                        st.session_state.extracted_data.append(
                            {"merchant_name": name, "latitude": float(lat), "longitude": float(lon)}
                        )
                        st.success(f"✅ Berhasil menambahkan: {name}")
                        if is_duplicate:
                            st.warning(
                                "⚠️ Koordinat ini sama persis dengan data lain yang sudah ada — "
                                "periksa apakah link-nya benar-benar berbeda."
                            )
                    else:
                        st.error(
                            "❌ Gagal mendeteksi koordinat dari link tersebut. Pastikan link berasal "
                            "dari halaman detail lokasi di Google Maps (bukan link pencarian), lalu "
                            "gunakan tombol **Bagikan → Salin link**."
                        )

    with tab_search:
        st.info(
            "Pencarian gratis via OpenStreetMap — tanpa API key, tapi cakupan merchant kecil/UMKM "
            "di Indonesia masih lebih terbatas dibanding Google Maps. Sertakan kota/wilayah supaya "
            "hasilnya lebih akurat.",
            icon="💡",
        )
        sc1, sc2 = st.columns([2, 1])
        with sc1:
            search_query = st.text_input(
                "Nama merchant", key="nominatim_query", placeholder="contoh: Warung Bu Tini"
            )
        with sc2:
            search_city = st.text_input(
                "Kota/wilayah (opsional)", key="nominatim_city", placeholder="contoh: Surakarta"
            )

        if st.button("🔍 Cari Lokasi", type="primary", width='stretch'):
            if not search_query.strip():
                st.error("❌ Nama merchant tidak boleh kosong.")
            else:
                full_query = (
                    f"{search_query.strip()}, {search_city.strip()}"
                    if search_city.strip()
                    else search_query.strip()
                )
                with st.spinner("Mencari di OpenStreetMap..."):
                    results, search_error = search_nominatim(full_query)
                st.session_state.nominatim_results = results
                st.session_state.nominatim_searched_for = full_query
                st.session_state.nominatim_query_name = search_query.strip()
                st.session_state.pop("nominatim_selected_idx", None)
                if search_error:
                    st.error(f"⚠️ {search_error}")
                elif not results:
                    st.warning(
                        "Tidak ditemukan hasil. Coba nama yang lebih spesifik, tambahkan "
                        "kota/wilayah, atau gunakan tab **Dari Link Google Maps** sebagai alternatif "
                        "yang cakupannya lebih luas."
                    )

        results = st.session_state.get("nominatim_results", [])
        if results:
            st.markdown(
                f"**🔎 Ditemukan {len(results)} hasil untuk:** _{st.session_state.get('nominatim_searched_for', '')}_"
            )
            idx_selected = st.radio(
                "Pilih lokasi yang paling sesuai:",
                options=list(range(len(results))),
                format_func=lambda i: results[i].get("display_name", "(tanpa nama)"),
                key="nominatim_selected_idx",
            )

            if st.button("➕ Tambahkan Lokasi Terpilih", type="primary", width='stretch'):
                chosen = results[idx_selected]
                try:
                    lat = float(chosen["lat"])
                    lon = float(chosen["lon"])
                except (KeyError, ValueError, TypeError):
                    st.error("❌ Data koordinat dari hasil pencarian tidak valid.")
                else:
                    name = nominatim_result_name(
                        chosen, fallback_query=st.session_state.get("nominatim_query_name", "")
                    )
                    is_duplicate = any(
                        abs(d["latitude"] - lat) < 1e-5 and abs(d["longitude"] - lon) < 1e-5
                        for d in st.session_state.extracted_data
                    )
                    st.session_state.extracted_data.append(
                        {"merchant_name": name, "latitude": lat, "longitude": lon}
                    )
                    st.success(f"✅ Berhasil menambahkan: {name}")
                    if is_duplicate:
                        st.warning(
                            "⚠️ Koordinat ini sama persis dengan data lain yang sudah ada — "
                            "periksa apakah lokasinya benar-benar berbeda."
                        )

    with tab_manual:
        with st.form("manual_form", clear_on_submit=True):
            manual_name = st.text_input("Nama merchant", placeholder="contoh: Toko Berkah")
            manual_coord = st.text_input(
                "📋 Tempel koordinat",
                placeholder="-7.5665, 110.8167",
                help=(
                    "Di Google Maps: klik kanan (atau tekan lama di HP) pada lokasi, lalu klik/sentuh angka "
                    "koordinat di bagian atas menu untuk menyalinnya, dan tempel di sini."
                ),
            )
            with st.expander("Atau isi latitude & longitude secara terpisah"):
                mc2, mc3 = st.columns(2)
                with mc2:
                    manual_lat = st.number_input(
                        "Latitude", value=0.0, format="%.6f",
                        help="Gunakan titik desimal, contoh: -7.5665",
                    )
                with mc3:
                    manual_lon = st.number_input(
                        "Longitude", value=0.0, format="%.6f",
                        help="Gunakan titik desimal, contoh: 110.8167",
                    )
            manual_submit = st.form_submit_button("➕ Tambahkan Data", type="primary", width='stretch')

            if manual_submit:
                lat = lon = None
                if not manual_name.strip():
                    st.error("❌ Nama merchant tidak boleh kosong.")
                elif manual_coord.strip():
                    lat, lon, coord_err = parse_coordinate_text(manual_coord)
                    if coord_err:
                        st.error(f"❌ {coord_err}")
                elif manual_lat == 0.0 and manual_lon == 0.0:
                    st.error("❌ Isi koordinat: tempel di kolom koordinat, atau isi latitude & longitude.")
                else:
                    lat, lon = manual_lat, manual_lon

                if lat is not None and lon is not None:
                    st.session_state.extracted_data.append(
                        {"merchant_name": manual_name.strip(), "latitude": float(lat), "longitude": float(lon)}
                    )
                    st.success(f"✅ Berhasil menambahkan: {manual_name.strip()}")

    if len(st.session_state.extracted_data) > 0:
        section_header(
            "📋", "Data yang Sudah Dikumpulkan",
            f"{len(st.session_state.extracted_data)} lokasi — klik dua kali sel untuk edit, atau hapus baris yang tidak perlu",
        )

        df_extract = pd.DataFrame(st.session_state.extracted_data)
        edited_df = st.data_editor(
            df_extract,
            width='stretch',
            num_rows="dynamic",
            **TABLE_KW,
            key="extract_editor",
            column_config={
                "latitude": st.column_config.NumberColumn(format="%.6f"),
                "longitude": st.column_config.NumberColumn(format="%.6f"),
            },
        )
        st.session_state.extracted_data = edited_df.to_dict("records")

        with st.expander("🗺️ Lihat lokasi di peta"):
            valid_points = edited_df.dropna(subset=["latitude", "longitude"])
            if not valid_points.empty:
                fmap = folium.Map(
                    location=[valid_points["latitude"].mean(), valid_points["longitude"].mean()],
                    zoom_start=12,
                )
                for _, row in valid_points.iterrows():
                    folium.Marker([row["latitude"], row["longitude"]], popup=row["merchant_name"]).add_to(fmap)
                st_folium(fmap, width=None, height=MAP_H, key="extract_map", returned_objects=[])

        col1, col2, col3 = st.columns([1, 1, 1.3])
        with col1:
            if st.button("🗑️ Hapus Semua", width='stretch'):
                st.session_state.extracted_data = []
                st.rerun()
        with col2:
            buffer_ext = io.BytesIO()
            with pd.ExcelWriter(buffer_ext, engine="openpyxl") as writer:
                edited_df.to_excel(writer, index=False)
            st.download_button(
                label="📥 Download Excel",
                data=buffer_ext.getvalue(),
                file_name="hasil_extract_gmaps.xlsx",
                mime="application/vnd.ms-excel",
                width='stretch',
            )
        with col3:
            if st.button("➡️ Pakai di Routing Optimizer", type="primary", width='stretch'):
                st.session_state.use_extracted_flag = True
                st.session_state.page = "Routing"
                st.rerun()
    else:
        empty_state(
            "🗺️",
            "Belum ada lokasi yang dikumpulkan",
            "Tempel link Google Maps, cari nama merchant, atau isi manual lewat tab di atas untuk mulai mengumpulkan data.",
        )


render_footer()
