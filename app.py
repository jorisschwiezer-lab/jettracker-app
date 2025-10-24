import streamlit as st
import pandas as pd
import pydeck as pdk

# CSV einlesen
df = pd.read_csv("tom_cruise_n350xx_flights.csv")

st.set_page_config(page_title="Tom Cruise Jet Tracker", layout="wide")
st.title("✈️ Tom Cruise Jet Tracker")

# Tabelle anzeigen
st.subheader("📋 Flugübersicht")
st.dataframe(df)

# Beispielhafte Spaltennamen anpassen (je nachdem, wie sie in deiner CSV heißen)
if "lat_from" in df.columns and "lon_from" in df.columns and "lat_to" in df.columns and "lon_to" in df.columns:
    st.subheader("🌍 Flugrouten auf Karte")

    # Karte mit PyDeck anzeigen
    layer = pdk.Layer(
        "ArcLayer",
        data=df,
        get_source_position=["lon_from", "lat_from"],
        get_target_position=["lon_to", "lat_to"],
        get_source_color=[255, 0, 0, 160],
        get_target_color=[0, 0, 255, 160],
        auto_highlight=True,
        width_scale=0.0005,
        get_width=5,
    )

    view_state = pdk.ViewState(latitude=30, longitude=-40, zoom=2)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
else:
    st.warning("Die CSV enthält keine Koordinaten-Spalten. Bitte ergänze lat/lon für Start und Ziel.")

