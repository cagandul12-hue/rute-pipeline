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


def extract_google_maps_data(link):
    try:
        place_pattern = r"/place/([^/]+)/"
        place_match = re.search(place_pattern, link)
        place_name = place_match.group(1).replace("+", " ") if place_match else "START POINT"

        latitude = longitude = None
        lat_match = re.search(r"!3d(-?\d+\.\d+)", link)
        lon_match = re.search(r"!4d(-?\d+\.\d+)", link)

        if lat_match and lon_match:
            latitude = float(lat_match.group(1))
            longitude = float(lon_match.group(1))
        else:
            coord_match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", link)
            if coord_match:
                latitude = float(coord_match.group(1))
                longitude = float(coord_match.group(2))
        return place_name, latitude, longitude
    except Exception:
        return "START POINT", None, None


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

# ==========================================================================================
# SIDEBAR NAVIGATION
# ==========================================================================================
with st.sidebar:
    st.markdown("## 🚚 Routing & Extractor")
    st.caption("KMeans + TSP Engine")
    st.markdown("---")

    page_choice = st.radio(
        "Menu",
        options=["Routing", "Extract"],
        format_func=lambda p: "🛣️ Routing Optimizer" if p == "Routing" else "📍 Maps Extractor",
        index=0 if st.session_state.page == "Routing" else 1,
        label_visibility="collapsed",
    )
    st.session_state.page = page_choice

    st.markdown("---")
    with st.expander("ℹ️ Cara pakai"):
        st.write(
            "1. Buka **Maps Extractor** untuk mengubah link Google Maps jadi tabel koordinat, "
            "atau siapkan langsung file Excel.\n\n"
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
        uploaded_file = st.file_uploader(
            "📂 Upload Excel (kolom: merchant_name, latitude, longitude)",
            type=["xlsx"],
        )

    use_extracted = False
    if st.session_state.extracted_data and not uploaded_file:
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
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Gagal membaca file Excel: {e}")
            st.stop()
    elif use_extracted:
        df = pd.DataFrame(st.session_state.extracted_data)

    if df is not None:
        is_valid, errors = validate_dataframe(df)
        if not is_valid:
            for err in errors:
                st.error(f"❌ {err}")
            st.stop()

        df["latitude"] = pd.to_numeric(df["latitude"])
        df["longitude"] = pd.to_numeric(df["longitude"])

        with st.expander("📄 Data Awal", expanded=False):
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
                    start_name, start_lat, start_lon = extract_google_maps_data(starting_link)
                    if start_lat is None:
                        st.warning("Link Google Maps titik awal tidak dikenali, dilewati.")

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

            st.success(f"✅ Berhasil membuat {len(route_summaries)} route optimal!")

            total_distance = sum(r["distance_km"] for r in route_summaries)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Route", len(route_summaries))
            m2.metric("Total Titik", len(df) + (1 if start_lat and start_lon else 0) * len(route_summaries))
            m3.metric("Estimasi Total Jarak", f"{total_distance:.1f} km")

            st.markdown("### 🗺️ Detail Setiap Route")
            first_route_id = sorted(df["route"].unique())[0]
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
                        st_folium(fmap, width=None, height=350, key=f"map_{route_id}")

            final_df = pd.concat([r["df"] for r in route_summaries], ignore_index=True)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                final_df.to_excel(writer, index=False, sheet_name="Semua Route")
                for r in route_summaries:
                    sheet_name = f"Route {r['route_id'] + 1}"[:31]
                    r["df"].to_excel(writer, index=False, sheet_name=sheet_name)

            st.markdown("### 📥 Unduh Hasil")
            st.download_button(
                label="Download Hasil Routing (Excel)",
                data=buffer.getvalue(),
                file_name="hasil_routing.xlsx",
                mime="application/vnd.ms-excel",
                type="primary",
                width='stretch',
            )
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

    tab_link, tab_manual = st.tabs(["🔗 Dari Link Google Maps", "✏️ Input Manual"])

    with tab_link:
        with st.form("extractor_form", clear_on_submit=True):
            new_link = st.text_input("Paste link Google Maps di sini:")
            submitted = st.form_submit_button("➕ Ekstrak & Tambahkan Data", width='stretch')

            if submitted:
                if not new_link.strip():
                    st.error("❌ Link tidak boleh kosong.")
                else:
                    name, lat, lon = extract_google_maps_data(new_link)
                    if lat is not None and lon is not None:
                        st.session_state.extracted_data.append(
                            {"merchant_name": name, "latitude": float(lat), "longitude": float(lon)}
                        )
                        st.success(f"✅ Berhasil menambahkan: {name}")
                    else:
                        st.error("❌ Gagal mendeteksi koordinat dari link tersebut. Pastikan link berasal dari Google Maps dan memuat koordinat.")

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
                st_folium(fmap, width=None, height=350, key="extract_map")

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
                st.session_state.page = "Routing"
                st.rerun()
    else:
        st.info("Belum ada data. Tambahkan lewat link Google Maps atau input manual di atas.")
