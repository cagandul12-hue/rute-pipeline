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
from urllib.parse import unquote, quote
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
    "#e6194B", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#800000", "#aaffc3", "#000075",
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
    best used with a specific name plus a city/area hint."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": limit,
        "countrycodes": "id",
    }
    # Nominatim's usage policy requires a real identifying User-Agent.
    headers = {"User-Agent": "RutePipelineOptimizerApp/1.0 (streamlit-community-app)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return []


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
        if str(c).strip().lower() in REQUIRED_COLS and c != str(c).strip().lower()
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
    if r.get("finish_label"):
        lines.append(f"🏁 Estimasi selesai ±{r['finish_label']}")
    lines.append("")
    for _, row in df.iterrows():
        eta = f" ({row['jam_tiba']})" if "jam_tiba" in df.columns else ""
        lines.append(f"{int(row['sequence'])}. {row['merchant_name']}{eta}")
    if r.get("round_trip"):
        lines.append("↩️ Lalu kembali ke titik awal")
    lines.append("")
    if len(map_links) == 1:
        lines.append(f"🗺️ Google Maps: {map_links[0][2]}")
    else:
        for i, (_, _, url) in enumerate(map_links, start=1):
            lines.append(f"🗺️ Google Maps bagian {i}: {url}")
    return "\n".join(lines)


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
[class*="st-key-filerow"] [data-testid="stHorizontalBlock"] {
    flex-direction: row !important; flex-wrap: nowrap !important; gap: 0.5rem !important;
}
.st-key-navrow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-moderow [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
.st-key-navrow [data-testid="stHorizontalBlock"] > [data-testid="column"],
.st-key-moderow [data-testid="stHorizontalBlock"] > [data-testid="column"] {
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
    st.session_state.round_trip_flag = st.session_state._round_trip_widget


def _sync_dedupe():
    st.session_state.dedupe_flag = st.session_state._dedupe_widget


def _sync_use_extracted():
    st.session_state.use_extracted_flag = st.session_state._use_extracted_widget


def _sync_starting_link():
    st.session_state.starting_link_saved = st.session_state._starting_link_widget


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
    st.session_state.plan_mode_flag = st.session_state._plan_widget


def _sync_target():
    st.session_state.target_routes_flag = int(st.session_state._target_widget)


def _sync_visit():
    st.session_state.visit_minutes_flag = int(st.session_state._visit_widget)


def _sync_start_time():
    st.session_state.start_time_flag = st.session_state._start_time_widget


# ---------- Simpan / buka sesi ----------
MAX_SESSION_BYTES = 40 * 1024 * 1024
SESSION_WIDGET_KEYS = (
    "_use_extracted_widget", "_starting_link_widget", "_round_trip_widget", "_dedupe_widget",
    "_split_widget", "_plan_widget", "_target_widget", "_visit_widget", "_start_time_widget",
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

    ss = st.session_state
    ss.uploaded_store = files
    ss.extracted_data = extracted
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
            "Lihat urutan kunjungan dan perkiraan jam tiba, buka di Google Maps, kirim ke WhatsApp, "
            "atau unduh semua rute sebagai Excel.\n\n"
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
            help="Format .xlsx atau .csv. Kolom wajib: merchant_name, latitude, longitude (koma desimal seperti -7,56 juga dikenali). Bisa pilih beberapa file sekaligus — nanti otomatis digabung. File yang sudah diupload tetap tersimpan walau kamu pindah ke Maps Extractor.",
        )
        if new_files:
            for nf in new_files:
                st.session_state.uploaded_store[nf.name] = nf.getvalue()
            st.session_state.uploader_nonce += 1
            st.rerun()

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

                all_routes = []
                route_summaries = []
                any_fallback_used = False
                osrm_errors = []
                base_date = datetime.date.today()
                start_dt = datetime.datetime.combine(base_date, start_time)
                visit_sec = int(visit_minutes) * 60
                for route_id in sorted(df["route"].unique()):
                    route_df = df[df["route"] == route_id].reset_index(drop=True)

                    if start_lat and start_lon:
                        start_df = pd.DataFrame(
                            [{"merchant_name": start_name, "latitude": start_lat, "longitude": start_lon}]
                        )
                        route_df = pd.concat([start_df, route_df], ignore_index=True)

                    distance_matrix, duration_matrix, used_real_roads, osrm_error = get_route_matrices(route_df)
                    any_fallback_used = any_fallback_used or not used_real_roads
                    if osrm_error:
                        osrm_errors.append(osrm_error)

                    has_start = bool(start_lat and start_lon)
                    best_route = solve_tsp(distance_matrix, round_trip=round_trip, fixed_start=has_start)
                    optimized_df = route_df.iloc[best_route].reset_index(drop=True)
                    optimized_df["sequence"] = optimized_df.index + 1
                    optimized_df["route_name"] = f"Rute {route_id + 1}"

                    arrivals, departs, back_dt, finish_dt = build_schedule(
                        duration_matrix, best_route, start_dt, visit_sec, has_start, round_trip
                    )
                    optimized_df["jam_tiba"] = [_clock(t, base_date) for t in arrivals]
                    if visit_sec:
                        optimized_df["jam_selesai"] = [_clock(t, base_date) for t in departs]
                    n_visits = len(best_route) - (1 if has_start else 0)
                    all_routes.append(optimized_df)

                    route_distance_km = route_leg_sum(distance_matrix, best_route, round_trip) / 1000
                    route_duration_sec = route_leg_sum(duration_matrix, best_route, round_trip)

                    route_summaries.append(
                        {
                            "route_id": route_id,
                            "df": optimized_df,
                            "distance_km": route_distance_km,
                            "duration_sec": route_duration_sec,
                            "visit_sec": visit_sec * n_visits,
                            "finish_label": _clock(finish_dt, base_date),
                            "real_roads": used_real_roads,
                            "round_trip": round_trip,
                        }
                    )

            final_df = pd.concat([r["df"] for r in route_summaries], ignore_index=True)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                final_df.to_excel(writer, index=False, sheet_name="Semua Rute")
                for r in route_summaries:
                    sheet_name = f"Rute {r['route_id'] + 1}"[:31]
                    r["df"].to_excel(writer, index=False, sheet_name=sheet_name)

            # Persist everything needed to render the result, so later reruns
            # (e.g. clicking the map or the download button) don't wipe it out.
            st.session_state.route_result = {
                "fingerprint": data_fingerprint,
                "route_summaries": route_summaries,
                "total_points": len(df) + (1 if start_lat and start_lon else 0) * len(route_summaries),
                "excel_bytes": buffer.getvalue(),
                "start_ok": bool(start_lat and start_lon),
                "start_link_given": bool(starting_link),
                "used_real_roads": not any_fallback_used,
                "osrm_error": osrm_errors[-1] if osrm_errors else None,
            }

        result = st.session_state.get("route_result")
        if result and result["fingerprint"] == data_fingerprint:
            if result["start_link_given"] and not result["start_ok"]:
                st.warning("⚠️ Titik awal tidak dikenali (bukan link Google Maps atau koordinat yang valid), jadi dilewati — rute tetap dibuat tanpa titik awal khusus.")

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
                with st.expander(
                    f"{emoji} Rute {route_id + 1} — {len(optimized_df)} titik — "
                    f"~{r['distance_km']:.1f} km — ~{format_duration(route_total_sec)}{warn_mark}",
                    expanded=(route_id == first_route_id),
                ):
                    parts = [f"🚗 Perjalanan {format_duration(r['duration_sec'])}"]
                    if r.get("visit_sec"):
                        parts.append(f"🏪 Kunjungan {format_duration(r['visit_sec'])}")
                    if r.get("finish_label"):
                        parts.append(
                            f"🏁 Selesai ±{r['finish_label']}"
                            + (" (sudah termasuk pulang)" if r.get("round_trip") else "")
                        )
                    st.caption(" · ".join(parts))
                    left, right = st.columns([1, 1.4])
                    with left:
                        st.dataframe(
                            optimized_df[
                                ["sequence", "merchant_name"]
                                + [c for c in ("jam_tiba", "jam_selesai") if c in optimized_df.columns]
                                + ["latitude", "longitude"]
                            ],
                            width='stretch',
                            **TABLE_KW,
                            hide_index=True,
                        )
                        is_round = bool(r.get("round_trip"))
                        link_df = (
                            pd.concat([optimized_df, optimized_df.iloc[[0]]], ignore_index=True)
                            if is_round else optimized_df
                        )
                        seq_nums = list(optimized_df["sequence"]) + (
                            [optimized_df["sequence"].iloc[0]] if is_round else []
                        )
                        # Batas 9 titik singgah berlaku untuk aplikasi Google Maps (Android/iOS)
                        # MAUPUN desktop — dan tap link di HP hampir selalu membuka aplikasi
                        # tersebut (deep-link), bukan browser HP. Batas 3 titik singgah menurut
                        # Google hanya berlaku kalau link dibuka di BROWSER HP secara spesifik,
                        # jadi kita pakai 9 sebagai default supaya tidak kepecah link-nya tanpa
                        # alasan untuk kasus paling umum, dan cukup beri catatan untuk skenario
                        # browser-HP yang lebih jarang terjadi.
                        max_wp = MAPS_MAX_WAYPOINTS_DESKTOP
                        map_links = generate_google_maps_links(link_df, max_wp)
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

                    with right:
                        center_lat = optimized_df["latitude"].mean()
                        center_lon = optimized_df["longitude"].mean()
                        fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12)
                        polyline_coords = []
                        for idx, row in optimized_df.iterrows():
                            coord = [row["latitude"], row["longitude"]]
                            polyline_coords.append(coord)
                            folium.Marker(
                                coord,
                                popup=f"{idx + 1}. {row['merchant_name']}",
                                icon=folium.Icon(color="blue" if idx > 0 else "green"),
                            ).add_to(fmap)
                        if r.get("round_trip") and polyline_coords:
                            polyline_coords.append(polyline_coords[0])
                        folium.PolyLine(polyline_coords, weight=4, color=color).add_to(fmap)
                        st_folium(fmap, width=None, height=MAP_H, key=f"map_{route_id}", returned_objects=[])

            section_header("📥", "Unduh Hasil", "Satu file Excel berisi semua rute, rapi per-sheet")
            st.download_button(
                label="📥 Download Hasil Routing (Excel)",
                data=result["excel_bytes"],
                file_name="hasil_routing.xlsx",
                mime="application/vnd.ms-excel",
                type="primary",
                width='stretch',
            )
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
                    results = search_nominatim(full_query)
                st.session_state.nominatim_results = results
                st.session_state.nominatim_searched_for = full_query
                st.session_state.nominatim_query_name = search_query.strip()
                st.session_state.pop("nominatim_selected_idx", None)
                if not results:
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
                    name = st.session_state.get("nominatim_query_name") or chosen.get(
                        "display_name", "Lokasi"
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
