import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Tom Cruise Flug-Statistik 2024",
    page_icon="✈️",
    layout="wide"
)

# --- 2. DATEN & KONSTANTEN ---
CSV_FILE = 'tom_cruise_n350xx_flights.csv'

# Erweiterte Koordinaten-Liste basierend auf deinen Daten
# (Ich habe internationale Ziele wie Kapstadt, Cancun, etc. hinzugefügt)
AIRPORT_COORDINATES = {
    'TPA': (27.975, -82.533), 'SBP': (35.237, -120.642), 'SFO': (37.619, -122.375),
    'FXE': (26.197, -80.171), 'SLC': (40.788, -111.978), 'CUN': (21.036, -86.877),
    'PNE': (40.082, -75.011), 'PSP': (33.829, -116.507), 'LAX': (33.942, -118.407),
    'TEB': (40.850, -74.061), 'LAS': (36.080, -115.152), 'VDI': (32.193, -82.371),
    'ISM': (28.289, -81.437), 'APA': (39.570, -104.849), 'EGE': (39.640, -106.918),
    'ASE': (39.223, -106.869), 'ANU': (17.137, -61.793), 'TWF': (42.482, -114.485),
    'PBI': (26.683, -80.096), 'STL': (38.748, -90.370), 'APF': (26.152, -81.775),
    'BZN': (45.777, -111.152), 'YUL': (45.470, -73.741), 'PHL': (39.872, -75.241),
    'RIL': (39.542, -107.720), 'HOU': (29.645, -95.279), 'CAK': (40.916, -81.442),
    'MRY': (36.587, -121.856), 'DPA': (41.907, -88.248), 'SAT': (29.534, -98.470),
    'SJT': (31.358, -100.496), 'RDU': (35.878, -78.788), 'BQK': (31.259, -81.466),
    'GCM': (19.292, -81.359), 'PIR': (44.383, -100.286), 'CHA': (35.035, -85.204),
    'BNA': (36.124, -86.678), 'COE': (47.774, -116.828), 'MYR': (33.679, -78.928),
    'BCT': (26.378, -80.107), 'FNL': (40.452, -105.011), 'TRI': (36.475, -82.407),
    'HPN': (41.067, -73.708), 'PVU': (40.219, -111.723), 'SJC': (37.362, -121.929),
    'FLL': (26.072, -80.153), 'EYF': (34.601, -78.579), 'MIA': (25.793, -80.291),
    'ACK': (41.253, -70.060), 'LGA': (40.777, -73.872), 'MHH': (26.511, -77.083),
    'DAL': (32.847, -96.852), 'SIG': (18.457, -66.098), 'BOS': (42.364, -71.005),
    'MBJ': (18.504, -77.913), 'STT': (18.337, -64.973), 'SJU': (18.439, -66.002),
    'PWM': (43.646, -70.309), 'PWK': (42.114, -87.901), 'SLK': (44.385, -74.206),
    'ATL': (33.636, -84.428), 'LIR': (10.593, -85.544), 'VNY': (34.209, -118.490),
    'SUA': (27.182, -80.221), 'JAX': (30.494, -81.688), 'AUS': (30.194, -97.670),
    'APC': (38.213, -122.281), 'TVC': (44.741, -85.582), 'PGA': (36.926, -111.448),
    'MKC': (39.123, -94.594), 'PIT': (40.491, -80.233), 'ORD': (41.978, -87.905),
    'FCM': (44.827, -93.457), 'BTR': (30.533, -91.150), 'OA9': (36.371, -82.173),
    'SPA': (34.916, -81.957), 'MMU': (40.799, -74.415), 'MDW': (41.786, -87.752),
    'UES': (43.041, -88.237), 'POP': (19.758, -70.570), 'DVT': (33.688, -112.082),
    'BOI': (43.564, -116.223), 'SFB': (28.777, -81.237), 'BHB': (44.449, -68.361),
    'PLN': (45.571, -84.797), 'IND': (39.717, -86.294), 'SNA': (33.675, -117.868),
    'CPT': (-33.964, 18.601), 'NAS': (25.039, -77.466), 'AZS': (19.272, -69.737),
    'FOK': (40.843, -72.632), 'DRO': (37.151, -107.754), 'IAD': (38.944, -77.456),
    'JZI': (32.700, -80.005), '181': (42.291, -73.710), 'CID': (41.884, -91.710),
    'SAN': (32.733, -117.189), 'ITH': (42.491, -76.458)
}

# --- 3. FUNKTIONEN ---

def extract_airport_code(location_str):
    """Extrahiert den Code aus Strings wie 'Tampa International Airport (TPA) Florida'"""
    if not isinstance(location_str, str):
        return None
    # Suche nach Muster (XYZ) oder (123)
    match = re.search(r'\(([A-Z0-9]{3,4})\)', location_str)
    if match:
        return match.group(1)
    return None

