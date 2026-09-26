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
from sklearn.cluster import KMeans  # Clustering 
from ortools.constraint_solver import pywrapcp # Library OR-Tools untuk TSP
from ortools.constraint_solver import routing_enums_pb2 # Library OR-Tools untuk TSP
from streamlit_folium import st_folium # Maps

st.set_page_config(page_title="Routing & Extractor System", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# ==========================================================================================
# SEMUA FUNGSI (Diletakkan di atas agar bisa diakses oleh semua halaman)
# ==========================================================================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def create_distance_matrix(df):
    matrix = []
    for i in range(len(df)):
        row = []
        for j in range(len(df)): 
            dist = haversine(df.iloc[i]["latitude"], df.iloc[i]["longitude"], df.iloc[j]["latitude"], df.iloc[j]["longitude"])
            row.append(int(dist * 1000))
        matrix.append(row)
    return matrix

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
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    solution = routing.SolveWithParameters(search_parameters)
    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        route.append(node)
        index = solution.Value(routing.NextVar(index))
    return route

def generate_google_maps_link(df):
    coords = [f"{row.latitude},{row.longitude}" for _, row in df.iterrows()]
    if len(coords) < 2: return None
    origin = coords[0]
    destination = coords[-1]
    waypoints = "%7C".join(coords[1:-1])
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    if waypoints: url += f"&waypoints={waypoints}"
    url += "&travelmode=driving"
    return url

def extract_google_maps_data(link):
    try:
        place_pattern = r'/place/([^/]+)/'
        place_match = re.search(place_pattern, link)
        if place_match:
            place_name = place_match.group(1).replace("+", " ")
        else:
            place_name = "START POINT"

        latitude = None
        longitude = None
        lat_match = re.search(r'!3d(-?\d+\.\d+)', link)
        lon_match = re.search(r'!4d(-?\d+\.\d+)', link)
        
        if lat_match and lon_match:
            latitude = float(lat_match.group(1))
            longitude = float(lon_match.group(1))
        else:
            coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', link)
            if coord_match:
                latitude = float(coord_match.group(1))
                longitude = float(coord_match.group(2))
        return place_name, latitude, longitude
    except:
        return "START POINT", None, None
    
def balance_clusters(df, max_points_per_route):
    while True:
        cluster_sizes = (df["route"].value_counts().to_dict())
        oversized_clusters = [cluster for cluster, size in cluster_sizes.items() if size > max_points_per_route]
        if not oversized_clusters: break
        
        for big_cluster in oversized_clusters:
            excess_points = (cluster_sizes[big_cluster] - max_points_per_route)
            big_cluster_df = df[df["route"] == big_cluster]
            
            candidate_clusters = [cluster for cluster, size in cluster_sizes.items() if size < max_points_per_route]
            
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
    return df

# ================================================================
# SIDEBAR NAVIGATION
# ================================================================
if "page" not in st.session_state:
    st.session_state.page = "Routing"

with st.sidebar:
    st.markdown("## 🚚 Navigation")
    if st.button("🛣️ Routing Optimizer", use_container_width=True):
        st.session_state.page = "Routing"
    if st.button("📍 Maps Extractor", use_container_width=True):
        st.session_state.page = "Extract"
    st.markdown("---")
    st.caption("KMeans + TSP Engine")

# ================================================================
# HALAMAN 1: ROUTING PIPELINE OPTIMIZER
# ================================================================
if st.session_state.page == "Routing":
    st.title("Routing Pipeline Optimizer by ODP")
    st.subheader("Optimalkan rute pipeline dengan clustering dan TSP")

    starting_link = st.text_input("Input Link Google Maps Titik Awal", placeholder="Paste link Google Maps di sini")
    uploaded_file = st.file_uploader("Upload Excel berisi merchant_name, latitude & longitude.", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        required_cols = ["merchant_name", "latitude", "longitude"]

        if not all(col in df.columns for col in required_cols):
            st.error("Kolom wajib: merchant_name, latitude, longitude")
            st.stop()
            
        st.subheader("Data Awal")
        st.dataframe(df)

        st.subheader("Pengaturan Route")
        max_points_per_route = st.slider("Maksimal Titik per Route", min_value=2, max_value=9, value=9)
        coords = df[["latitude", "longitude"]] 

        n_cluster = math.ceil(len(df) / max_points_per_route)
        kmeans = KMeans(n_clusters=n_cluster, random_state=42, n_init=10)    
        df["route"] = kmeans.fit_predict(coords)
        df = balance_clusters(df, max_points_per_route)
        
        cluster_sizes = df["route"].value_counts()
        st.success(f"Total Route Digunakan: {n_cluster}")
        st.write("Jumlah titik tiap route:")
        st.write(cluster_sizes.sort_index())
            
        all_routes = []
        start_name, start_lat, start_lon = "START POINT", None, None

        if starting_link:
            start_name, start_lat, start_lon = extract_google_maps_data(starting_link)
                
        for route_id in sorted(df["route"].unique()): 
            route_df = df[df["route"] == route_id].reset_index(drop=True)
            
            if start_lat and start_lon:
                start_df = pd.DataFrame([{"merchant_name": start_name, "latitude": start_lat, "longitude": start_lon}])
                route_df = pd.concat([start_df, route_df], ignore_index=True)
            
            distance_matrix = create_distance_matrix(route_df)
            best_route = solve_tsp(distance_matrix)           
            optimized_df = route_df.iloc[best_route].reset_index(drop=True)
            optimized_df["sequence"] = (optimized_df.index + 1)
            optimized_df["route_name"] = (f"Route {route_id + 1}")
            all_routes.append(optimized_df)

            st.subheader(f"Route {route_id + 1}")
            st.dataframe(optimized_df[["sequence", "merchant_name", "latitude","longitude"]])

            maps_url = generate_google_maps_link(optimized_df)           
            st.markdown(f'<a href="{maps_url}" target="_blank">🚗 Open Google Maps Navigation</a>', unsafe_allow_html=True)

            center_lat = optimized_df["latitude"].mean()        
            center_lon = optimized_df["longitude"].mean()
            m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
            polyline_coords = []

            for idx, row in optimized_df.iterrows():
                coord = [row["latitude"], row["longitude"]]
                polyline_coords.append(coord)
                folium.Marker(coord, popup=f"{idx+1}. {row['merchant_name']}").add_to(m)

            folium.PolyLine(polyline_coords, weight=5).add_to(m)
            st_folium(m, width=1200, height=400)
            st.markdown('<div style="margin-top: -35px;"></div>', unsafe_allow_html=True)
            st.markdown("---")

        # Export (Diubah menjadi BytesIO agar berjalan optimal di web Streamlit)
        final_df = pd.concat(all_routes, ignore_index=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False)
        
        st.download_button(
            label="Download Routing Excel",
            data=buffer.getvalue(),
            file_name="hasil_routing.xlsx",
            mime="application/vnd.ms-excel"
        )


# ================================================================
# HALAMAN 2: GOOGLE MAPS EXTRACTOR
# ================================================================
elif st.session_state.page == "Extract":
    st.title("📍 Google Maps Extractor")
    st.write("Ubah link Google Maps menjadi format tabel (Nama, Latitude, Longitude)")
    
    # Inisialisasi list kosong di session state agar data tidak hilang saat refresh
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = []

    # Kolom Input
    with st.form("extractor_form", clear_on_submit=True):
        new_link = st.text_input("Paste Link Google Maps di sini:")
        submitted = st.form_submit_button("Ekstrak & Tambahkan Data")

        if submitted and new_link:
            name, lat, lon = extract_google_maps_data(new_link)
            
            if lat is not None and lon is not None:               
                # Menambahkan ke database sementara
                st.session_state.extracted_data.append({
                    "merchant_name": name,
                    "latitude": float(lat),
                    "longitude":float(lon)
                })
                st.success(f"✅ Berhasil menambahkan: {name}") 
            else:
                st.error("❌ Gagal mendeteksi koordinat dari link tersebut.")

    # Tampilkan Tabel jika ada isinya
    if len(st.session_state.extracted_data) > 0:
        st.subheader("Hasil Ekstraksi")
        
        # Buat dataframe untuk preview
        df_extract = pd.DataFrame(st.session_state.extracted_data)
        st.dataframe(df_extract, use_container_width=True)
        
        col1, col2 = st.columns([1, 4])
        # Fitur Hapus Semua
        with col1:
            if st.button("🗑️ Hapus Semua Data"):
                st.session_state.extracted_data = []
                st.rerun()
                
        # Fitur Download Excel
        with col2:
            buffer_ext = io.BytesIO()
            with pd.ExcelWriter(buffer_ext, engine='openpyxl') as writer:
                df_extract.to_excel(writer, index=False)
                
            st.download_button(
                label="📥 Download Excel (.xlsx)",
                data=buffer_ext.getvalue(),
                file_name="hasil_extract_gmaps.xlsx",
                mime="application/vnd.ms-excel"
            )
