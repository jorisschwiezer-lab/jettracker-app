import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Jet Tracker", layout="wide")

st.title("✈️ Tom Cruise Jet Tracker")

# Beispiel-Daten (du kannst später deine CSV einlesen)
data = {
    "Date": ["2025-03-24", "2025-03-19", "2025-03-17"],
    "From": ["Cincinnati Municipal Airport (LUK)", "Naples Airport (APF)", "Ohio State University Airport (OSU)"],
    "To": ["Fort Lauderdale Executive Airport (FXE)", "Cincinnati Municipal Airport (LUK)", "Laconia Municipal Airport (LCI)"],
    "CO2 (tons)": [5, 5, 4],
    "Distance (miles)": [930, 910, 650],
    "lat_from": [39.1031, 26.1527, 40.0799],
    "lon_from": [-84.5120, -81.7750, -83.0726],
    "lat_to": [26.1833, 39.1031, 43.5500],
    "lon_to": [-80.1000, -84.5120, -71.4000],
}

df = pd.DataFrame(data)

st.subheader("Flugübersicht")
st.dataframe(df)

st.subheader("🌍 Flugrouten auf Karte")

# Karte mit PyDeck
layer = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position=["lon_from", "lat_from"],
    get_target_position=["lon_to", "lat_to"],
    get_source_color=[255, 0, 0, 160],
    get_target_color=[0, 128, 255, 160],
    auto_highlight=True,
    width_scale=0.0005,
    get_width="Distance (miles)",
)

view_state = pdk.ViewState(latitude=30, longitude=-80, zoom=3)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
