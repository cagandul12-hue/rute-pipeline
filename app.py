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
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================================================
# STYLING
# ==========================================================================================
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    .metric-card {
        background: #ffffff10;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 14px 18px;
    }
    .route-card {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 16px;
    }
    .app-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }
    div[data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

ROUTE_COLORS = [
    "#e6194B", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
    "#42d4f4", "#f032e6", "#bfef45", "#fabed4", "#469990",
    "#dcbeff", "#9A6324", "#800000", "#aaffc3", "#000075",
]

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
    n = len(df)
    lat = df["latitude"].to_numpy()
    lon = df["longitude"].to_numpy()
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                matrix[i][j] = int(haversine(lat[i], lon[i], lat[j], lon[j]) * 1000)
    return matrix


def route_total_distance_km(df_ordered):
    total = 0.0
    for i in range(len(df_ordered) - 1):
        total += haversine(
            df_ordered.iloc[i]["latitude"], df_ordered.iloc[i]["longitude"],
            df_ordered.iloc[i + 1]["latitude"], df_ordered.iloc[i + 1]["longitude"],
        )
    return total


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
# A widget's own state (key="page") can only be set BEFORE that widget is
# instantiated in a given run — never after, even from a button lower down
# the same script. So a "switch page" request is staged here as a plain,
# non-widget flag and applied right now, before the sidebar radio below is
# created; the button just sets the flag and reruns.
if "pending_page" in st.session_state:
    st.session_state.page = st.session_state.pop("pending_page")
if "page" not in st.session_state:
    st.session_state.page = "Routing"
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = []
if "routing_df" not in st.session_state:
    st.session_state.routing_df = None

# ==========================================================================================
# SIDEBAR NAVIGATION
# ==========================================================================================
with st.sidebar:
    st.markdown("## 🚚 Routing & Extractor")
    st.caption("KMeans + TSP Engine")
    st.markdown("---")

    st.radio(
        "Menu",
        options=["Routing", "Extract"],
        format_func=lambda p: "🛣️ Routing Optimizer" if p == "Routing" else "📍 Maps Extractor",
        key="page",
        label_visibility="collapsed",
    )

    st.markdown("---")
    with st.expander("ℹ️ Cara pakai"):
        st.write(
            "1. Buka **Maps Extractor** untuk mengubah link Google Maps, hasil pencarian nama "
            "merchant, atau input manual jadi tabel koordinat — atau siapkan langsung file Excel.\n\n"
            "2. Buka **Routing Optimizer**, upload file Excel (`merchant_name`, `latitude`, `longitude`).\n\n"
            "3. Atur jumlah titik maksimal per rute, lalu lihat hasil rute optimal di peta."
        )


# ================================================================
# HALAMAN 1: ROUTING PIPELINE OPTIMIZER
# ================================================================
if st.session_state.page == "Routing":
    st.markdown(
        '<div class="app-header"><h1>🛣️ Routing Pipeline Optimizer</h1></div>',
        unsafe_allow_html=True,
    )
    st.caption("Optimalkan rute pengiriman dengan clustering (KMeans) dan penentuan urutan kunjungan (TSP).")

    col_link, col_upload = st.columns([1, 1.3])
    with col_link:
        starting_link = st.text_input(
            "📍 Link Google Maps Titik Awal (opsional)",
            placeholder="Tempel link Google Maps di sini",
            help="Jika diisi, titik ini akan dijadikan awal setiap rute.",
        )
    with col_upload:
        uploaded_files = st.file_uploader(
            "📂 Upload Excel (kolom: merchant_name, latitude, longitude) — bisa pilih lebih dari satu file",
            type=["xlsx"],
            accept_multiple_files=True,
        )

    use_extracted = False
    if st.session_state.extracted_data and not uploaded_files:
        use_extracted = st.checkbox(
            f"Gunakan {len(st.session_state.extracted_data)} data hasil ekstraksi dari halaman Maps Extractor",
            value=False,
        )

    st.download_button(
        "⬇️ Download template Excel",
        data=make_template_excel(),
        file_name="template_routing.xlsx",
        mime="application/vnd.ms-excel",
        help="Gunakan format ini agar file kamu langsung terbaca.",
    )

    df = None
    already_validated = False

    if uploaded_files:
        valid_parts = []
        file_errors = []
        for f in uploaded_files:
            try:
                file_df = pd.read_excel(f)
            except Exception as e:
                file_errors.append(f"**{f.name}**: gagal dibaca ({e})")
                continue

            is_valid, errors = validate_dataframe(file_df)
            if not is_valid:
                for err in errors:
                    file_errors.append(f"**{f.name}**: {err}")
                continue

            file_df = file_df.copy()
            file_df["source_file"] = f.name
            valid_parts.append(file_df)

        for err in file_errors:
            st.error(f"❌ {err}")

        if valid_parts:
            df = pd.concat(valid_parts, ignore_index=True)
            already_validated = True
            skipped = len(uploaded_files) - len(valid_parts)
            msg = f"✅ Berhasil menggabungkan {len(valid_parts)} file ({len(df)} baris total)."
            if skipped:
                msg += f" {skipped} file dilewati karena error di atas."
            st.success(msg)
        else:
            st.stop()
    elif use_extracted:
        df = pd.DataFrame(st.session_state.extracted_data)

    if df is not None:
        if not already_validated:
            is_valid, errors = validate_dataframe(df)
            if not is_valid:
                for err in errors:
                    st.error(f"❌ {err}")
                st.stop()

        df["latitude"] = pd.to_numeric(df["latitude"])
        df["longitude"] = pd.to_numeric(df["longitude"])

        with st.expander("📄 Data Awal", expanded=False):
            if "source_file" in df.columns:
                st.caption("Kolom `source_file` menunjukkan file asal tiap baris setelah digabung.")
            st.dataframe(df, width='stretch')

        st.markdown("### ⚙️ Pengaturan Route")
        c1, c2, c3 = st.columns(3)
        with c1:
            max_points_per_route = st.slider(
                "Maksimal titik per route", min_value=2, max_value=15,
                value=min(9, max(2, len(df))),
            )
        n_cluster_default = math.ceil(len(df) / max_points_per_route)
        with c2:
            st.metric("Total Merchant", len(df))
        with c3:
            st.metric("Estimasi Jumlah Route", n_cluster_default)

        run = st.button("🚀 Buat Rute Optimal", type="primary", width='stretch')

        # Fingerprint of the current input+settings, so stale results (from a
        # previous file/slider value) don't linger after the inputs change.
        data_fingerprint = (len(df), tuple(df["merchant_name"]), max_points_per_route, starting_link)

        if run:
            if len(df) < 2:
                st.warning("Minimal butuh 2 titik untuk membuat rute.")
                st.stop()

            with st.spinner("Mengelompokkan titik dan menghitung rute tercepat..."):
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
                for route_id in sorted(df["route"].unique()):
                    route_df = df[df["route"] == route_id].reset_index(drop=True)

                    if start_lat and start_lon:
                        start_df = pd.DataFrame(
                            [{"merchant_name": start_name, "latitude": start_lat, "longitude": start_lon}]
                        )
                        route_df = pd.concat([start_df, route_df], ignore_index=True)

                    distance_matrix = create_distance_matrix(route_df)
                    best_route = solve_tsp(distance_matrix)
                    optimized_df = route_df.iloc[best_route].reset_index(drop=True)
                    optimized_df["sequence"] = optimized_df.index + 1
                    optimized_df["route_name"] = f"Route {route_id + 1}"
                    all_routes.append(optimized_df)
                    route_summaries.append(
                        {
                            "route_id": route_id,
                            "df": optimized_df,
                            "distance_km": route_total_distance_km(optimized_df),
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
            }

        result = st.session_state.get("route_result")
        if result and result["fingerprint"] == data_fingerprint:
            if result["start_link_given"] and not result["start_ok"]:
                st.warning("Link Google Maps titik awal tidak dikenali, dilewati.")

            route_summaries = result["route_summaries"]
            st.success(f"✅ Berhasil membuat {len(route_summaries)} route optimal!")

            total_distance = sum(r["distance_km"] for r in route_summaries)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Route", len(route_summaries))
            m2.metric("Total Titik", result["total_points"])
            m3.metric("Estimasi Total Jarak", f"{total_distance:.1f} km")

            st.markdown("### 🗺️ Detail Setiap Route")
            first_route_id = route_summaries[0]["route_id"]
            for r in route_summaries:
                route_id = r["route_id"]
                optimized_df = r["df"]
                color = ROUTE_COLORS[route_id % len(ROUTE_COLORS)]

                with st.expander(
                    f"Route {route_id + 1} — {len(optimized_df)} titik — ~{r['distance_km']:.1f} km",
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

            st.markdown("### 📥 Unduh Hasil")
            st.download_button(
                label="Download Hasil Routing (Excel)",
                data=result["excel_bytes"],
                file_name="hasil_routing.xlsx",
                mime="application/vnd.ms-excel",
                type="primary",
                width='stretch',
            )
        elif result and result["fingerprint"] != data_fingerprint:
            st.info("Pengaturan atau data berubah — tekan **Buat Rute Optimal** lagi untuk memperbarui hasil.")
    else:
        st.info("⬆️ Upload file Excel atau centang opsi data hasil ekstraksi untuk memulai.")

# ================================================================
# HALAMAN 2: GOOGLE MAPS EXTRACTOR
# ================================================================
elif st.session_state.page == "Extract":
    st.markdown(
        '<div class="app-header"><h1>📍 Google Maps Extractor</h1></div>',
        unsafe_allow_html=True,
    )
    st.caption("Ubah link Google Maps menjadi tabel (merchant_name, latitude, longitude) siap pakai.")

    tab_link, tab_search, tab_manual = st.tabs(
        ["🔗 Dari Link Google Maps", "🔎 Cari Nama Merchant", "✏️ Input Manual"]
    )

    with tab_link:
        with st.form("extractor_form", clear_on_submit=True):
            new_link = st.text_input("Paste link Google Maps di sini:")
            submitted = st.form_submit_button("➕ Ekstrak & Tambahkan Data", width='stretch')

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
        st.caption(
            "Pencarian gratis via OpenStreetMap (Nominatim) — tanpa API key, tapi cakupan "
            "merchant kecil/UMKM di Indonesia masih lebih terbatas dibanding Google Maps. "
            "Sertakan kota/wilayah supaya hasilnya lebih relevan."
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

        if st.button("🔍 Cari Lokasi", width='stretch'):
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
            st.markdown(f"**Hasil untuk:** _{st.session_state.get('nominatim_searched_for', '')}_")
            idx_selected = st.radio(
                "Pilih lokasi yang sesuai:",
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
                manual_name = st.text_input("Nama merchant")
            with mc2:
                manual_lat = st.number_input("Latitude", value=0.0, format="%.6f")
            with mc3:
                manual_lon = st.number_input("Longitude", value=0.0, format="%.6f")
            manual_submit = st.form_submit_button("➕ Tambahkan Data", width='stretch')

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
        st.markdown("### 📋 Hasil Ekstraksi")
        st.caption("Klik dua kali pada sel untuk mengubah nilai, atau centang baris lalu tekan delete untuk menghapus.")

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

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🗑️ Hapus Semua Data", width='stretch'):
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
            if st.button("➡️ Gunakan di Routing Optimizer", type="primary", width='stretch'):
                st.session_state.pending_page = "Routing"
                st.rerun()
    else:
        st.info("Belum ada data. Tambahkan lewat link Google Maps atau input manual di atas.")
