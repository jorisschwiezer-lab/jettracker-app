import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. Konfiguration ---
st.set_page_config(layout="wide", page_title="Privatjet Tracker Tom Cruise", page_icon="✈️")

# CSS HACK: Entfernt den weißen Rand oben, damit der "Space Look" besser wirkt
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    div[data-testid="stMetricValue"] {font-size: 1.5rem !important;}
</style>
""", unsafe_allow_html=True)

# Konstanten
CSV_FILE = 'tom_cruise_n350xx_flights.csv'
CO2_INGOLSTADT_ANNUAL_TONS = 1800000

# Koordinaten (Deine Liste)
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

# --- 2. Funktionen ---
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

# --- 3. Hauptprogramm ---

try:
    data = load_data(CSV_FILE)
    map_data = data.dropna(subset=['lat', 'lon', 'Ziel_lat', 'Ziel_lon'])
    total_flights = len(data)
    st.success(f"Datensatz geladen: {total_flights} Flüge.")
except Exception as e:
    st.error(f"Fehler: {e}")
    st.stop()

# Layout Titel
st.title("Privatjet Tracker Tom Cruise")

col_img1, col_text, col_img2 = st.columns([1, 2, 1])
with col_img1:
    st.image("image-w856.jpg.webp", caption="Berühmtheit: Tom Cruise")
with col_text:
    st.header("Analyse der Flugbewegungen 2024")
    st.markdown(f"Tracker für Bombardier Challenger 350 (N350XX).")
with col_img2:
    st.image("Bild 2.jpeg", caption="Flugzeugtyp: Challenger 350")
st.markdown("---")

# KPIs
total_distance = data['Distanz (Meilen)'].sum()
total_emissions = data['Emissionen (Metrische Tonnen)'].sum()
avg_emissions = data['Emissionen (Metrische Tonnen)'].mean()

def format_de(number, decimals=0):
    return f"{number:,.{decimals}f}".replace(",", "|").replace(".", ",").replace("|", ".")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Anzahl Flüge", total_flights)
c2.metric("Gesamtdistanz", format_de(total_distance) + " Meilen")
c3.metric("Emissionen", format_de(total_emissions) + " t CO₂")
c4.metric("Ø pro Flug", format_de(avg_emissions, 1) + " t CO₂")

st.markdown("---")

# --- 4. HIGH-END 3D GLOBUS ---
st.header("🌍 Flugrouten & Frequenz")
st.markdown("""
<div style="background-color: #0e1117; padding: 10px; border-radius: 5px; border-left: 5px solid #FFD700;">
    <strong>Legende:</strong> 
    <span style="color: #FFD700;">⬥ Goldene Diamanten</span> = Flughäfen | 
    <span style="color: #FF4B4B;">Dicke Linien</span> = Häufige Routen |
    Die Linien folgen der <strong>realen Erdkrümmung</strong> (Orthodromen).
