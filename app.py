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

# Zusätzliche Daten: Flughafennamen und Koordinaten
AIRPORT_NAMES = {
    'FXE': 'Fort Lauderdale Executive Airport', 'VNY': 'Van Nuys Airport', 'SUA': 'Witham Field (Stuart)',
    'CAK': 'Akron-Canton Airport', 'MRY': 'Monterey Regional Airport', 'APF': 'Naples Municipal Airport',
    'ASE': 'Aspen/Pitkin County Airport', 'APC': 'Napa County Airport', 'IND': 'Indianapolis International Airport',
    'LAX': 'Los Angeles International Airport', 'PSP': 'Palm Springs International Airport', 'SJC': 'San Jose International Airport',
    'PHL': 'Philadelphia International Airport', 'BOI': 'Boise Airport', 'SFB': 'Orlando Sanford International Airport',
    'SNA': 'John Wayne Airport (Orange County)', 'LAS': 'Harry Reid International Airport', 'TEB': 'Teterboro Airport',
    'ITH': 'Ithaca Tompkins International Airport', 'TWF': 'Magic Valley Regional Airport', 'SLC': 'Salt Lake City International Airport',
    'COE': 'Coeur d\'Alene Airport', 'JAX': 'Jacksonville International Airport', 'PBI': 'Palm Beach International Airport',
    'PNE': 'Northeast Philadelphia Airport', 'TPA': 'Tampa International Airport', 'SBP': 'San Luis Obispo County Regional Airport',
    'BNA': 'Nashville International Airport', 'FCM': 'Flying Cloud Airport', 'IAD': 'Dulles International Airport',
    'PVU': 'Provo Municipal Airport', 'HOU': 'William P. Hobby Airport', 'ISM': 'Kissimmee Gateway Airport',
    'APA': 'Centennial Airport (Denver)', 'EGE': 'Eagle County Regional Airport', 'YUL': 'Montréal–Trudeau International Airport (CAN)',
    'PWM': 'Portland International Jetport', 'SIG': 'Fernando Luis Ribas Dominicci Airport', 'LIR': 'Guanacaste Airport (Costa Rica)',
    'ATL': 'Hartsfield–Jackson Atlanta International Airport', 'BTR': 'Baton Rouge Metropolitan Airport', 'ORD': 'O’Hare International Airport',
    'CHA': 'Chattanooga Metropolitan Airport', 'MIA': 'Miami International Airport', 'LGA': 'LaGuardia Airport (NYC)',
    'MMU': 'Morristown Municipal Airport', 'PTK': 'Oakland County International Airport', '1B1': 'Columbia County Airport',
    'HPN': 'Westchester County Airport', 'DAL': 'Dallas Love Field', 'BCT': 'Boca Raton Airport',
    'STT': 'Cyril E. King Airport (St. Thomas)', 'SJU': 'Luis Muñoz Marín International Airport', 'FLL': 'Fort Lauderdale–Hollywood International Airport',
    'SAN': 'San Diego International Airport', 'UES': 'Waukesha County Airport', 'CID': 'The Eastern Iowa Airport',
    'MDW': 'Midway International Airport', 'BQK': 'Brunswick Golden Isles Airport', 'GCM': 'Owen Roberts International Airport (Cayman)',
    'RDU': 'Raleigh–Durham International Airport', 'SJT': 'San Angelo Regional Airport', 'SAT': 'San Antonio International Airport',
    'DEN': 'Denver International Airport', 'FNL': 'Northern Colorado Regional Airport', 'MYR': 'Myrtle Beach International Airport',
    'EYF': 'Curtis L. Brown Jr. Field', 'TRI': 'Tri-Cities Airport', 'BHM': 'Birmingham–Shuttlesworth International Airport',
    'ACK': 'Nantucket Memorial Airport', 'SLK': 'Adirondack Regional Airport', 'PGA': 'Page Municipal Airport',
    'SGR': 'Sugar Land Regional Airport', 'DVT': 'Deer Valley Airport (Phoenix)', 'PLN': 'Pellston Regional Airport',
    'BHB': 'Hancock County–Bar Harbor Airport', 'MHH': 'Marsh Harbour Airport (Bahamas)', 'OA9': 'Watauga County Airport',
    'BZN': 'Bozeman Yellowstone International Airport', 'FPR': 'St Lucie County International Airport', 'FIL': 'Faulkner County Airport',
    'HTH': 'Hawthorne Municipal Airport', 'CRQ': 'McClellan–Palomar Airport', 'MMSF': 'San Felipe International Airport',
    'MMSL': 'Los Cabos International Airport', 'MYES': 'Eleuthera Island Airport', 'MBAC': 'Matthew Town Airport',
    'PLS': 'Providenciales International Airport', 'ANU': 'V. C. Bird International Airport', 'OSU': 'Ohio State University Airport',
    'LCI': 'Laconia Municipal Airport', 'JZI': 'Charleston Executive Airport', 'SSI': 'Malcolm McKinnon Airport',
    'PPM': 'Pompano Beach Airpark', 'SLT': 'Salida Airport', 'CRE': 'Grand Strand Airport',
}

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
    df['Datum_str'] = df['Datum'].dt.strftime('%d.%m.%Y')

    df['Abflug_Code'] = df['Abflugort'].apply(extract_airport_code)
    df['Ziel_Code'] = df['Zielort'].apply(extract_airport_code)

    df['lat'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['lon'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    df['Ziel_lat'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['Ziel_lon'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    
    df['Abflug_Name'] = df['Abflug_Code'].apply(lambda x: AIRPORT_NAMES.get(x, x))
    df['Ziel_Name'] = df['Ziel_Code'].apply(lambda x: AIRPORT_NAMES.get(x, x))

    return df

try:
    data = load_data(CSV_FILE)
    total_flights = len(data)
    st.success(f"Daten erfolgreich geladen. {total_flights} Flüge aus 2024.")
except Exception as e:
    st.error(f"FEHLER: Die Datei '{CSV_FILE}' konnte nicht geladen werden oder ist ungültig. Details: {e}")
    st.stop()

def format_number_de(number, decimals=0):
    formatted = f"{number:,.{decimals}f}"
    formatted = formatted.replace(",", "|").replace(".", ",").replace("|", ".")
    return formatted

# --- 2. Kopfzeile und Statistische Kennzahlen (Statisch) ---
st.title("✈️ Privatjet-Tracker für Bonuspunkte")

col_img1, col_text, col_img2 = st.columns([1, 2, 1])
with col_text:
    st.header(f"Analyse der Privatjet-Flüge von Tom Cruise (2024)")
    st.markdown(f"Analysiert **{total_flights}** Privatjet-Flüge im Jahr 2024.")
    st.markdown("---")

# Platzhalter für Bilder
with col_img1:
    st.markdown("<!-- Bild 1 Placeholder -->")
with col_img2:
    st.markdown("<!-- Bild 2 Placeholder -->")

# Statistische Kennzahlen
total_distance = data['Distanz (Meilen)'].sum()
total_fuel = data['Treibstoffverbrauch (Gallons)'].sum()
total_emissions = data['Emissionen (Metrische Tonnen)'].sum()
avg_emissions_per_flight = data['Emissionen (Metrische Tonnen)'].mean()

st.header("📊 Statistische Kennzahlen")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Gesamtflüge", f"{total_flights}")
col2.metric("Gesamtdistanz (Meilen)", format_number_de(total_distance))
col3.metric("Treibstoff (Gallons)", format_number_de(total_fuel))
col4.metric("Emissionen (t CO₂)", format_number_de(total_emissions))
col5.metric("Ø Emission pro Flug", format_number_de(avg_emissions_per_flight, 1))

st.markdown("---")

# =====================================================================
# ======================== 3. Interaktive Flugverfolgung ================
# =====================================================================

st.header("🗓️ Interaktive Flugverfolgung (2024)")

# --- 3a. Kalender/Datumsauswahl ---
unique_dates = data['Datum_str'].unique()
selected_date_str = st.selectbox(
    "1. Flugdatum wählen (Kalender-Simulation):",
    options=unique_dates,
    index=0,
    help="Wählen Sie ein Datum, an dem Flüge stattfanden."
)

filtered_flights = data[data['Datum_str'] == selected_date_str].reset_index(drop=True)

# --- 3b. Flugauswahl ---
if not filtered_flights.empty:
    flight_options = [
        f"{row['Abflug_Name']} ({row['Abflug_Code']}) → {row['Ziel_Name']} ({row['Ziel_Code']})"
        for index, row in filtered_flights.iterrows()
    ]
    
    selected_flight_option = st.selectbox(
        f"2. Flug auf dem Datum ({selected_date_str}) wählen:",
        options=flight_options,
        index=0
    )
    
    # Ausgewählter Flug extrahieren
    selected_index = flight_options.index(selected_flight_option)
    flight_data = filtered_flights.iloc[selected_index]
    
    # --- 3c. Fortschrittsregler ---
    st.subheader(f"Flug: {flight_data['Abflug_Code']} → {flight_data['Ziel_Code']} am {selected_date_str}")
    progress = st.slider(
        "3. Fortschritt des Fluges (Flugzeug steuern):",
        min_value=0,
        max_value=100,
        value=0,
        step=1,
        format="%d %%"
    ) / 100.0
    
    # --- Berechnung der aktuellen Flugzeugposition (Interpolation) ---
    lat_start, lon_start = flight_data['lat'], flight_data['lon']
    lat_end, lon_end = flight_data['Ziel_lat'], flight_data['Ziel_lon']
    
    # Lineare Interpolation für die Position des Flugzeugs
    current_lat = lat_start + progress * (lat_end - lat_start)
    current_lon = lon_start + progress * (lon_end - lon_start)

    # --- 3d. Map Visualisierung ---
    fig = go.Figure()

    # 1. Die gesamte Flugbahn (Bogen)
    fig.add_trace(go.Scattergeo(
        lon=[lon_start, lon_end],
        lat=[lat_start, lat_end],
        mode="lines",
        line=dict(width=4, color='#FF4B4B'), # Rot für die aktive Bahn
        hoverinfo="text",
        text=selected_flight_option,
        name='Flugbahn'
    ))

    # 2. Startpunkt
    fig.add_trace(go.Scattergeo(
        lon=[lon_start], lat=[lat_start],
        mode='markers',
        marker=dict(size=10, color='darkgreen', symbol='circle'),
        hoverinfo='text',
        text=[f"Start: {flight_data['Abflug_Name']} ({flight_data['Abflug_Code']})"],
        name='Start'
    ))

    # 3. Zielpunkt (mit Richtung)
    fig.add_trace(go.Scattergeo(
        lon=[lon_end], lat=[lat_end],
        mode='markers',
        marker=dict(size=10, color='#0056B3', symbol='star'),
        hoverinfo='text',
        text=[f"Ziel: {flight_data['Ziel_Name']} ({flight_data['Ziel_Code']})"],
        name='Ziel'
    ))

    # 4. Flugzeugsymbol (Aktuelle Position)
    fig.add_trace(go.Scattergeo(
        lon=[current_lon], lat=[current_lat],
        mode='markers',
        marker=dict(
            size=15, 
            color='#333333', 
            symbol='triangle-up', 
            line=dict(width=1, color='white')
        ),
        hoverinfo='text',
        text=[f"Flugzeug: {int(progress*100)}%"],
        name='Aktuelle Position'
    ))

    # Globe-Konfiguration (Light Mode)
    fig.update_geos(
        projection_type="orthographic", # 3D-Globus für bogenförmige Linien
        showland=True,
        showcountries=True,
        landcolor="#F5F5F5",
        countrycolor="#CCCCCC",
        bgcolor="#FFFFFF",
        showocean=True,
        oceancolor="#E6F0FF"
    )

    # Automatische Zentrierung der Karte um den Flug
    center_lat = (lat_start + lat_end) / 2
    center_lon = (lon_start + lon_end) / 2
    
    fig.update_layout(
        height=700,
        title=f"Verfolgung des Fluges {flight_data['Abflug_Code']} → {flight_data['Ziel_Code']}",
        title_font_color="#333333",
        geo=dict(
            projection_rotation=dict(lon=-center_lon, lat=-center_lat, roll=0), 
            center=dict(lon=center_lon, lat=center_lat),
            scope='world'
        )
    )

    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("Für dieses Datum sind keine gültigen Flüge verfügbar.")


st.markdown("---")

# --- 4. Vergleichsanalyse ---
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
                 },
                 template='plotly_white')

st.plotly_chart(fig_bar, use_container_width=True)

st.success(f"Die Privatjet-Flüge entsprechen **{ratio_formatted}%** der jährlichen Emissionen von Ingolstadt.")

st.markdown("---")

# --- 5. Rohdaten ---
st.header("📋 Rohdaten")
st.dataframe(data)
