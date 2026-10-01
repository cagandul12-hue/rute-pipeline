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
from urllib.parse import unquote
from sklearn.cluster import KMeans
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Routing & Extractor System",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================================
# STYLING
# ==========================================================================================
ACCENT_GRADIENT = "linear-gradient(135deg, #4F46E5 0%, #0EA5E9 100%)"

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
        background: linear-gradient(135deg, #4F46E5 0%, #0EA5E9 100%);
        border-radius: 18px;
        padding: 26px 32px;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(79,70,229,0.28);
    }
    .hero-header h1 {
        color: #ffffff !important;
        margin: 0 !important;
        font-size: 1.7rem;
        font-weight: 800;
        line-height: 1.3;
    }
    .hero-header p {
        color: rgba(255,255,255,0.92) !important;
        margin: 6px 0 0 0 !important;
        font-size: 0.95rem;
    }

    /* ---------- Metric cards ---------- */
    .metric-card {
        background: rgba(128,128,128,0.08);
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 14px;
        padding: 16px 18px;
        height: 100%;
    }
    .metric-card .metric-icon {font-size: 1.4rem; line-height: 1;}
    .metric-card .metric-label {
        font-size: 0.78rem; opacity: 0.7; margin-top: 8px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.03em;
    }
    .metric-card .metric-value {font-size: 1.5rem; font-weight: 800; margin-top: 2px;}

    /* ---------- Sidebar ---------- */
    .sidebar-brand {display: flex; align-items: center; gap: 10px;}
    .sidebar-brand .emoji {font-size: 1.9rem; line-height: 1;}
    .sidebar-brand .title {font-weight: 800; font-size: 1.08rem; line-height: 1.2;}
    .sidebar-brand .subtitle {font-size: 0.78rem; opacity: 0.65;}
    section[data-testid="stSidebar"] button {border-radius: 10px !important;}

    /* ---------- Buttons ---------- */
    .stButton > button, .stDownloadButton > button, .stLinkButton > a {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #0EA5E9 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(79,70,229,0.32);
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
        background: linear-gradient(135deg, #4F46E5 0%, #0EA5E9 100%);
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
    }
    .section-header .title {font-weight: 800; font-size: 1.08rem; line-height: 1.3;}
    .section-header .subtitle {font-size: 0.82rem; opacity: 0.65; margin-top: 1px;}

    /* ---------- Empty state ---------- */
    .empty-state {
        border: 1.5px dashed rgba(128,128,128,0.35);
        border-radius: 16px;
        padding: 36px 24px;
        text-align: center;
        background: rgba(128,128,128,0.04);
        margin-top: 8px;
    }
    .empty-state .emoji {font-size: 2.3rem;}
    .empty-state .title {font-weight: 700; font-size: 1.05rem; margin-top: 12px;}
    .empty-state .desc {
        font-size: 0.86rem; opacity: 0.7; margin-top: 4px;
        max-width: 440px; margin-left: auto; margin-right: auto; line-height: 1.5;
    }

    div[data-testid="stSidebarNav"] {display: none;}
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


OSRM_BASE_URL = "https://router.project-osrm.org"
FALLBACK_SPEED_KMH = 30  # used only if OSRM is unreachable


def get_route_matrices(df):
    """Returns (distance_matrix_meters, duration_matrix_seconds, used_real_roads).

    Tries OSRM's public routing service first, which follows the actual
    road network (one-ways, detours, etc.) instead of a straight line — so
    both the TSP ordering and the reported distance/time reflect real
    driving conditions. Falls back to haversine straight-line distance
    with an assumed average speed if OSRM is unreachable, rate-limited, or
    the request fails for any other reason.
    """
    n = len(df)
    if n < 2:
        return [[0]], [[0]], True

    try:
        coords = ";".join(f"{row.longitude},{row.latitude}" for _, row in df.iterrows())
        url = f"{OSRM_BASE_URL}/table/v1/driving/{coords}"
        resp = requests.get(url, params={"annotations": "distance,duration"}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != "Ok":
            raise ValueError(data.get("message", "OSRM returned an error"))

        raw_distances = data["distances"]
        raw_durations = data["durations"]
        # OSRM can return null for a pair it couldn't route between; treat
        # that as "very far" so the TSP solver avoids it rather than crashing.
        distance_matrix = [
            [int(raw_distances[i][j]) if raw_distances[i][j] is not None else 10_000_000 for j in range(n)]
            for i in range(n)
        ]
        duration_matrix = [
            [raw_durations[i][j] if raw_durations[i][j] is not None else 0 for j in range(n)]
            for i in range(n)
        ]
        return distance_matrix, duration_matrix, True
    except Exception:
        distance_matrix = create_distance_matrix(df)
        duration_matrix = [
            [
                (distance_matrix[i][j] / 1000) / FALLBACK_SPEED_KMH * 3600 if i != j else 0
                for j in range(n)
            ]
            for i in range(n)
        ]
        return distance_matrix, duration_matrix, False


def format_duration(seconds):
    if seconds is None:
        return "–"
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes} menit"
    hours, rem = divmod(minutes, 60)
    return f"{hours} jam {rem} menit" if rem else f"{hours} jam"


def solve_tsp(distance_matrix):
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.time_limit.seconds = 5
    solution = routing.SolveWithParameters(search_parameters)

    if solution is None:
        return list(range(len(distance_matrix)))

    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route.append(node)
        index = solution.Value(routing.NextVar(index))
    return route


def generate_google_maps_link(df):
    coords = [f"{row.latitude},{row.longitude}" for _, row in df.iterrows()]
    if len(coords) < 2:
        return None
    origin = coords[0]
    destination = coords[-1]
    waypoints = "%7C".join(coords[1:-1])
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    if waypoints:
        url += f"&waypoints={waypoints}"
    url += "&travelmode=driving"
    return url


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
    while True:
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


def validate_dataframe(df):
    """Returns (is_valid, list_of_error_messages)."""
    errors = []
    required_cols = ["merchant_name", "latitude", "longitude"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        errors.append(f"Kolom wajib hilang: {', '.join(missing)}")
        return False, errors

    if df.empty:
        errors.append("File Excel tidak berisi data.")
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


def make_template_excel():
    template_df = pd.DataFrame(
        {
            "merchant_name": ["Toko A", "Toko B", "Toko C"],
            "latitude": [-7.5665, -7.5700, -7.5610],
            "longitude": [110.8167, 110.8200, 110.8100],
        }
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        template_df.to_excel(writer, index=False)
    return buf.getvalue()


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


def _sync_use_extracted():
    st.session_state.use_extracted_flag = st.session_state._use_extracted_widget


def _sync_starting_link():
    st.session_state.starting_link_saved = st.session_state._starting_link_widget

# ==========================================================================================
# SIDEBAR NAVIGATION
# ==========================================================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <span class="emoji">🏎️</span>
            <div>
                <div class="title">Routing &amp; Extractor</div>
                <div class="subtitle">Rute otomatis, lebih singkat & rapi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Plain buttons (not a key-bound widget) so the active page can be set
    # programmatically from anywhere — e.g. the "pakai di Routing Optimizer"
    # button on the Extract page — without hitting Streamlit's restriction
    # on mutating a widget's own session-state key after it's been created.
    nav_routing_active = st.session_state.page == "Routing"
    nav_extract_active = st.session_state.page == "Extract"

    if st.button(
        "🛣️  Routing Optimizer",
        width='stretch',
        type="primary" if nav_routing_active else "secondary",
    ):
        st.session_state.page = "Routing"
        st.rerun()

    if st.button(
        "📍  Maps Extractor",
        width='stretch',
        type="primary" if nav_extract_active else "secondary",
    ):
        st.session_state.page = "Extract"
        st.rerun()

    st.markdown("---")
    with st.expander("ℹ️ Cara Pakai (3 Langkah)", expanded=False):
        st.write(
            "**1. Kumpulkan data** 📍\n"
            "Buka **Maps Extractor** — tempel link Google Maps, cari nama merchant, atau isi manual. "
            "Sudah punya file Excel? Langsung lompat ke langkah 2.\n\n"
            "**2. Buat rute** 🛣️\n"
            "Buka **Routing Optimizer**, upload Excel (`merchant_name`, `latitude`, `longitude`), "
            "atur maksimal titik per rute, lalu klik **Buat Rute Optimal**.\n\n"
            "**3. Unduh & pakai** 📥\n"
            "Lihat tiap rute di peta, buka langsung di Google Maps, atau unduh semuanya sebagai Excel."
        )


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

    section_header(
        "1️⃣", "Siapkan Data Merchant",
        "Upload file Excel, pakai data dari Maps Extractor, atau gabungan keduanya",
    )

    col_link, col_upload = st.columns([1, 1.3])
    with col_link:
        starting_link = st.text_input(
            "📍 Titik Awal (opsional)",
            value=st.session_state.starting_link_saved,
            key="_starting_link_widget",
            on_change=_sync_starting_link,
            placeholder="Tempel link Google Maps di sini",
            help="Misalnya lokasi gudang atau toko pusat. Kalau diisi, titik ini otomatis jadi awal setiap rute.",
        )
    with col_upload:
        new_files = st.file_uploader(
            "📂 Upload Data Excel",
            type=["xlsx"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_nonce}",
            help="Kolom wajib: merchant_name, latitude, longitude. Bisa pilih beberapa file sekaligus — nanti otomatis digabung. File yang sudah diupload tetap tersimpan walau kamu pindah ke Maps Extractor.",
        )
        if new_files:
            for nf in new_files:
                st.session_state.uploaded_store[nf.name] = nf.getvalue()
            st.session_state.uploader_nonce += 1
            st.rerun()

    # Daftar file yang tersimpan (tetap ada setelah pindah halaman)
    if st.session_state.uploaded_store:
        st.caption(f"📎 {len(st.session_state.uploaded_store)} file tersimpan")
        for fname in list(st.session_state.uploaded_store.keys()):
            fc1, fc2 = st.columns([6, 1])
            with fc1:
                st.markdown(f"📄 `{fname}`")
            with fc2:
                if st.button("✖", key=f"rm_{fname}", help=f"Hapus {fname}"):
                    st.session_state.uploaded_store.pop(fname, None)
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

    st.download_button(
        "⬇️ Download Template Excel",
        data=make_template_excel(),
        file_name="template_routing.xlsx",
        mime="application/vnd.ms-excel",
        help="Belum punya file? Download contoh formatnya di sini supaya langsung cocok.",
    )

    df = None
    valid_parts = []
    file_errors = []

    for fname, fbytes in st.session_state.uploaded_store.items():
        try:
            file_df = pd.read_excel(io.BytesIO(fbytes))
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
        df["latitude"] = pd.to_numeric(df["latitude"])
        df["longitude"] = pd.to_numeric(df["longitude"])

        with st.expander(f"📄 Lihat Data Awal ({len(df)} baris)", expanded=False):
            if "source_file" in df.columns:
                st.caption("💡 Kolom `source_file` menunjukkan file/sumber asal tiap baris setelah digabung.")
            st.dataframe(df, width='stretch')

        section_header(
            "2️⃣", "Atur Pembagian Rute",
            "Tentukan berapa banyak merchant maksimal dalam satu rute",
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            slider_max = max(2, len(df))
            if slider_max <= 2:
                # st.slider needs min_value < max_value; with only 2
                # merchants there's only one sensible route anyway.
                max_points_per_route = slider_max
                metric_card("📍", "Maksimal titik per route", max_points_per_route)
            else:
                max_points_per_route = st.slider(
                    "Maksimal titik per route", min_value=2, max_value=slider_max,
                    value=slider_max,
                    help="Default = total merchant, sehingga semua muat dalam 1 rute. Geser ke bawah untuk memecah jadi beberapa rute.",
                )
        n_cluster_default = math.ceil(len(df) / max_points_per_route)
        with c2:
            metric_card("🏪", "Total Merchant", len(df))
        with c3:
            metric_card("🧭", "Estimasi Jumlah Route", n_cluster_default)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        run = st.button("🚀 Buat Rute Optimal Sekarang", type="primary", width='stretch')

        # Fingerprint of the current input+settings, so stale results (from a
        # previous file/slider value) don't linger after the inputs change.
        data_fingerprint = (len(df), tuple(df["merchant_name"]), max_points_per_route, starting_link)

        if run:
            if len(df) < 2:
                st.warning("⚠️ Minimal butuh 2 titik untuk bisa membuat rute.")
                st.stop()

            with st.spinner("🔄 Mengelompokkan titik dan mencari rute tercepat di jalan asli..."):
                n_cluster = math.ceil(len(df) / max_points_per_route)
                n_cluster = max(1, min(n_cluster, len(df)))
                coords = df[["latitude", "longitude"]]
                kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=10)
                df["route"] = kmeans.fit_predict(coords)
                df = balance_clusters(df, max_points_per_route)

                start_name, start_lat, start_lon = "START POINT", None, None
                if starting_link:
                    parsed_name, start_lat, start_lon = extract_google_maps_data(starting_link)
                    start_name = parsed_name or "START POINT"

                all_routes = []
                route_summaries = []
                any_fallback_used = False
                for route_id in sorted(df["route"].unique()):
                    route_df = df[df["route"] == route_id].reset_index(drop=True)

                    if start_lat and start_lon:
                        start_df = pd.DataFrame(
                            [{"merchant_name": start_name, "latitude": start_lat, "longitude": start_lon}]
                        )
                        route_df = pd.concat([start_df, route_df], ignore_index=True)

                    distance_matrix, duration_matrix, used_real_roads = get_route_matrices(route_df)
                    any_fallback_used = any_fallback_used or not used_real_roads

                    best_route = solve_tsp(distance_matrix)
                    optimized_df = route_df.iloc[best_route].reset_index(drop=True)
                    optimized_df["sequence"] = optimized_df.index + 1
                    optimized_df["route_name"] = f"Route {route_id + 1}"
                    all_routes.append(optimized_df)

                    route_distance_km = sum(
                        distance_matrix[best_route[i]][best_route[i + 1]]
                        for i in range(len(best_route) - 1)
                    ) / 1000
                    route_duration_sec = sum(
                        duration_matrix[best_route[i]][best_route[i + 1]]
                        for i in range(len(best_route) - 1)
                    )

                    route_summaries.append(
                        {
                            "route_id": route_id,
                            "df": optimized_df,
                            "distance_km": route_distance_km,
                            "duration_sec": route_duration_sec,
                        }
                    )

            final_df = pd.concat([r["df"] for r in route_summaries], ignore_index=True)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                final_df.to_excel(writer, index=False, sheet_name="Semua Route")
                for r in route_summaries:
                    sheet_name = f"Route {r['route_id'] + 1}"[:31]
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
            }

        result = st.session_state.get("route_result")
        if result and result["fingerprint"] == data_fingerprint:
            if result["start_link_given"] and not result["start_ok"]:
                st.warning("⚠️ Link Google Maps titik awal tidak dikenali, jadi dilewati — rute tetap dibuat tanpa titik awal khusus.")

            if not result.get("used_real_roads", True):
                st.warning(
                    "⚠️ Tidak bisa terhubung ke layanan rute jalan asli (OSRM) — jarak & waktu tempuh "
                    "di bawah ini dihitung dari estimasi garis lurus, jadi bisa kurang akurat "
                    "dibanding kondisi jalan sebenarnya."
                )

            route_summaries = result["route_summaries"]
            st.success(f"🎉 Rute berhasil dibuat! {len(route_summaries)} rute siap dipakai.")

            total_distance = sum(r["distance_km"] for r in route_summaries)
            total_duration = sum(r["duration_sec"] for r in route_summaries)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                metric_card("🧭", "Total Route", len(route_summaries))
            with m2:
                metric_card("📍", "Total Titik", result["total_points"])
            with m3:
                metric_card("📏", "Estimasi Total Jarak", f"{total_distance:.1f} km")
            with m4:
                metric_card("⏱️", "Estimasi Waktu Tempuh", format_duration(total_duration))

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

                with st.expander(
                    f"{emoji} Route {route_id + 1} — {len(optimized_df)} titik — "
                    f"~{r['distance_km']:.1f} km — ~{format_duration(r['duration_sec'])}",
                    expanded=(route_id == first_route_id),
                ):
                    left, right = st.columns([1, 1.4])
                    with left:
                        st.dataframe(
                            optimized_df[["sequence", "merchant_name", "latitude", "longitude"]],
                            width='stretch',
                            hide_index=True,
                        )
                        maps_url = generate_google_maps_link(optimized_df)
                        if maps_url:
                            st.link_button("🚗 Buka di Google Maps", maps_url, width='stretch')

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
                        folium.PolyLine(polyline_coords, weight=4, color=color).add_to(fmap)
                        st_folium(fmap, width=None, height=350, key=f"map_{route_id}", returned_objects=[])

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
            "Upload file Excel di atas, atau centang opsi data dari Maps Extractor untuk mulai membuat rute optimal.",
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
        ["🔗 Dari Link Google Maps", "🔎 Cari Nama Merchant", "✏️ Input Manual"]
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
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                manual_name = st.text_input("Nama merchant", placeholder="contoh: Toko Berkah")
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
                if not manual_name.strip():
                    st.error("❌ Nama merchant tidak boleh kosong.")
                elif manual_lat == 0.0 and manual_lon == 0.0:
                    st.error("❌ Masukkan koordinat yang valid.")
                else:
                    st.session_state.extracted_data.append(
                        {"merchant_name": manual_name, "latitude": manual_lat, "longitude": manual_lon}
                    )
                    st.success(f"✅ Berhasil menambahkan: {manual_name}")

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
                st_folium(fmap, width=None, height=350, key="extract_map", returned_objects=[])

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
