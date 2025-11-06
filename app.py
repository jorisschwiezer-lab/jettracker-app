import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go # NEU: Für die Kartenlinien benötigt
import re # KORRIGIERT: Fehlender Import für reguläre Ausdrücke
from datetime import datetime

# --- 1. Konfiguration und Daten laden ---
# Das Layout der Seite auf "wide" setzen
st.set_page_config(layout="wide", page_title="Tom Cruise Jet Tracker (2024)", page_icon="✈️")

# Name der CSV-Datei (Daten aus 2024)
CSV_FILE = 'tom_cruise_n350xx_flights.csv'

# Konstante für den CO2-Vergleich (Jährliche CO2-Emissionen der Vergleichsstadt)
CO2_INGOLSTADT_ANNUAL_TONS = 1800000

# Dictionary mit den geokodierten Koordinaten der Flughäfen
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

# Funktion zum Extrahieren des Airport-Codes aus dem Ort-String
def extract_airport_code(location_str):
    # Sucht nach Text in Klammern und nimmt den letzten Teil als Code
    match = re.search(r'\(([^)]+)\)', str(location_str))
    return match.group(1).split()[-1] if match else None

# Funktion zum Laden und Vorbereiten der Daten
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Datenbereinigung und Typkonvertierung
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
    df.dropna(subset=['Datum'], inplace=True)
    df.sort_values(by='Datum', inplace=True)

    # Berechne die Flugnummer
    df['Flugnummer'] = np.arange(1, len(df) + 1)

    # --- HIER ERFOLGT DIE GEOKODIERUNG ---
    # Erzeuge Spalten für die Airport Codes
    df['Abflug_Code'] = df['Abflugort'].apply(extract_airport_code)
    df['Ziel_Code'] = df['Zielort'].apply(extract_airport_code)

    # Ordne Längen- und Breitengrade zu (falls Code bekannt)
    df['lat'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['lon'] = df['Abflug_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    df['Ziel_lat'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[0])
    df['Ziel_lon'] = df['Ziel_Code'].apply(lambda x: AIRPORT_COORDINATES.get(x, (None, None))[1])
    
    # Für die Karte benötigen wir alle Punkte (Abflug und Ziel) in einer langen Liste
    flight_lines = []
    for index, row in df.iterrows():
        # Abflugort (Startpunkt der Linie)
        flight_lines.append({
            'Flugnummer': row['Flugnummer'],
            'Ort': row['Abflugort'],
            'lat': row['lat'],
            'lon': row['lon'],
            'Typ': 'Start',
            'Datum': row['Datum']
        })
        # Zielort (Endpunkt der Linie)
        flight_lines.append({
            'Flugnummer': row['Flugnummer'],
            'Ort': row['Zielort'],
            'lat': row['Ziel_lat'],
            'lon': row['Ziel_lon'],
            'Typ': 'Ziel',
            'Datum': row['Datum']
        })

    df_map = pd.DataFrame(flight_lines).dropna(subset=['lat', 'lon'])


    return df, df_map

# Daten laden
try:
    data, map_data = load_data(CSV_FILE)
    total_flights = len(data)
    if map_data.empty:
         st.error("FEHLER: Konnte keine gültigen Koordinaten finden. Karte kann nicht dargestellt werden. Überprüfen Sie, ob die Flughafen-Codes in der AIRPORT_COORDINATES-Liste vorhanden sind.")
         st.stop()
    st.success(f"Daten erfolgreich geladen. {total_flights} Flüge aus 2024.")
except FileNotFoundError:
    st.error(f"FEHLER: Die Datei '{CSV_FILE}' wurde nicht gefunden. Bitte prüfen Sie den Dateinamen und den Pfad im GitHub-Repository.")
    st.stop()
except Exception as e:
    st.error(f"FEHLER beim Laden oder Verarbeiten der Daten: {e}")
    st.stop()


# --- 2. Seitentitel, Bilder und Einleitung ---
st.title("✈️ Privatjet-Tracker für Bonuspunkte")

col_img1, col_text, col_img2 = st.columns([1, 2, 1])

with col_img1:
    st.image("image-w856.jpg.webp", caption="Berühmtheit: Tom Cruise")

with col_text:
    st.header(f"Analyse der Privatjet-Flüge von Tom Cruise (2024)")
    st.markdown(f"Analysiert **{total_flights}** Privatjet-Flüge von Tom Cruise (Bombardier Challenger 350 N350XX) im Jahr 2024.")
    st.markdown("---")

with col_img2:
    st.image("Bild 2.jpeg", caption="Flugzeugtyp: Bombardier Challenger 350 (N350XX)")

st.markdown("---")


# --- 3. Statistische Kennzahlen (KPIs) (Zahlenformat geändert) ---
st.header("📊 Statistische Kennzahlen")

# Berechne Kennzahlen
total_distance = data['Distanz (Meilen)'].sum()
total_fuel = data['Treibstoffverbrauch (Gallons)'].sum()
total_emissions = data['Emissionen (Metrische Tonnen)'].sum()
avg_emissions_per_flight = data['Emissionen (Metrische Tonnen)'].mean()

# Hilfsfunktion für die Formatierung (Punkt als Tausendertrenner, Komma als Dezimaltrennzeichen)
def format_number_de(number, decimals=0):
    if pd.isna(number):
        return ""
    # Verwende String-Formatierung für Tausendertrenner und ersetze dann Komma durch Punkt
    formatted = f"{number:,.{decimals}f}"
    
    # 1. Ersetze Komma (Dezimaltrennzeichen in US-Formatierung) durch temporäres Zeichen (z.B. Pipe)
    formatted = formatted.replace(",", "|")
    # 2. Ersetze Punkt (Tausendertrennzeichen in US-Formatierung) durch Komma
    formatted = formatted.replace(".", ",")
    # 3. Ersetze temporäres Zeichen durch Punkt (Dezimaltrennzeichen in DE-Formatierung)
    formatted = formatted.replace("|", ".")
    return formatted

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Gesamtflüge (2024)", value=f"{total_flights}")

with col2:
    st.metric(label="Gesamtdistanz (Meilen)", value=format_number_de(total_distance))

with col3:
    st.metric(label="Gesamter Treibstoff (Gallons)", value=format_number_de(total_fuel))

with col4:
    st.metric(label="Gesamtemissionen (Metr. Tonnen CO₂)", value=format_number_de(total_emissions))

with col5:
    st.metric(label="Ø Emission pro Flug (Tonnen CO₂)", value=format_number_de(avg_emissions_per_flight, decimals=1))

st.markdown("---")

# --- 4. Interaktive Karte mit Schieberegler (Karte an Koordinaten angepasst) ---
st.header("📍 Flugbahn auf der Karte")
st.markdown("Nutzen Sie den **Schieberegler**, um die Flüge sukzessive darzustellen und die Flugbahn zu verfolgen.")

# Schieberegler für die Flugnummer (sukzessive Darstellung)
max_flight = data['Flugnummer'].max()
flight_slider = st.slider(
    'Flüge bis zur Nummer:',
    min_value=1,
    max_value=max_flight,
    value=max_flight,
    step=1
)

# Daten für die Karte filtern
filtered_map_data = map_data[map_data['Flugnummer'] <= flight_slider]
filtered_data = data[data['Flugnummer'] <= flight_slider]
latest_flight = filtered_data.iloc[-1] if not filtered_data.empty else None

fig = go.Figure()

# Fügen Sie die Fluglinien hinzu (gruppiert nach Flugnummer)
for flight_num in filtered_map_data['Flugnummer'].unique():
    segment = filtered_map_data[filtered_map_data['Flugnummer'] == flight_num]
    if len(segment) >= 2: # Muss mindestens Start- und Zielpunkt haben
        # Fügt die Fluglinie hinzu
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=segment['lon'],
            lat=segment['lat'],
            name=f"Flug {flight_num}",
            line=dict(width=2, color='red'),
            hoverinfo='text',
            text=f"Flug {flight_num}: {segment.iloc[0]['Ort']} -> {segment.iloc[-1]['Ort']}",
        ))

