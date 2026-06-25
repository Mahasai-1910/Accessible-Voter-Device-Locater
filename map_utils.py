"""Map visualization utilities using Folium and Plotly."""

from __future__ import annotations

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from utils.theme import COLORS


def compliance_color(score: float) -> str:
    if score >= 85:
        return COLORS["accent"]
    if score >= 60:
        return COLORS["warning"]
    return COLORS["danger"] if "danger" in COLORS else "#EF4444"


def create_folium_map(
    df: pd.DataFrame,
    center_lat: float = 28.6139,
    center_lon: float = 77.2090,
    zoom: int = 10,
    user_lat: float | None = None,
    user_lon: float | None = None,
) -> folium.Map:
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")
    cluster = MarkerCluster(name="Polling Locations").add_to(m)

    for _, row in df.iterrows():
        score = float(row.get("Compliance Score", row.get("Match Score", 50)))
        color = compliance_color(score)
        popup_html = f"""
        <b>{row.get('Location Name', 'Unknown')}</b><br>
        {row.get('Address', '')}<br>
        Compliance: {score:.0f}%<br>
        ♿ Wheelchair: {'Yes' if row.get('Wheelchair Access') else 'No'}<br>
        📞 {row.get('Contact Number', 'N/A')}
        """
        folium.CircleMarker(
            location=[float(row["Latitude"]), float(row["Longitude"])],
            radius=10,
            popup=folium.Popup(popup_html, max_width=280),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            tooltip=str(row.get("Location Name", "")),
        ).add_to(cluster)

    if user_lat and user_lon:
        folium.Marker(
            [user_lat, user_lon],
            popup="Your Location",
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
            tooltip="You are here",
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def render_folium_map(df: pd.DataFrame, height: int = 500, **kwargs) -> dict | None:
    if df.empty:
        st.info("No locations to display on the map.")
        return None

    center_lat = df["Latitude"].astype(float).mean()
    center_lon = df["Longitude"].astype(float).mean()
    m = create_folium_map(df, center_lat=center_lat, center_lon=center_lon, **kwargs)
    return st_folium(m, width=None, height=height, returned_objects=["last_object_clicked"])


def create_plotly_scatter_map(df: pd.DataFrame, color_col: str = "Compliance Score") -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data available")
        return fig

    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=color_col,
        size_max=15,
        zoom=9,
        hover_name="Location Name",
        hover_data=["City", "State", "Contact Number"],
        color_continuous_scale=["#EF4444", "#F59E0B", "#00C896"],
        mapbox_style="carto-positron",
        title="Accessibility Coverage Map",
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=500)
    return fig


def render_plotly_map(df: pd.DataFrame, color_col: str = "Compliance Score") -> None:
    fig = create_plotly_scatter_map(df, color_col)
    st.plotly_chart(fig, use_container_width=True)
