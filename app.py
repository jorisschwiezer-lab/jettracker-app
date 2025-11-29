import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re

# ---------------------------------------------------
# --- 1. Streamlit Einstellungen (Heller Modus)
# ---------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="Tom Cruise Jet Tracker (2024)",
    page_icon="✈️",
    initial_sidebar_state="expanded"
)

# HELLES Layout erzwingen
st.markdown("""
    <style>
        body { background-color: #F7F7F7 !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# --- 2. Mapbox Token
# ---------------------------------------------------
MAPBOX_TOKEN = "pk.eyJ1Ijoiam9yaXNzY2h3IiwiYSI6ImNtaWs3Zms3ajBtM2EzZ3M0MHViZ2k1c28ifQ.gbuhPm3JU40TRRzXKWThbw"
px.set_mapbox_access_token(MAPBOX_TOKEN)

# ---------------------------------------------------
# --- 3. CSV Pfad
# ---------------------------------------------------
CSV_FILE = "tom_cruise_n350xx_flights.csv"
CO2_INGOLSTADT_ANNUAL_TONS = 1_800_000

# ---------------------------------------------------
# --- 4. Flughafen-Koordinaten
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
    'BHM': (33.565, -86.757), 'ACK': (41.253, -70.061), 'SLK': (44.409, -74.209)
}

# ---------------------------------------------------
# --- 5. Airport-Code extrahieren
# ---------------------------------------------------
def extract_airport_code(text):
    match = re.search(r"\(([^)]+)\)", str(text))
    return match.group(1).split()[-1] if match else None

# ---------------------------------------------------
# --- 6. CSV laden + Koordinaten zuordnen
# ---------------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y", errors="coerce")
    df.dropna(subset=["Datum"], inplace=True)
    df.sort_values("Datum", inplace=True)

    df["Flugnummer"] = np.arange(1, len(df)+1)
    df["Abflug_Code"] = df["Abflugort"].apply(extract_airport_code)
    df["Ziel_Code"] = df["Zielort"].apply(extract_airport_code)

    df["lat"]      = df["Abflug_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None, None))[0])
    df["lon"]      = df["Abflug_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None, None))[1])
    df["Ziel_lat"] = df["Ziel_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None, None))[0])
    df["Ziel_lon"] = df["Ziel_Code"].apply(lambda c: AIRPORT_COORDINATES.get(c, (None, None))[1])

    return df

data = load_data(CSV_FILE)

# ---------------------------------------------------
# --- 7. Titel
# ---------------------------------------------------
st.title("✈️ Tom Cruise Privatjet-Tracker 2024 (Satellitenkarte)")

# ---------------------------------------------------
# --- 8. Great Circle Weltkarte
# ---------------------------------------------------

st.header("🌍 Weltkarte der Flugrouten (Great-Circle)")

valid = data.dropna(subset=["lat","lon","Ziel_lat","Ziel_lon"]).copy()
valid["Route"] = valid["Abflug_Code"] + " → " + valid["Ziel_Code"]

freq = valid["Route"].value_counts()
valid["freq"] = valid["Route"].map(freq)
valid["line_width"] = valid["freq"].apply(lambda f: 1 + f * 1.4)

fig = go.Figure()

# Flughäfen
fig.add_trace(go.Scattermapbox(
    lat=list(valid["lat"]) + list(valid["Ziel_lat"]),
    lon=list(valid["lon"]) + list(valid["Ziel_lon"]),
    mode="markers",
    marker=dict(size=10, color="yellow", opacity=0.9),
    hoverinfo="text",
    text=list(valid["Abflug_Code"]) + list(valid["Ziel_Code"]),
    name="Airports"
))

# Routen
for _, r in valid.iterrows():
    fig.add_trace(go.Scattermapbox(
        mode="lines",
        lon=[r["lon"], r["Ziel_lon"]],
        lat=[r["lat"], r["Ziel_lat"]],
        line=dict(width=r["line_width"], color="red"),
        hoverinfo="text",
        text=f"{r['Route']} – {r['freq']}×",
        name="Route"
    ))

fig.update_layout(
    mapbox=dict(
        style="satellite-streets",
        center=dict(lat=20, lon=-20),
        zoom=1.3
    ),
    height=900,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# --- 9. KPIs
# ---------------------------------------------------
st.header("📊 Statistische Kennzahlen")

col1, col2, col3 = st.columns(3)

col1.metric("Gesamtflüge", len(data))
col2.metric("Distanz (Meilen)", f"{data['Distanz (Meilen)'].sum():,.0f}".replace(",", "."))
col3.metric("CO₂-Emissionen (t)", f"{data['Emissionen (Metrische Tonnen)'].sum():,.0f}".replace(",", "."))

# ---------------------------------------------------
# --- 10. Rohdaten
# ---------------------------------------------------
st.header("📋 Rohdaten")
st.dataframe(data)