# Füge die Flughafen-Punkte hinzu (alle Punkte, die im gefilterten Segment liegen)
fig.add_trace(go.Scattermapbox(
    mode="markers",
    lon=filtered_map_data['lon'],
    lat=filtered_map_data['lat'],
    marker={'size': 8, 'color': 'blue'},
    name='Flughäfen',
    hoverinfo='text',
    text=filtered_map_data['Ort']
))

# Kartenlayout aktualisieren
fig.update_layout(
    mapbox_style="open-street-map",
    hovermode='closest',
    margin={"r":0,"t":0,"l":0,"b":0},
    mapbox=dict(
        bearing=0,
        center=dict(
            lat=map_data['lat'].mean(),
            lon=map_data['lon'].mean()
        ),
        pitch=0,
        zoom=2.5
    )
)

st.plotly_chart(fig, use_container_width=True)

if latest_flight is not None and pd.notna(latest_flight['Datum']):
    st.info(f"""
        **Aktueller Flug (Nr. {latest_flight['Flugnummer']}):**
        * **Datum:** {latest_flight['Datum'].strftime('%d.%m.%Y')}
        * **Route:** {latest_flight['Abflugort']} → {latest_flight['Zielort']}
        * **Emissionen:** {format_number_de(latest_flight['Emissionen (Metrische Tonnen)'], decimals=1)} metrische Tonnen CO₂
    """)

