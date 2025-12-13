import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# --- 1. Konfiguration ---
st.set_page_config(layout="wide", page_title="Privatjet Tracker Tom Cruise", page_icon="✈️")

# CSS: Abstände verringern
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
</style>
""", unsafe_allow_html=True)

CSV_FILE = 'tom_cruise_n350xx_flights.csv'
CO2_INGOLSTADT_ANNUAL_TONS = 1800000

# Koordinaten
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

# --- 2. Hilfsfunktionen ---

def extract_airport_code(location_str):
    if not isinstance(location_str, str): return None
    match = re.search(r'\(([^)]+)\)', str(location_str))
    return match.group(1).split()[-1] if match else None

# Berechnet Punkte für eine gekrümmte Linie (Great Circle)
def get_great_circle_path(lat1, lon1, lat2, lon2, num_points=30):
    # Konvertiere Grad in Radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Sphärische Interpolation (einfache Approximation für Visualisierung)
    t = np.linspace(0, 1, num_points)
    
    # Vereinfachte Berechnung für Mapbox (Linear zwischen den Vektoren)
    # Wir nutzen hier eine einfache Interpolation, da Mapbox Mercator ist,
    # aber wir wollen, dass es "rund" aussieht.
    # Echte Orthodrome Formel:
    d = 2 * np.arcsin(np.sqrt(np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2))
    if d == 0: return [np.degrees(lat1)], [np.degrees(lon1)]
    
    lats, lons = [], []
    for x in t:
        A = np.sin((1-x)*d) / np.sin(d)
        B = np.sin(x*d) / np.sin(d)
        x_val = A*np.cos(lat1)*np.cos(lon1) + B*np.cos(lat2)*np.cos(lon2)
        y_val = A*np.cos(lat1)*np.sin(lon1) + B*np.cos(lat2)*np.sin(lon2)
        z_val = A*np.sin(lat1) + B*np.sin(lat2)
        
        new_lat = np.arctan2(z_val, np.sqrt(x_val**2 + y_val**2))
        new_lon = np.arctan2(y_val, x_val)
        lats.append(np.degrees(new_lat))
        lons.append(np.degrees(new_lon))
        
    return lats, lons

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

# --- 3. Hauptprogramm ---

try:
    data = load_data(CSV_FILE)
    map_data = data.dropna(subset=['lat', 'lon', 'Ziel_lat', 'Ziel_lon'])
    total_flights = len(data)
except Exception as e:
    st.error(f"Fehler beim Laden: {e}")
    st.stop()

# Header
st.title("Privatjet Tracker Tom Cruise")
c1, c2, c3 = st.columns([1, 2, 1])
with c1: st.image("image-w856.jpg.webp", caption="Tom Cruise")
with c2: 
    st.header("Analyse der Flugbewegungen 2024")
    st.markdown(f"**{total_flights} Flüge** | N350XX | Bombardier Challenger 350")
with c3: st.image("Bild 2.jpeg", caption="Der Jet")
st.markdown("---")

# KPIs
total_dist = data['Distanz (Meilen)'].sum()
total_co2 = data['Emissionen (Metrische Tonnen)'].sum()
avg_co2 = data['Emissionen (Metrische Tonnen)'].mean()

def fmt(n): return f"{n:,.0f}".replace(",", ".")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Flüge", total_flights)
k2.metric("Meilen", fmt(total_dist))
k3.metric("CO₂ (Tonnen)", fmt(total_co2))
k4.metric("Ø CO₂/Flug", f"{avg_co2:.1f}".replace(".", ","))

st.markdown("---")

# --- 4. MAPBOX SATELLITEN-KARTE (Gestrichelt & Gekrümmt) ---
st.header("📍 Flugrouten")
st.markdown("Satellitenansicht. Die Routen folgen der Erdkrümmung.")

# Gruppieren
routes = map_data.groupby(['Abflugort', 'Zielort', 'lat', 'lon', 'Ziel_lat', 'Ziel_lon']).size().reset_index(name='Count')

fig = go.Figure()

for i, row in routes.iterrows():
    # 1. Berechne gekrümmte Linie (Orthodrome)
    lats_curve, lons_curve = get_great_circle_path(row['lat'], row['lon'], row['Ziel_lat'], row['Ziel_lon'])
    
    # 2. Linie zeichnen (Gestrichelt "dot")
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=lons_curve,
        lat=lats_curve,
        line=dict(width=2, color='#FF3333', dash='dot'), # Rot, gestrichelt, dünn
        opacity=0.8,
        hoverinfo='text',
        text=f"{row['Abflugort']} ➝ {row['Zielort']} ({row['Count']}x)",
        name=f"Route {i}"
    ))

    # 3. Flugzeug in der Mitte (Mittelpunkt der Kurve berechnen)
    mid_idx = len(lats_curve) // 2
    mid_lat = lats_curve[mid_idx]
    mid_lon = lons_curve[mid_idx]

    fig.add_trace(go.Scattermapbox(
        mode="text",
        lon=[mid_lon],
        lat=[mid_lat],
        text="✈", # Flugzeug Symbol
        textfont=dict(size=16, color="white"), # Weißes Flugzeug für guten Kontrast
        hoverinfo='skip'
    ))

# 4. Flughäfen
all_lons = list(map_data['lon']) + list(map_data['Ziel_lon'])
all_lats = list(map_data['lat']) + list(map_data['Ziel_lat'])
all_texts = list(map_data['Abflugort']) + list(map_data['Zielort'])

fig.add_trace(go.Scattermapbox(
    mode="markers",
    lon=all_lons,
    lat=all_lats,
    marker=dict(size=6, color='cyan'),
    text=all_texts,
    hoverinfo='text',
    name='Airports'
))

# Layout
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=700,
    showlegend=False,
    mapbox=dict(
        style="white-bg", # Basis für Layer
        layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
            },
            {
                "below": 'traces',
                "sourcetype": "raster",
                "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"]
            }
        ],
        center=dict(lat=35, lon=-90),
        zoom=3,
        pitch=30,
    )
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 5. Vergleich & Diagramme ---
st.header("📊 Statistiken & Vergleich")

c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Emissionen vs. Ingolstadt")
    comp_df = pd.DataFrame({
        'Quelle': ['Tom Cruise (2024)', 'Ingolstadt (Jahr)'],
        'CO2': [total_co2, CO2_INGOLSTADT_ANNUAL_TONS]
    })
    fig_comp = px.bar(comp_df, x='Quelle', y='CO2', color='Quelle', 
                      color_discrete_map={'Tom Cruise (2024)': '#FF4B4B', 'Ingolstadt (Jahr)': '#0083B8'})
    st.plotly_chart(fig_comp, use_container_width=True)
    st.info(f"Anteil an Ingolstadt: **{(total_co2/CO2_INGOLSTADT_ANNUAL_TONS)*100:.4f}%**")

with c_right:
    st.subheader("Top 5 Ziele")
    top5 = data['Zielort'].value_counts().head(5).reset_index()
    top5.columns = ['Ort', 'Count']
    top5['Label'] = top5['Ort'].apply(lambda x: x.split('(')[0][:20] + "...")
    fig_top = px.bar(top5, x='Count', y='Label', orientation='h', 
                     color='Count', color_continuous_scale='Blues')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

st.subheader("Monatliche Emissionen")
data['Monat'] = data['Datum'].dt.strftime('%Y-%m')
monthly = data.groupby('Monat')['Emissionen (Metrische Tonnen)'].sum().reset_index()
fig_m = px.bar(monthly, x='Monat', y='Emissionen (Metrische Tonnen)', 
               color='Emissionen (Metrische Tonnen)', color_continuous_scale='Reds')
st.plotly_chart(fig_m, use_container_width=True)
