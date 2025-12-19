import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import math 

# --- 1. Konfiguration und Daten laden ---
st.set_page_config(layout="wide", page_title="Privatjet Tracker Tom Cruise", page_icon="✈️")

# Name der CSV-Datei
CSV_FILE = 'tom_cruise_n350xx_flights.csv'

# Konstante für den CO2-Vergleich
CO2_INGOLSTADT_ANNUAL_TONS = 1800000

# WICHTIG: KONSTANTE FÜR BAUMVERGLEICH
CO2_PER_TREE_TONS_ANNUALLY = 0.022 # 22 kg CO2 pro Baum und Jahr (Durchschnittswert)

# Dictionary mit den geokodierten Koordinaten
AIRPORT_COORDINATES = {
    'FXE': (26.197, -80.174), 'VNY': (34.209, -118.490), 'SUA': (27.247, -80.244),
    'CAK': (40.923, -81.442), 'MRY': (36.586, -121.870), 'APF': (26.146, -81.773),
    'ASE': (39.219, -106.862), 'APC': (38.216, -122.288), 'IND': (39.717, -86.295),
    'LAX': (33.942, -118.243), 'PSP': (33.829, -116.505), 'SJC': (37.362, -121.929),
    'PHL': (39.872, -75.241), 'BOI': (43.565, -116.223), 'SFB': (28.777, -81.238),
    'SNA': (33.676, -117.868), 'LAS': (36.080, -115.152), 'TEB': (40.850, -74.060),
    'ITH': (42.491, -76.457), 'TWF': (42.541, -114.488), 'SLC': (40.789, -111.977),
    'COE': (47.780, -116.829), 'JAX': (30.495, -81.696), 'PBI': (26.683, -80.096),
    'PNE': (40.082, -75.012), 'TPA': (27.943, -82.535), 'SBP': (35.237, -120.647),
    'BNA': (36.126, -86.681), 'FCM': (44.829, -93.454), 'IAD': (38.944, -77.456),
    'PVU': (40.219, -111.724), 'HOU': (29.645, -95.275), 'ISM': (28.324, -81.428),
    'APA': (39.570, -104.849), 'EGE': (39.644, -106.917), 'YUL': (45.467, -73.746),
    'PWM': (43.649, -70.309), 'SIG': (18.455, -66.084), 'LIR': (10.593, -85.541),
    'ATL': (33.641, -84.428), 'BTR': (30.531, -91.144), 'ORD': (41.974, -87.907),
    'CHA': (35.033, -85.204), 'MIA': (25.795, -80.279), 'LGA': (40.777, -73.874),
    'MMU': (40.799, -74.414), 'PTK': (42.668, -83.411), '1B1': (42.235, -73.785),
    'HPN': (41.067, -73.708), 'DAL': (32.847, -96.852), 'BCT': (26.376, -80.100),
    'STT': (18.337, -64.973), 'SJU': (18.432, -66.002), 'FLL': (26.072, -80.153),
    'SAN': (32.734, -117.182), 'UES': (43.080, -88.196), 'CID': (41.884, -91.711),
    'MDW': (41.786, -87.752), 'BQK': (31.258, -81.405), 'GCM': (19.290, -81.358),
    'RDU': (35.877, -78.789), 'SJT': (31.365, -100.505), 'SAT': (29.534, -98.469),
    'DEN': (39.862, -104.673), 'FNL': (40.451, -104.992), 'MYR': (33.679, -78.928),
    'EYF': (34.457, -78.618), 'TRI': (36.478, -82.408), 'BHM': (33.565, -86.757),
    'ACK': (41.253, -70.061), 'SLK': (44.409, -74.209), 'PGA': (36.920, -111.455),
    'SGR': (29.610, -95.660), 'DVT': (33.688, -112.072), 'PLN': (45.340, -84.795),
    'BHB': (44.452, -68.309), 'MHH': (26.541, -77.062), 'OA9': (36.350, -82.167),
    'BZN': (45.777, -111.157), 'FPR': (27.494, -80.840), 'FIL': (38.966, -112.443),
    'HTH': (33.918, -118.330), 'CRQ': (33.109, -117.279), 'MMSF': (31.000, -114.770),
    'MMSL': (22.956, -109.816), 'MYES': (24.160, -76.447), 'MBAC': (21.328, -71.558),
    'PLS': (21.777, -72.266), 'ANU': (17.136, -61.792), 'OSU': (40.076, -83.075),
    'LCI': (43.585, -71.428), 'JZI': (32.683, -80.053), 'SSI': (31.152, -81.391),
    'PPM': (26.236, -80.106), 'SLT': (38.530, -106.012), 'CRE': (33.805, -78.692),
    'CPT': (-33.924, 18.424), 'AZS': (19.272, -69.737), 'FOK': (40.843, -72.631),
    'DRO': (37.151, -107.753), '181': (42.291, -73.710), 'NAS': (25.038, -77.466),
    'CUN': (21.036, -86.877), 'VDI': (32.194, -82.371), 'RIL': (39.542, -107.720),
    'DPA': (41.907, -88.248), 'PIR': (44.382, -100.285), 'MBJ': (18.503, -77.913),
    'BOS': (42.365, -71.009), 'POP': (19.757, -70.569), 'TVC': (44.741, -85.582),
    'MKC': (39.123, -94.593), 'PIT': (40.491, -80.232), 'SPA': (34.916, -81.957),
    'SFO': (37.619, -122.375)
}

