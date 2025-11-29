import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# ---------------------------------------------------
# --- 1. Streamlit Grundkonfiguration
# ---------------------------------------------------
st.set_page_config(layout="wide", page_title="Tom Cruise Jet Tracker (2024)", page_icon="✈️")

CSV_FILE = "tom_cruise_n350xx_flights.csv"
CO2_INGOLSTADT_ANNUAL_TONS = 1_800_000

# Mapbox Token
MAPBOX_TOKEN = "pk.eyJ1Ijoiam9yaXNzY2h3IiwiYSI6ImNtaWs3Zms3ajBtM2EzZ3M0MHViZ2k1c28ifQ.gbuhPm3JU40TRRzXKWThbw"
px.set_mapbox_access_token(MAPBOX_TOKEN)

# ---------------------------------------------------
# --- 2. Flughafen-Koordinaten
# ---------------------------------------------------
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
    'MMU': (40.799, -74.414), 'PTK': (42.668, -83.411), 'HPN': (41.067, -73.708),
    'DAL': (32.847, -96.852), 'BCT': (26.376, -80.100), 'STT': (18.337, -64.973),
    'SJU': (18.432, -66.002), 'FLL': (26.072, -80.153), 'SAN': (32.734, -117.182),
    'UES': (43.080, -88.196), 'CID': (41.884, -91.711), 'BQK': (31.258, -81.405),
    'GCM': (19.290, -81.358), 'RDU': (35.877, -78.789), 'SJT': (31.365, -100.505),
    'SAT': (29.534, -98.469), 'DEN': (39.862, -104.673), 'FNL': (40.451, -104.992),
    'MYR': (33.679, -78.928), 'EYF': (34.457, -78.618), 'TRI': (36.478, -82.408),
    'BHM': (33.565, -86.757), 'ACK': (41.253, -70.061), 'SLK': (44.409, -74.209),
    'PGA': (36.920, -111.455), 'SGR': (29.610, -95.660), 'DVT': (33.688, -112.072),
    'PLN': (45.340, -84.795), 'BHB': (44.452, -68.309), 'MHH': (26.541, -77.062),
    'OA9': (36.350, -82.167), 'BZN': (45.777, -111.157), 'FPR': (27.494, -80.840),
    'FIL': (38.966, -112.443), 'CRQ': (33.109, -117.279), 'MMSF': (31.000, -114.770),
    'MMSL': (22.956, -109.816), 'MYES': (24.160, -76.447), 'MBAC': (21.328, -71.558),
    'PLS': (21.777, -72.266), 'ANU': (17.136, -61.792), 'OSU': (40.076, -83.075),
    'LCI': (43.585, -71.428), 'JZI': (32.683, -80.053), 'SSI': (31.152, -81.391),
    'PPM': (26.236, -80.106), 'SLT': (38.530, -106.012), 'CRE': (33.805, -78.692)
}

# ---------------------------------------------------
# --- 3. Airport-Code aus Text extrahieren
# ---------------------------------------------------
def extract_airport_code(location_str):
    match = re.search(r"\(([^)]+)\)", str(location_str))
    return match.group(1).split()[-1] if match else None

# ---------------------------------------------------
# --- 4. CSV Laden + Geokoordinaten zuordnen
# ---------------------------------------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df.dropna(subset=["Datum"], inplace=True)
    df.sort_values("Datum", inplace=True)
    df["Flugnummer"] = np.arange(1, len(df)+1)

    df["Abflug_Code"] = df["Abflugort"].apply(extract_airport_code)
    df["Ziel_Code"] = df["Zielort"].apply(extract_airport_code)

    df["lat"] = df["Abflug_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None,None))[0])
    df["lon"] = df["Abflug_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None,None))[1])
    df["Ziel_lat"] = df["Ziel_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None,None))[0])
    df["Ziel_lon"] = df["Ziel_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None,None))[1])

    return df

data = load_data(CSV_FILE)
total_flights = len(data)

# ---------------------------------------------------
# --- 5. Titel & Bilder
# ---------------------------------------------------
st.title("✈️ Tom Cruise Privatjet-Tracker (2024)")
st.markdown(f"**{total_flights} Flüge** des Bombardier Challenger 350 N350XX im Jahr 2024.")

# ---------------------------------------------------
# --- 6. Satellitenkarte mit Great-Circle Routen
# ---------------------------------------------------
st.header("🌍 Satellitenkarte der Flugrouten (Great-Circle)")

valid = data.dropna(subset=["lat","lon","Ziel_lat","Ziel_lon"]).copy()
valid["Route"] = valid["Abflug_Code"] + " → " + valid["Ziel_Code"]

freq = valid["Route"].value_counts()
valid["freq"] = valid["Route"].map(freq)
valid["line_width"] = valid["freq"].apply(lambda f: 1 + f * 1.3)

fig_map = go.Figure()

# Flughäfen
fig_map.add_trace(go.Scattermapbox(
    lat=list(valid["lat"]) + list(valid["Ziel_lat"]),
    lon=list(valid["lon"]) + list(valid["Ziel_lon"]),
    mode="markers",
    marker=dict(size=9, color="#FFD700", opacity=0.9),
    hoverinfo="text",
    text=list(valid["Abflug_Code"]) + list(valid["Ziel_Code"]),
    name="Airports"
))

# Fluglinien (Great Circle)
for _, r in valid.iterrows():
    fig_map.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[r["lon"], r["Ziel_lon"]],
        lat=[r["lat"], r["Ziel_lat"]],
        line=dict(width=r["line_width"], color="red"),
        hoverinfo="text",
        text=f"{r['Route']} – {r['freq']}×",
        name="Route"
    ))

fig_map.update_layout(
    mapbox=dict(
        style="satellite-streets",
        center=dict(lat=20, lon=-20),
        zoom=1.3
    ),
    height=900,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig_map, use_container_width=True)

# ---------------------------------------------------
# --- 7. KPIs
# ---------------------------------------------------
st.header("📊 Statistische Kennzahlen")

def fmt(n): return f"{n:,.0f}".replace(",", ".")

total_distance = data["Distanz (Meilen)"].sum()
total_fuel = data["Treibstoffverbrauch (Gallons)"].sum()
total_em = data["Emissionen (Metrische Tonnen)"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gesamtflüge", total_flights)
col2.metric("Gesamtdistanz (Meilen)", fmt(total_distance))
col3.metric("Treibstoff (Gallons)", fmt(total_fuel))
col4.metric("CO₂-Emissionen (t)", fmt(total_em))

# ---------------------------------------------------
# --- 8. Rohdaten anzeigen
# ---------------------------------------------------
st.header("📋 Rohdaten")
st.dataframe(data)


