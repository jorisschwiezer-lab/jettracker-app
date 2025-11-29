import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# --- 1. Konfiguration und Daten laden ---
st.set_page_config(layout="wide", page_title="Tom Cruise Jet Tracker (2024)", page_icon="✈️")

CSV_FILE = 'tom_cruise_n350xx_flights.csv'
CO2_INGOLSTADT_ANNUAL_TONS = 1800000

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
    'PPM': (26.236, -80.106), 'SLT': (38.530, -106.012), 'CRE': (33.805, -78.692)
}

def extract_airport_code(location_str):
    match = re.search(r'\(([^)]+)\)', str(location_str))
    return match.group(1).split()[-1] if match else None

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    df.dropna(subset=['Datum'], inplace=True)
    df.sort_values(by='Datum', inplace=True)

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
    st.success(f"Daten erfolgreich geladen. {total_flights} Flüge aus 2024.")
except Exception as e:
    st.error(f"FEHLER: {e}")
    st.stop()

# --- 2. Seitentitel, Bilder und Einleitung ---
st.title("✈️ Privatjet-Tracker für Bonuspunkte")

col_img1, col_text, col_img2 = st.columns([1, 2, 1])

with col_img1:
    st.image("image-w856.jpg.webp", caption="Berühmtheit: Tom Cruise")

with col_text:
    st.header(f"Analyse der Privatjet-Flüge von Tom Cruise (2024)")
    st.markdown(f"Analysiert **{total_flights}** Privatjet-Flüge im Jahr 2024.")
    st.markdown("---")

with col_img2:
    st.image("Bild 2.jpeg", caption="Bombardier Challenger 350 (N350XX)")

st.markdown("---")

# --- 3. Statistische Kennzahlen ---
st.header("📊 Statistische Kennzahlen")

total_distance = data['Distanz (Meilen)'].sum()
total_fuel = data['Treibstoffverbrauch (Gallons)'].sum()
total_emissions = data['Emissionen (Metrische Tonnen)'].sum()
avg_emissions_per_flight = data['Emissionen (Metrische Tonnen)'].mean()

def format_number_de(number, decimals=0):
    formatted = f"{number:,.{decimals}f}"
    formatted = formatted.replace(",", "|").replace(".", ",").replace("|", ".")
    return formatted

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Gesamtflüge", f"{total_flights}")
col2.metric("Gesamtdistanz (Meilen)", format_number_de(total_distance))
col3.metric("Treibstoff (Gallons)", format_number_de(total_fuel))
col4.metric("Emissionen (t CO₂)", format_number_de(total_emissions))
col5.metric("Ø Emission pro Flug", format_number_de(avg_emissions_per_flight, 1))

st.markdown("---")

# =====================================================================
# ======================== 3D GLOBE – NEU ==============================
# =====================================================================

st.header("🌍 3D-Weltkarte der Flugbahnen")

valid = data.dropna(subset=["lat", "lon", "Ziel_lat", "Ziel_lon"]).copy()
valid["Route"] = valid["Abflug_Code"] + " → " + valid["Ziel_Code"]
route_counts = valid["Route"].value_counts()
valid["freq"] = valid["Route"].map(route_counts)

max_freq = valid["freq"].max()

fig = go.Figure()

for _, r in valid.iterrows():
    red = int(255 * (r["freq"] / max_freq))
    green = int(255 * (1 - r["freq"] / max_freq))
    blue = 0

    fig.add_trace(go.Scattergeo(
        lon=[r["lon"], r["Ziel_lon"]],
        lat=[r["lat"], r["Ziel_lat"]],
        mode="lines",
        line=dict(width=2, color=f"rgb({red},{green},{blue})"),
        hoverinfo="text",
        text=f"{r['Route']}<br>Geflogen: {r['freq']}×"
    ))

fig.update_geos(
    projection_type="orthographic",
    showland=True,
    showcountries=True,
    landcolor="lightgray",
    countrycolor="gray",
)

fig.update_layout(
    height=800,
    title="3D-Globus – Routenhäufigkeit (Grün → Rot)"
)

st.plotly_chart(fig, use_container_width=True)

st.info("🟩 Grün = einmal • 🟨 mittel • 🟥 oft")

st.markdown("---")

# --- 5. Vergleichsanalyse ---
st.header("⚖️ Vergleich mit einer Kleinstadt")

comparison_data = pd.DataFrame({
    'Quelle': ['Cruise-Flüge', 'Ingolstadt (jährlich)'],
    'CO2': [total_emissions, CO2_INGOLSTADT_ANNUAL_TONS]
})

ratio = (total_emissions / CO2_INGOLSTADT_ANNUAL_TONS) * 100
ratio_formatted = format_number_de(ratio, 4)

fig_bar = px.bar(comparison_data, x='Quelle', y='CO2',
                 color='Quelle',
                 color_discrete_map={
                     'Cruise-Flüge': '#FF4B4B',
                     'Ingolstadt (jährlich)': '#0083B8'
                 })

st.plotly_chart(fig_bar, use_container_width=True)

st.success(f"Die Privatjet-Flüge entsprechen **{ratio_formatted}%** der jährlichen Emissionen von Ingolstadt.")

st.markdown("---")

# --- 6. Rohdaten ---
st.header("📋 Rohdaten")
st.dataframe(data)