@st.cache_data
def load_data():
    try:
        # CSV einlesen
        df = pd.read_csv(CSV_FILE)
        
        # Datumsformat bereinigen
        df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
        df = df.dropna(subset=['Datum']).sort_values(by='Datum')
        
        # Numerische Spalten bereinigen (falls Strings enthalten sind)
        cols_to_numeric = ['Distanz (Meilen)', 'Emissionen (Metrische Tonnen)']
        for col in cols_to_numeric:
            if df[col].dtype == object:
                # Entferne Tausendertrennzeichen falls nötig
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)

        # Codes extrahieren
        df['Start_Code'] = df['Abflugort'].apply(extract_airport_code)
        df['Ziel_Code'] = df['Zielort'].apply(extract_airport_code)

        # Koordinaten zuordnen
        def get_lat(code): return AIRPORT_COORDINATES.get(code, (None, None))[0]
        def get_lon(code): return AIRPORT_COORDINATES.get(code, (None, None))[1]

        df['Start_Lat'] = df['Start_Code'].apply(get_lat)
        df['Start_Lon'] = df['Start_Code'].apply(get_lon)
        df['Ziel_Lat'] = df['Ziel_Code'].apply(get_lat)
        df['Ziel_Lon'] = df['Ziel_Code'].apply(get_lon)

        return df
    except Exception as e:
        return str(e)

# --- 4. HAUPTPROGRAMM ---

# Daten laden
data = load_data()

if isinstance(data, str):
    st.error(f"Fehler beim Laden der Datei: {data}")
    st.info("Bitte stelle sicher, dass die Datei 'tom_cruise_n350xx_flights.csv' im gleichen Ordner liegt.")
else:
    # --- DASHBOARD LAYOUT ---
    
    st.title("📊 Statistik-Projekt: Tom Cruise Jet Tracker")
    st.markdown("Analyse der Flugbewegungen der **Bombardier Challenger 350 (N350XX)** im Jahr 2024.")

    # KPIs (Key Performance Indicators)
    total_flights = len(data)
    total_miles = data['Distanz (Meilen)'].sum()
    total_co2 = data['Emissionen (Metrische Tonnen)'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Anzahl Flüge", total_flights)
    col2.metric("Gesamtdistanz", f"{total_miles:,.0f} Meilen".replace(",", "."))
    col3.metric("CO₂ Ausstoß", f"{total_co2:,.1f} Tonnen".replace(".", ","))
    col4.metric("Ø CO₂ pro Flug", f"{total_co2/total_flights:.2f} Tonnen".replace(".", ","))

    st.markdown("---")

    # --- INTERAKTIVE KARTE (3D GLOBUS) ---
    st.subheader("🌍 Globale Flugrouten")
    
    # Filtere ungültige Koordinaten heraus für die Karte
    map_data = data.dropna(subset=['Start_Lat', 'Start_Lon', 'Ziel_Lat', 'Ziel_Lon'])
    
    fig_map = go.Figure()

    # Fluglinien zeichnen
    for i, row in map_data.iterrows():
        fig_map.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[row['Start_Lon'], row['Ziel_Lon']],
            lat=[row['Start_Lat'], row['Ziel_Lat']],
            mode='lines',
            line=dict(width=1, color='red'),
            opacity=0.6,
            hoverinfo='text',
            text=f"{row['Datum'].strftime('%d.%m.')}: {row['Abflugort']} -> {row['Zielort']}"
        ))

    # Flughäfen als Punkte
    all_lons = list(map_data['Start_Lon']) + list(map_data['Ziel_Lon'])
    all_lats = list(map_data['Start_Lat']) + list(map_data['Ziel_Lat'])
    all_texts = list(map_data['Abflugort']) + list(map_data['Zielort'])

    fig_map.add_trace(go.Scattergeo(
        lon=all_lons,
        lat=all_lats,
        hoverinfo='text',
        text=all_texts,
        mode='markers',
        marker=dict(size=4, color='blue')
    ))

    fig_map.update_layout(
        title_text='Flugbewegungen 2024 (Orthografische Projektion)',
        showlegend=False,
        geo=dict(
            projection_type="orthographic",
            showland=True,
            landcolor="lightgray",
            oceancolor="azure",
            showocean=True,
            coastlinecolor="white"
        ),
        height=600,
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # --- DIAGRAMME ---
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📅 Emissionen pro Monat")
        data['Monat'] = data['Datum'].dt.strftime('%Y-%m')
        monthly_emissions = data.groupby('Monat')['Emissionen (Metrische Tonnen)'].sum().reset_index()
        
        fig_bar = px.bar(
            monthly_emissions, 
            x='Monat', 
            y='Emissionen (Metrische Tonnen)',
            color='Emissionen (Metrische Tonnen)',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🏆 Top 5 Zielorte")
        top_dest = data['Zielort'].value_counts().head(5).reset_index()
        top_dest.columns = ['Ort', 'Anzahl']
        # Wir kürzen die langen Namen für das Diagramm
        top_dest['Ort_Kurz'] = top_dest['Ort'].apply(lambda x: x.split('(')[0][:20] + "...")
        
        fig_pie = px.pie(
            top_dest, 
            values='Anzahl', 
            names='Ort_Kurz', 
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- ROHDATEN ---
    with st.expander("📋 Detaillierte Flugliste ansehen"):
        st.dataframe(data[['Datum', 'Abflugort', 'Zielort', 'Distanz (Meilen)', 'Emissionen (Metrische Tonnen)']])
