import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- 1. Konfiguration und Daten laden ---
# Das Layout der Seite auf "wide" setzen
st.set_page_config(layout="wide", page_title="Tom Cruise Jet Tracker (2025)", page_icon="✈️")

# Name der CSV-Datei (muss im selben Ordner wie diese App sein)
CSV_FILE = 'Tom_Cruise_Jet_2025.csv'

# Konstante für den CO2-Vergleich (monatliche CO2-Emissionen der Vergleichsstadt)
# Annahme: Monatl. Emissionen Ingolstadt (mittlere dt. Stadt) in Tonnen CO2.
# Dies ist ein Platzhalterwert und muss recherchiert/angepasst werden!
CO2_INGOLSTADT_MONTHLY_TONS = 150000

# Funktion zum Laden und Vorbereiten der Daten
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Datenbereinigung und Typkonvertierung
    # Konvertiere 'Datum' ins richtige Format
    def parse_date(date_str):
        # Versuche gängige Formate
        for fmt in ('%m/%d/%Y', '%m/%d/%y', '%d.%m.%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(str(date_str), fmt)
            except (ValueError, TypeError):
                continue
        return pd.NaT

    df['Datum'] = df['Datum'].apply(parse_date)
    df.dropna(subset=['Datum'], inplace=True) # Entferne Zeilen ohne gültiges Datum
    df.sort_values(by='Datum', inplace=True)

    # Bereinige 'Distanz (Meilen)' und konvertiere zu float
    df['Distanz (Meilen)'] = df['Distanz (Meilen)'].str.replace(' miles', '', regex=False).str.replace(',', '', regex=False).astype(float, errors='ignore')

    # Berechne die Flugnummer (wichtig für den Schieberegler)
    df['Flugnummer'] = np.arange(1, len(df) + 1)

    # Füge Platzhalter für geokodierte Koordinaten hinzu (für die Karte erforderlich)
    # ECHTES PROJEKT: Hier müsste eine API-Abfrage (z.B. Google Maps oder OpenStreetMap)
    # zur Umwandlung der Airport-Codes (CLD, SUA, VNY etc.) in Längen- und Breitengrade erfolgen.
    # Da dies komplex ist und externe APIs erfordert, werden hier Beispiel-Daten verwendet,
    # die auf den echten Koordinaten von LA und Florida basieren, um die Funktionalität zu zeigen.
    df['lat'] = np.random.uniform(25, 35, len(df)) # Breitengrad
    df['lon'] = np.random.uniform(-120, -75, len(df)) # Längengrad

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


# --- 2. Seitentitel und Einleitung ---
st.title("✈️ Tom Cruise Privatjet-Tracker: Q1 2025 Flüge")
st.markdown("Analysiert 43 Privatjet-Flüge von Tom Cruise (Bombardier Challenger 350 N350XX) im ersten Quartal 2025.")
st.markdown("---")

# --- 3. Statistische Kennzahlen (KPIs) ---
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

# --- 4. Interaktive Karte mit Schieberegler ---
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
# Die Karte verwendet die Platzhalter-Koordinaten (lat/lon)
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

# --- 5. Vergleichsanalyse ---
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

# --- 6. Datenvorschau ---
st.header("📋 Rohdaten")
st.dataframe(data)

# --- ENDE DES STREAMLIT-CODES ---