st.markdown("---")

# --- 5. Vergleichsanalyse (Zahlenformat und Text angepasst) ---
st.header("⚖️ Vergleich mit einer mittleren deutschen Kleinstadt")
st.markdown(f"Hier stellen wir die **Gesamt-Jahres-CO₂-Emissionen (2024)** der {total_flights} Privatjet-Flüge in Relation zum geschätzten **jährlichen** CO₂-Ausstoß der **mittleren deutschen Kleinstadt Ingolstadt** (Platzhalterwert: $1.800.000$ Tonnen).")

# Erzeuge einen DataFrame für das Balkendiagramm
comparison_data = pd.DataFrame({
    'Quelle': [
        'Tom Cruise Privatjet-Flüge (2024 Gesamt)',
        'Geschätzter CO₂-Ausstoß Ingolstadt (Jährlich)'
    ],
    'CO2 Emissionen (Metrische Tonnen)': [
        total_emissions,
        CO2_INGOLSTADT_ANNUAL_TONS
    ]
})

# Verhältnis berechnen
ratio = (total_emissions / CO2_INGOLSTADT_ANNUAL_TONS) * 100
ratio_formatted = format_number_de(ratio, decimals=4)

st.subheader("Balkendiagramm: CO₂-Emissionen im Jahresvergleich")
fig_bar = px.bar(
    comparison_data,
    x='Quelle',
    y='CO2 Emissionen (Metrische Tonnen)',
    color='Quelle',
    color_discrete_map={
        'Tom Cruise Privatjet-Flüge (2024 Gesamt)': '#FF4B4B',
        'Geschätzter CO₂-Ausstoß Ingolstadt (Jährlich)': '#0083B8'
    },
    labels={'CO2 Emissionen (Metrische Tonnen)':'CO₂-Emissionen (Metrische Tonnen)'}
)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Verhältnis")
st.success(
    f"Die Gesamt-CO₂-Emissionen der {total_flights} Privatjet-Flüge von Tom Cruise (2024) "
    f"entsprechen **{ratio_formatted}%** des geschätzten jährlichen CO₂-Ausstoßes von Ingolstadt."
)

st.markdown("---")

# --- 6. Datenvorschau ---
st.header("📋 Rohdaten")
st.dataframe(data)

# --- ENDE DES STREAMLIT-CODES ---
