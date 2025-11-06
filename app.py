import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. Konfiguration und Daten laden ---
# Das Layout der Seite auf "wide" setzen
st.set_page_config(layout="wide", page_title="Tom Cruise Jet Tracker (2025)", page_icon="✈️")

# Name der CSV-Datei (muss im selben Ordner wie diese App sein)
CSV_FILE = 'tom_cruise_n350xx_flights.csv'

# Konstante für den CO2-Vergleich (monatliche CO2-Emissionen der Vergleichsstadt)
CO2_INGOLSTADT_MONTHLY_TONS = 150000

# Funktion zum Laden und Vorbereiten der Daten (Unverändert)
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Datenbereinigung und Typkonvertierung
    def parse_date(date_str):
        for fmt in ('%m/%d/%Y', '%m/%d/%y', '%d.%m.%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(str(date_str), fmt)
            except (ValueError, TypeError):
                continue
        return pd.NaT

    df['Datum'] = df['Datum'].apply(parse_date)
    df.dropna(subset=['Datum'], inplace=True)
    df.sort_values(by='Datum', inplace=True)

    df['Distanz (Meilen)'] = df['Distanz (Meilen)'].str.replace(' miles', '', regex=False).str.replace(',', '', regex=False).astype(float, errors='ignore')
    df['Flugnummer'] = np.arange(1, len(df) + 1)

    # Füge Platzhalter für geokodierte Koordinaten hinzu (für die Karte erforderlich)
    df['lat'] = np.random.uniform(25, 35, len(df))
    df['lon'] = np.random.uniform(-120, -75, len(df))

    return df

# Daten laden
try:
    data = load_data(CSV_FILE)
    st.success(f"Daten erfolgreich geladen. {len(data)} Flüge aus 2025.")
except FileNotFoundError:
    st.error(f"FEHLER: Die Datei '{CSV_FILE}' wurde nicht gefunden. Bitte prüfen Sie den Dateinamen und den Pfad im GitHub-Repository.")
    st.stop()
except Exception as e:
    st.error(f"FEHLER beim Laden oder Verarbeiten der Daten: {e}")
    st.stop()


# --- 2. Seitentitel, Bilder und Einleitung (NEU & GEÄNDERT) ---
st.title("✈️ Privatjet-Tracker für Bonuspunkte")

# Füge die Bilder der Berühmtheit und des Jets hinzu
col_img1, col_text, col_img2 = st.columns([1, 2, 1])

with col_img1:
    # Bild der Berühmtheit
    st.image("image-w856.jpg.webp", caption="Berühmtheit: Tom Cruise")

with col_text:
    st.header("Analyse der Privatjet-Flüge von Tom Cruise (Q1 2025)")
    st.markdown("Analysiert 43 Privatjet-Flüge von Tom Cruise im ersten Quartal 2025.")
    st.markdown("---")

with col_img2:
    # Bild des Jets und Name
    st.image("Bild 2.jpeg", caption="Flugzeugtyp: Bombardier Challenger 350 (N350XX)")

st.markdown("---")


# --- 3. Statistische Kennzahlen (KPIs) (Unverändert) ---
st.header("📊 Statistische Kennzahlen")

# Berechne Kennzahlen
total_flights = len(data)
total_distance = data['Distanz (Meilen)'].sum()
total_fuel = data['Treibstoffverbrauch (Gallons)'].sum()
total_emissions = data['Emissionen (Metrische Tonnen)'].sum()
avg_emissions_per_flight = data['Emissionen (Metrische Tonnen)'].mean()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="Gesamtflüge (Q1 2025)", value=f"{total_flights}")

with col2:
    st.metric(label="Gesamtdistanz (Meilen)", value=f"{total_distance:,.0f}")

with col3:
    st.metric(label="Gesamter Treibstoff (Gallons)", value=f"{total_fuel:,.0f}")

with col4:
    st.metric(label="Gesamtemissionen (Metr. Tonnen CO₂)", value=f"{total_emissions:,.0f}")

with col5:
    st.metric(label="Ø Emission pro Flug (Tonnen CO₂)", value=f"{avg_emissions_per_flight:,.1f}")

st.markdown("---")

# --- 4. Interaktive Karte mit Schieberegler (Unverändert) ---
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

# Daten filtern basierend auf dem Schieberegler-Wert
filtered_data = data[data['Flugnummer'] <= flight_slider]
latest_flight = filtered_data.iloc[-1] if not filtered_data.empty else None

# Karte erstellen
fig = px.scatter_mapbox(
    filtered_data,
    lat="lat",
    lon="lon",
    hover_name="Abflugort",
    hover_data={
        "Datum": "|%Y-%m-%d",
        "Abflugort": True,
        "Zielort": True,
        "Emissionen (Metrische Tonnen)": ':,1f',
        "lat": False,
        "lon": False
    },
    color_discrete_sequence=["fuchsia"],
    zoom=2.5,
    height=500
)

# Kartenstil anpassen (OpenStreetMap)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)

if latest_flight is not None:
    st.info(f"""
        **Aktueller Flug (Nr. {latest_flight['Flugnummer']}):**
        * **Datum:** {latest_flight['Datum'].strftime('%d.%m.%Y')}
        * **Route:** {latest_flight['Abflugort']} → {latest_flight['Zielort']}
        * **Emissionen:** {latest_flight['Emissionen (Metrische Tonnen)']:.1f} metrische Tonnen CO₂
    """)

st.markdown("---")

# --- 5. Vergleichsanalyse (Unverändert) ---
st.header("⚖️ Vergleich mit einer mittleren deutschen Kleinstadt")
st.markdown(f"Hier stellen wir die Gesamt-CO₂-Emissionen der **43 Privatjet-Flüge** in Relation zum geschätzten monatlichen CO₂-Ausstoß der **mittleren deutschen Kleinstadt Ingolstadt** (Platzhalterwert: {CO2_INGOLSTADT_MONTHLY_TONS:,.0f} Tonnen).")

# Erzeuge einen DataFrame für das Balkendiagramm
comparison_data = pd.DataFrame({
    'Quelle': [
        'Tom Cruise Privatjet-Flüge (Q1 2025)',
        'Geschätzter CO₂-Ausstoß Ingolstadt (monatlich)'
    ],
    'CO2 Emissionen (Metrische Tonnen)': [
        total_emissions,
        CO2_INGOLSTADT_MONTHLY_TONS
    ]
})

# Verhältnis berechnen
ratio = (total_emissions / CO2_INGOLSTADT_MONTHLY_TONS) * 100

st.subheader("Balkendiagramm: CO₂-Emissionen im Vergleich")
fig_bar = px.bar(
    comparison_data,
    x='Quelle',
    y='CO2 Emissionen (Metrische Tonnen)',
    color='Quelle',
    color_discrete_map={
        'Tom Cruise Privatjet-Flüge (Q1 2025)': '#FF4B4B',
        'Geschätzter CO₂-Ausstoß Ingolstadt (monatlich)': '#0083B8'
    },
    labels={'CO2 Emissionen (Metrische Tonnen)':'CO₂-Emissionen (Metrische Tonnen)'}
)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Verhältnis")
st.success(
    f"Die Gesamt-CO₂-Emissionen der {total_flights} Privatjet-Flüge von Tom Cruise (Q1 2025) "
    f"entsprechen **{ratio:.2f}%** des geschätzten monatlichen CO₂-Ausstoßes von Ingolstadt."
)

st.markdown("---")

# --- 6. Datenvorschau (Unverändert) ---
st.header("📋 Rohdaten")
st.dataframe(data)

# --- ENDE DES STREAMLIT-CODES ---