</div>
""", unsafe_allow_html=True)

# Daten gruppieren für Dicke
route_counts = map_data.groupby(['Abflugort', 'Zielort', 'lat', 'lon', 'Ziel_lat', 'Ziel_lon']).size().reset_index(name='Anzahl')

fig = go.Figure()

# A. FLUGROUTEN (Linien)
# Wir sortieren, damit die dicken Linien OBEN liegen
route_counts = route_counts.sort_values(by='Anzahl', ascending=True)

for index, row in route_counts.iterrows():
    # Logik für Liniendicke: 1 Flug = dünn, viele Flüge = sehr dick
    width = 0.5 + (row['Anzahl'] * 1.5) 
    # Logik für Farbe/Transparenz: Häufige Flüge leuchten stärker
    opacity = 0.4 + (min(row['Anzahl'], 5) * 0.1) 
    
    hover_txt = f"{row['Abflugort']} ➝ {row['Zielort']}<br>Anzahl: {row['Anzahl']}"
    
    fig.add_trace(go.Scattergeo(
        lon=[row['lon'], row['Ziel_lon']],
        lat=[row['lat'], row['Ziel_lat']],
        mode='lines',
        # Helle "Neon"-Farbe für Kontrast zum dunklen Globus
        line=dict(width=width, color='#FF4B4B'), 
        opacity=opacity,
        hoverinfo='text',
        text=hover_txt,
        name=f"{row['Anzahl']}x"
    ))

# B. FLUGHÄFEN (Design-Element: Goldene Diamanten)
all_lons = list(map_data['lon']) + list(map_data['Ziel_lon'])
all_lats = list(map_data['lat']) + list(map_data['Ziel_lat'])
all_texts = list(map_data['Abflugort']) + list(map_data['Zielort'])

# Einzigartige Flughäfen filtern
unique_airports = pd.DataFrame({'lon': all_lons, 'lat': all_lats, 'Ort': all_texts}).drop_duplicates()

# 1. Layer: Glow-Effekt (Großer, transparenter Punkt dahinter)
fig.add_trace(go.Scattergeo(
    lon=unique_airports['lon'],
    lat=unique_airports['lat'],
    mode='markers',
    marker=dict(size=15, color='#FFD700', opacity=0.3, symbol='circle'),
    hoverinfo='skip'
))

# 2. Layer: Der eigentliche Marker (Scharfer Diamant)
fig.add_trace(go.Scattergeo(
    lon=unique_airports['lon'],
    lat=unique_airports['lat'],
    text=unique_airports['Ort'],
    mode='markers',
    marker=dict(
        size=6, 
        color='#FFD700',      # Gold
        symbol='diamond',     # Design-Element
        line=dict(width=1, color='black') # Schwarzer Rand für Kontrast
    ),
    hoverinfo='text',
    name='Airports'
))

# C. GLOBUS LAYOUT (Satelliten/Dark-Mode Style)
fig.update_layout(
    height=750,
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor='rgba(0,0,0,0)', # Transparenter Hintergrund
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    geo=dict(
        projection_type="orthographic", # Echter 3D Globus
        showland=True,
        showlakes=True,
        showocean=True,
        showcountries=True,
        
        # FARBPALETTE "NIGHT SATELLITE"
        landcolor="rgb(20, 20, 20)",       # Fast schwarzes Land
        oceancolor="rgb(10, 10, 25)",      # Tiefblaues/Schwarzes Meer
        lakecolor="rgb(10, 10, 25)",
        countrycolor="rgb(60, 60, 60)",    # Dunkelgraue Grenzen
        coastlinecolor="rgb(100, 100, 100)", # Hellere Küstenlinien
        
        bgcolor='rgba(0,0,0,0)', # Kein weißer Kasten um den Globus
        resolution=50
    )
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("---")

# --- 5. Vergleich ---
st.header("⚖️ CO₂ Vergleich")
ratio = (total_emissions / CO2_INGOLSTADT_ANNUAL_TONS) * 100
df_comp = pd.DataFrame({
    'Quelle': ['Tom Cruise (2024)', 'Ingolstadt (Jahr)'],
    'CO2': [total_emissions, CO2_INGOLSTADT_ANNUAL_TONS]
})
fig_bar = px.bar(df_comp, x='Quelle', y='CO2', color='Quelle',
                 color_discrete_map={'Tom Cruise (2024)': '#FF4B4B', 'Ingolstadt (Jahr)': '#0083B8'})
st.plotly_chart(fig_bar, use_container_width=True)
st.info(f"Tom Cruise entspricht **{format_de(ratio, 4)}%** einer ganzen Stadt.")
st.markdown("---")

# --- 6. Statistiken ---
st.header("📈 Statistiken")
c1, c2 = st.columns(2)

with c1:
    st.subheader("Emissionen pro Monat")
    data['Monat'] = data['Datum'].dt.strftime('%Y-%m')
    monthly = data.groupby('Monat')['Emissionen (Metrische Tonnen)'].sum().reset_index()
    fig_m = px.bar(monthly, x='Monat', y='Emissionen (Metrische Tonnen)', 
                   color='Emissionen (Metrische Tonnen)', color_continuous_scale='Reds')
    st.plotly_chart(fig_m, use_container_width=True)

with c2:
    st.subheader("Top 5 Zielorte")
    top5 = data['Zielort'].value_counts().head(5).reset_index()
    top5.columns = ['Ort', 'Count']
    top5['Label'] = top5['Ort'].apply(lambda x: x.split('(')[0][:20] + "...")
    fig_t = px.bar(top5, x='Count', y='Label', orientation='h', color='Count', color_continuous_scale='Blues')
    fig_t.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_t, use_container_width=True)
