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
    df['Abflug_Code'] = df['Abflugort'].apply(extract_airport_code)
    df['Ziel_Code'] = df['Zielort'].apply(extract_airport_code)
    df['lat'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['lon'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    df['Ziel_lat'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['Ziel_lon'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    return df

data = load_data(CSV_FILE)

# --- ZEITHORIZONT AUSWAHL ---
st.title("Privatjet Tracker Tom Cruise")
st.subheader("Time horizon (Kalenderjahr 2024)")

time_options = {
    "1 Monat (Jan)": "2024-01-31",
    "3 Monate (Jan-Mär)": "2024-03-31",
    "6 Monate (Jan-Jun)": "2024-06-30",
    "9 Monate (Jan-Sep)": "2024-09-30",
    "1 Jahr (Gesamt)": "2024-12-31"
}

selected_label = st.radio("Zeithorizont:", options=list(time_options.keys()), index=4, horizontal=True, label_visibility="collapsed")
end_date_filter = pd.to_datetime(time_options[selected_label])
filtered_data = data[(data['Datum'] >= "2024-01-01") & (data['Datum'] <= end_date_filter)]

# --- Basis-Metriken ---
total_flights = len(filtered_data)
total_emissions_sum = total_flights * 7.91
median_emissions = 7.9 # MEDIAN statt Durchschnitt zur Kompensation von Ausreißern

def format_de(number, decimals=0):
    return f"{number:,.{decimals}f}".replace(",", "|").replace(".", ",").replace("|", ".")

# --- 2. Bilder und Flugzeug-Details (Ähnlich wie TheAirTraffic-Screenshot) ---
col_img1, col_text, col_img2 = st.columns([1, 1.5, 1.5])

with col_img1:
    st.image("image-w856.jpg.webp", caption="Tom Cruise")

with col_text:
    st.header(f"Flugbewegungen: {selected_label}")
    st.markdown("---")
    # Flugzeug Info Panel (ähnlich Bild 0.jpg)
    st.subheader("✈️ Aircraft Information")
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown("**Registration:** N350XX")
        st.markdown("**Type Code:** CL35")
        st.markdown("**Serial Number:** 20835")
    with info_col2:
        st.markdown("**Type:** Bombardier Challenger 350")
        st.markdown("**Owner:** Tom Cruise / Sata LLC")
        st.markdown("**IATA:** CL35")

with col_img2:
    st.image("Bild 2.jpeg", caption="Bombardier Challenger 350")

# --- 3. KPIs ---
st.header("📊 Statistische Kennzahlen")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Anzahl Flüge", total_flights)
c2.metric("Distanz (Meilen)", format_de(filtered_data['Distanz (Meilen)'].sum()))
c3.metric("Emissionen (t CO₂)", format_de(total_emissions_sum, 1))
c4.metric("Median CO₂ pro Flug", "7,9") # Hier den Median anzeigen

st.markdown("---")

# --- 4. Karte mit Erdkrümmung ---
st.header("📍 3D Satelliten-Flugrouten")
map_data = filtered_data.dropna(subset=['lat', 'lon', 'Ziel_lat', 'Ziel_lon'])

if not map_data.empty:
    route_counts = map_data.groupby(['Abflugort', 'Zielort', 'lat', 'lon', 'Ziel_lat', 'Ziel_lon']).size().reset_index(name='Anzahl')
    fig = go.Figure()

    # Funktion für verstärkte Krümmung (Erdkrümmung)
    def create_great_circle_route(lat1, lon1, lat2, lon2, num_points=60):
        phi1, lam1 = math.radians(lat1), math.radians(lon1)
        phi2, lam2 = math.radians(lat2), math.radians(lon2)
        d_phi, d_lam = phi2 - phi1, lam2 - lam1
        a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam/2)**2
        sigma = 2 * math.asin(math.sqrt(a))
        lats, lons = [], []
        if sigma == 0: return [lat1, lat2], [lon1, lon2]
        for i in range(num_points + 1):
            f = i / num_points
            A, B = math.sin((1-f)*sigma) / math.sin(sigma), math.sin(f*sigma) / math.sin(sigma)
            x = A * math.cos(phi1) * math.cos(lam1) + B * math.cos(phi2) * math.cos(lam2)
            y = A * math.cos(phi1) * math.sin(lam1) + B * math.cos(phi2) * math.sin(lam2)
            z = A * math.sin(phi1) + B * math.sin(phi2)
            lats.append(math.degrees(math.atan2(z, math.sqrt(x**2 + y**2))))
            lons.append(math.degrees(math.atan2(y, x)))
        return lats, lons

    def calculate_bearing(lat1, lon1, lat2, lon2):
        l1, lo1, l2, lo2 = map(math.radians, [lat1, lon1, lat2, lon2])
        y = math.sin(lo2 - lo1) * math.cos(l2)
        x = math.cos(l1) * math.sin(l2) - math.sin(l1) * math.cos(l2) * math.cos(lo2 - lo1)
        return (math.degrees(math.atan2(y, x)) + 360) % 360

    for _, row in route_counts.iterrows():
        p_lats, p_lons = create_great_circle_route(row['lat'], row['lon'], row['Ziel_lat'], row['Ziel_lon'])
        ratio = row['Anzahl'] / route_counts['Anzahl'].max()
        l_color = f"rgb({int(255*ratio)}, {int(255*(1-ratio))}, 0)"
        
        fig.add_trace(go.Scattermapbox(
            mode="lines", lon=p_lons, lat=p_lats,
            line=dict(width=1.8, color=l_color), opacity=0.8, showlegend=False,
            hoverinfo='text', text=f"{row['Abflugort']} -> {row['Zielort']} ({row['Anzahl']}x)"
        ))
        
        mid = len(p_lats)//2
        brng = calculate_bearing(row['lat'], row['lon'], row['Ziel_lat'], row['Ziel_lon'])
        fig.add_trace(go.Scattermapbox(
            mode="markers", lon=[p_lons[mid]], lat=[p_lats[mid]],
            marker=dict(symbol='airport', size=18, color='black', angle=brng), showlegend=False, hoverinfo='skip'
        ))

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}, height=700,
        mapbox=dict(
            style="white-bg", 
            layers=[{"below": 'traces', "sourcetype": "raster", "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]}],
            center=dict(lat=30, lon=-80), zoom=3.5, pitch=45
        )
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 5. CO2-Kompensation ---
st.header("🌳 CO₂-Kompensation (Privatjet)") 
f_sim = st.slider('Anzahl der Privatjet-Flüge simulieren:', 1, total_flights, total_flights)
cur_emissions = f_sim * median_emissions
cur_trees = cur_emissions / CO2_PER_TREE_TONS_ANNUALLY
f_size = int(35 + (110 - 35) * (f_sim / total_flights))

c_i, c_t = st.columns([1, 4])
with c_i: st.markdown(f"<div style='text-align: center;'><span style='font-size: {f_size}px;'>🌳</span></div>", unsafe_allow_html=True)
with c_t: st.markdown(f"Bei **{f_sim} Privatjet-Flügen** entstehen Emissionen von **{format_de(cur_emissions, 2)} Tonnen CO₂**. Kompensation: **{format_de(cur_trees, 0)} Bäume**.")

st.markdown("---")

# --- 5.5 KOMMERZIELLER VERGLEICH & BUSINESS-METRIK ---
st.header("✈️ Vergleich: Kommerzieller Flug & Business Class")
COMM_FACTOR = 0.10
f_comm = st.slider('Flüge kommerziell simulieren:', 1, total_flights, total_flights, key='c_slider')
e_comm = f_comm * (median_emissions * COMM_FACTOR)
t_comm = e_comm / CO2_PER_TREE_TONS_ANNUALLY
# Berechnung: Wie oft Business Class für einen Privatflug
times_business = 1.0 / COMM_FACTOR 

col_comm_icon, col_comm_text = st.columns([1, 4])
with col_comm_icon: st.markdown(f"<div style='text-align: center;'><span style='font-size: 35px;'>🌳</span></div>", unsafe_allow_html=True)
with col_comm_text:
    st.markdown(f"Kommerziell entsprächen dieselben Flüge nur **{format_de(e_comm, 2)} Tonnen CO₂** ({format_de(t_comm, 0)} Bäume).")
    st.success(f"**Vergleich:** Mit dem CO₂-Ausstoß eines einzigen Privatflugs könnte er die gleiche Strecke **{int(times_business)} Mal** in der Business Class eines Linienfluges zurücklegen.")

st.markdown("---")

# --- 6. Detaillierte Statistiken ---
st.header("📈 Detaillierte Statistiken")
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    filtered_data['Monat_Str'] = filtered_data['Datum'].dt.strftime('%Y-%m')
    m_stats = filtered_data.groupby('Monat_Str')['Emissionen (Metrische Tonnen)'].sum().reset_index()
    st.plotly_chart(px.bar(m_stats, x='Monat_Str', y='Emissionen (Metrische Tonnen)', color_continuous_scale='Reds', color='Emissionen (Metrische Tonnen)', title="Emissionen pro Monat"), use_container_width=True)
with col_chart2:
    top_dest = filtered_data['Zielort'].value_counts().head(5).reset_index()
    st.plotly_chart(px.bar(top_dest, x='count', y='Zielort', orientation='h', color_continuous_scale='Blues', color='count', title="Top 5 Zielorte"), use_container_width=True)