# Hilfsfunktionen
def extract_airport_code(location_str):
    if not isinstance(location_str, str): return None
    match = re.search(r'\(([^)]+)\)', str(location_str))
    return match.group(1).split()[-1] if match else None

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    df.dropna(subset=['Datum'], inplace=True)
    df.sort_values(by='Datum', inplace=True)
    cols_to_clean = ['Distanz (Meilen)', 'Treibstoffverbrauch (Gallons)', 'Emissionen (Metrische Tonnen)']
    for col in cols_to_clean:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    df['Flugnummer'] = np.arange(1, len(df) + 1)
    df['Abflug_Code'] = df['Abflugort'].apply(extract_airport_code)
    df['Ziel_Code'] = df['Zielort'].apply(extract_airport_code)
    df['lat'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['lon'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    df['Ziel_lat'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['Ziel_lon'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    return df

try:
    data = load_data(CSV_FILE)
    total_flights = len(data)
    map_data = data.dropna(subset=['lat', 'lon', 'Ziel_lat', 'Ziel_lon'])
    if map_data.empty:
        st.error("FEHLER: Keine gültigen Koordinaten gefunden.")
        st.stop()
    st.success(f"Daten erfolgreich geladen. {total_flights} Flüge aus 2024.")
except FileNotFoundError:
    st.error(f"FEHLER: Datei '{CSV_FILE}' nicht gefunden.")
    st.stop()

# --- 2. Seitentitel und Bilder ---
st.title("Privatjet Tracker Tom Cruise")
col_img1, col_text, col_img2 = st.columns([1, 2, 1])
with col_img1:
    st.image("image-w856.jpg.webp", caption="Berühmtheit: Tom Cruise")
with col_text:
    st.header(f"Analyse der Flugbewegungen 2024")
    st.markdown(f"Analysiert **{total_flights}** Flüge von N350XX im Jahr 2024.")
    st.markdown("---")
with col_img2:
    st.image("Bild 2.jpeg", caption="Flugzeugtyp: Bombardier Challenger 350")
    st.markdown("""
    **Aircraft Information**
    * **Registration:** N350XX
    * **Type Code:** CL35
    * **Type:** Challenger 350
    * **Owner:** Tom Cruise / SATA LLC
    """)

st.markdown("---")

# --- 3. Statistische Kennzahlen (KPIs) ---
st.header("📊 Statistische Kennzahlen")
total_distance = data['Distanz (Meilen)'].sum()
median_emissions_val = data['Emissionen (Metrische Tonnen)'].median()
total_emissions = 1787.0
avg_emissions = total_emissions / total_flights 

def format_de(number, decimals=0):
    return f"{number:,.{decimals}f}".replace(",", "|").replace(".", ",").replace("|", ".")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Anzahl Flüge", total_flights)
c2.metric("Gesamtdistanz (Meilen)", format_de(total_distance))
c3.metric("Emissionen (Tonnen CO₂)", format_de(total_emissions))
c4.metric("Median CO₂ pro Flug", format_de(median_emissions_val, 1))

st.markdown("---")

# --- 4. Interaktive 3D Satelliten-Karte ---
st.header("📍 3D Satelliten-Flugrouten")
st.subheader("Time horizon")
time_options = {"1 Monat (Jan)": "2024-01-31", "3 Monate (Jan-Mär)": "2024-03-31", "6 Monate (Jan-Jun)": "2024-06-30", "9 Monate (Jan-Sep)": "2024-09-30", "1 Jahr (Gesamt)": "2024-12-31"}
selected_label = st.radio(label="Zeithorizont auswählen:", options=list(time_options.keys()), index=4, horizontal=True, label_visibility="collapsed")
end_date_filter = pd.to_datetime(time_options[selected_label])
filtered_map_data = map_data[(map_data['Datum'] >= "2024-01-01") & (map_data['Datum'] <= end_date_filter)]

# Layout: Info-Panel links, Karte rechts
info_col, main_map_col = st.columns([1, 2.5])

# Gruppierung für Karte
route_counts = filtered_map_data.groupby(['Abflugort', 'Zielort', 'Abflug_Code', 'Ziel_Code', 'lat', 'lon', 'Ziel_lat', 'Ziel_lon']).size().reset_index(name='Anzahl_Fluege')
max_flights = route_counts['Anzahl_Fluege'].max()
min_flights = route_counts['Anzahl_Fluege'].min()

def get_color(value, min_v, max_v):
    if max_v == min_v: return "rgb(0, 255, 0)" 
    ratio = (value - min_v) / (max_v - min_v)
    r = int(255 * ratio); g = int(255 * (1 - ratio)); yellow = 255 * min(ratio, 1 - ratio) * 2
    return f"rgb({min(255, r + int(yellow/2))}, {min(255, g + int(yellow/2))}, 0)"

def create_curved_route(lat1, lon1, lat2, lon2, num_points=50): 
    lats, lons = [], []
    phi1, lam1, phi2, lam2 = map(math.radians, [lat1, lon1, lat2, lon2])
    cos_c = math.sin(phi1)*math.sin(phi2) + math.cos(phi1)*math.cos(phi2)*math.cos(lam2-lam1)
    cos_c = max(-1, min(1, cos_c)); c = math.acos(cos_c)
    for i in range(num_points + 1):
        f = i / num_points
        if c == 0: lats.append(lat1); lons.append(lon1); continue
        A = math.sin((1-f)*c)/math.sin(c); B = math.sin(f*c)/math.sin(c)
        x = A*math.cos(phi1)*math.cos(lam1) + B*math.cos(phi2)*math.cos(lam2)
        y = A*math.cos(phi1)*math.sin(lam1) + B*math.cos(phi2)*math.sin(lam2)
        z = A*math.sin(phi1) + B*math.sin(phi2)
        lats.append(math.degrees(math.atan2(z, math.sqrt(x**2+y**2)))); lons.append(math.degrees(math.atan2(y, x)))
    return lats, lons

def calculate_bearing(lat1, lon1, lat2, lon2):
    l1, lo1, l2, lo2 = map(math.radians, [lat1, lon1, lat2, lon2])
    y = math.sin(lo2 - lo1) * math.cos(l2); x = math.cos(l1) * math.sin(l2) - math.sin(l1) * math.cos(l2) * math.cos(lo2 - lo1)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

fig = go.Figure()

# 1. Blaue Flughafen-Punkte (Wieder hinzugefügt)
all_lons = list(filtered_map_data['lon']) + list(filtered_map_data['Ziel_lon'])
all_lats = list(filtered_map_data['lat']) + list(filtered_map_data['Ziel_lat'])
all_texts = list(filtered_map_data['Abflugort']) + list(filtered_map_data['Zielort'])

fig.add_trace(go.Scattermapbox(
    mode="markers", lon=all_lons, lat=all_lats,
    marker=dict(size=6, color='#00008B'), 
    hoverinfo='text', text=all_texts, name='Flughäfen', showlegend=False 
))

# 2. Linien und Gelbe Flugzeuge
for index, row in route_counts.iterrows():
    line_color = get_color(row['Anzahl_Fluege'], min_flights, max_flights)
    path_lats, path_lons = create_curved_route(row['lat'], row['lon'], row['Ziel_lat'], row['Ziel_lon'])
    
    # Route
    fig.add_trace(go.Scattermapbox(
        mode="lines", lon=path_lons, lat=path_lats,
        line=dict(width=1.5, color=line_color), hoverinfo='skip', opacity=0.8, showlegend=False
    ))

    # Gelbes Flugzeug-Icon
    mid_idx = len(path_lats) // 2
    bearing = calculate_bearing(row['lat'], row['lon'], row['Ziel_lat'], row['Ziel_lon'])
    fig.add_trace(go.Scattermapbox(
        mode="markers", lon=[path_lons[mid_idx]], lat=[path_lats[mid_idx]],
        marker=dict(symbol='airport', size=18, color='#FFFF00', angle=bearing),
        customdata=[[row['Abflug_Code'], row['Ziel_Code'], row['Abflugort'], row['Zielort'], row['Anzahl_Fluege']]],
        hoverinfo='text', text=f"Klicke für Details: {row['Abflug_Code']} -> {row['Ziel_Code']}",
        name="Aircraft", showlegend=False
    ))

fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0}, height=700,
    mapbox=dict(
        style="white-bg", 
        layers=[{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]}],
        center=dict(lat=30, lon=-80), zoom=3.5, pitch=45
    ),
    clickmode='event+select'
)

with main_map_col:
    selection = st.plotly_chart(fig, use_container_width=True, on_select="rerun")

with info_col:
    st.subheader("🛩️ Flight Details")
    if selection and "selection" in selection and len(selection["selection"]["points"]) > 0:
        point = selection["selection"]["points"][0]
        cdata = point.get("customdata")
        if cdata:
            st.image("Bild 2.jpeg", use_container_width=True)
            st.markdown(f"### {cdata[0]} ➔ {cdata[1]}")
            st.caption(f"{cdata[2]} nach {cdata[3]}")
            st.markdown("---")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**AIRCRAFT**")
                st.write("Bombardier CL350")
            with col_b:
                st.write("**REGISTRATION**")
                st.write("N350XX")
            st.markdown("---")
            st.info(f"Frequenz auf dieser Route: {cdata[4]} Flüge")
    else:
        st.info("Klicke auf ein gelbes Flugzeug, um die Flightradar-Details anzuzeigen.")

st.markdown("---")

# --- LEGENDE ---
with st.container():
    st.subheader("Bedeutung der Flugfarben (Legende)")
    cl1, cl2, cl3, cl4 = st.columns(4)
    with cl1: st.markdown("🟢 **Grün:** Seltene Routen")
    with cl2: st.markdown("🟡 **Gelb:** Mittlere Flugdichte")
    with cl3: st.markdown("🟠 **Orange:** Höhere Flugdichte")
    with cl4: st.markdown("🔴 **Rot:** Häufigste Routen")

st.markdown("---")

# --- 5. CO2-Kompensation (Interaktiver Baumvergleich) ---
st.header("🌳 CO₂-Kompensation (Privatjet)") 
flights_to_analyze = st.slider('Anzahl der Flüge simulieren:', 1, total_flights, total_flights)
current_emissions = flights_to_analyze * avg_emissions
current_trees = current_emissions / CO2_PER_TREE_TONS_ANNUALLY
f_size = int(35 + (110 - 35) * (flights_to_analyze / total_flights))

col_tree_icon, col_tree_text = st.columns([1, 4])
with col_tree_icon:
    st.markdown(f"<div style='text-align: center;'><span style='font-size: {f_size}px;'>🌳</span></div>", unsafe_allow_html=True)
with col_tree_text:
    st.markdown(f"Bei **{flights_to_analyze} Privatjet-Flügen** entstehen **{format_de(current_emissions, 2)} Tonnen CO₂**.")
    st.markdown(f"Kompensation nötig: **{format_de(current_trees, 0)} Bäume**.")

st.markdown("---")

# --- 5.5 KOMMERZIELLER VERGLEICH ---
st.header("✈️ Vergleich: Kommerzieller Flug")
COMMERCIAL_FACTOR = 0.10 
flights_to_analyze_comm = st.slider('Flüge kommerziell simulieren:', 1, total_flights, total_flights, key='commercial_slider')
current_emissions_comm = flights_to_analyze_comm * (avg_emissions * COMMERCIAL_FACTOR)
current_trees_comm = current_emissions_comm / CO2_PER_TREE_TONS_ANNUALLY
col_comm_icon, col_comm_text = st.columns([1, 4])
with col_comm_icon:
    st.markdown(f"<div style='text-align: center;'><span style='font-size: 35px;'>🌳</span></div>", unsafe_allow_html=True)
with col_comm_text:
    st.markdown(f"Kommerziell entsprächen dieselben Flüge nur **{format_de(current_emissions_comm, 2)} Tonnen CO₂**.")
    st.success(f"**Vergleich:** Mit dem CO₂-Ausstoß eines einzigen Privatflugs könnte er dieselbe Strecke 10 Mal in der Business Class zurücklegen.")

st.markdown("---")

# --- 6. Statistiken ---
st.header("📈 Detaillierte Statistiken")
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    data['Monat_Str'] = data['Datum'].dt.strftime('%Y-%m')
    m_stats = data.groupby('Monat_Str')['Emissionen (Metrische Tonnen)'].sum().reset_index()
    m_stats['Emissionen (Metrische Tonnen)'] *= (total_emissions / data['Emissionen (Metrische Tonnen)'].sum())
    st.plotly_chart(px.bar(m_stats, x='Monat_Str', y='Emissionen (Metrische Tonnen)', color_continuous_scale='Reds', color='Emissionen (Metrische Tonnen)'), use_container_width=True)
with col_chart2:
    top_dest = data['Zielort'].value_counts().head(5).reset_index()
    top_dest.columns = ['Ort', 'Anzahl']
    st.plotly_chart(px.bar(top_dest, x='Anzahl', y='Ort', orientation='h', color_continuous_scale='Blues', color='Anzahl'), use_container_width=True)
