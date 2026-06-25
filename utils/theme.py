"""Shared UI theme, CSS, and accessibility controls for CAP AI."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "assets" / "cap_ai_logo.png"

COLORS = {
    "primary": "#0047AB",
    "secondary": "#00AEEF",
    "accent": "#00C896",
    "light_bg": "#F8FAFC",
    "dark_bg": "#0F172A",
    "success": "#00C896",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}

REQUIRED_COLUMNS = [
    "Location ID",
    "Location Name",
    "Address",
    "City",
    "State",
    "ZIP Code",
    "Latitude",
    "Longitude",
    "Wheelchair Access",
    "Braille Device",
    "Audio Ballot",
    "Sip-and-Puff Device",
    "Large Print Ballot",
    "Sign Language Assistance",
    "Staff Assistance",
    "Contact Number",
]

COLUMN_ALIASES = {
    "location id": "Location ID",
    "location_id": "Location ID",
    "location name": "Location Name",
    "location_name": "Location Name",
    "zip": "ZIP Code",
    "zip code": "ZIP Code",
    "zip_code": "ZIP Code",
    "pin code": "ZIP Code",
    "lat": "Latitude",
    "latitude": "Latitude",
    "lon": "Longitude",
    "lng": "Longitude",
    "longitude": "Longitude",
    "wheelchair access": "Wheelchair Access",
    "wheelchair_access": "Wheelchair Access",
    "braille device": "Braille Device",
    "braille_device": "Braille Device",
    "audio ballot": "Audio Ballot",
    "audio_ballot": "Audio Ballot",
    "sip-and-puff device": "Sip-and-Puff Device",
    "sip_and_puff": "Sip-and-Puff Device",
    "large print ballot": "Large Print Ballot",
    "large_print_ballot": "Large Print Ballot",
    "sign language assistance": "Sign Language Assistance",
    "sign_language_assistance": "Sign Language Assistance",
    "staff assistance": "Staff Assistance",
    "staff_assistance": "Staff Assistance",
    "contact number": "Contact Number",
    "contact_number": "Contact Number",
    "district": "District",
}


def init_session_defaults() -> None:
    defaults = {
        "authenticated": False,
        "username": None,
        "role": None,
        "dark_mode": False,
        "high_contrast": False,
        "font_scale": 100,
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def inject_global_css() -> None:
    dark = st.session_state.get("dark_mode", False)
    hc = st.session_state.get("high_contrast", False)
    scale = st.session_state.get("font_scale", 100)

    bg = COLORS["dark_bg"] if dark else COLORS["light_bg"]
    text = "#F8FAFC" if dark else "#0F172A"
    card_bg = "rgba(15, 23, 42, 0.72)" if dark else "rgba(255, 255, 255, 0.72)"
    border = "rgba(0, 174, 239, 0.35)" if not hc else "#FFFFFF"
    primary = "#FFFFFF" if hc and dark else COLORS["primary"]
    secondary = "#FFFF00" if hc else COLORS["secondary"]

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif !important;
            font-size: {scale}% !important;
        }}

        .stApp {{
            background: linear-gradient(135deg, {bg} 0%, {'#1E293B' if dark else '#E2E8F0'} 50%, {bg} 100%);
            color: {text};
            animation: fadeIn 0.6s ease-in-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(0, 174, 239, 0.4); }}
            50% {{ box-shadow: 0 0 0 12px rgba(0, 174, 239, 0); }}
        }}

        .cap-hero {{
            background: linear-gradient(120deg, {primary} 0%, {secondary} 55%, {COLORS['accent']} 100%);
            border-radius: 20px;
            padding: 2rem 2.5rem;
            margin-bottom: 1.5rem;
            color: white;
            box-shadow: 0 20px 40px rgba(0, 71, 171, 0.25);
            animation: fadeIn 0.8s ease;
        }}

        .cap-hero h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            margin: 0;
            letter-spacing: -0.02em;
        }}

        .cap-hero p {{
            font-size: 1.1rem;
            opacity: 0.95;
            margin: 0.5rem 0 0 0;
        }}

        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 2px solid {border};
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 32px rgba(0, 71, 171, 0.12);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}

        .glass-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(0, 174, 239, 0.2);
        }}

        .kpi-value {{
            font-size: 2rem;
            font-weight: 800;
            color: {secondary};
            line-height: 1.1;
        }}

        .kpi-label {{
            font-size: 0.95rem;
            font-weight: 600;
            color: {text};
            opacity: 0.85;
        }}

        .cap-footer {{
            text-align: center;
            padding: 1.5rem;
            margin-top: 2rem;
            border-top: 1px solid {border};
            color: {text};
            opacity: 0.8;
            font-size: 0.9rem;
        }}

        .badge-success {{ background: {COLORS['accent']}; color: #0F172A; padding: 0.2rem 0.6rem; border-radius: 999px; font-weight: 600; }}
        .badge-warning {{ background: {COLORS['warning']}; color: #0F172A; padding: 0.2rem 0.6rem; border-radius: 999px; font-weight: 600; }}
        .badge-danger {{ background: {COLORS['danger']}; color: white; padding: 0.2rem 0.6rem; border-radius: 999px; font-weight: 600; }}

        div[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {primary} 0%, {'#1E3A5F' if dark else '#003380'} 100%);
        }}

        div[data-testid="stSidebar"] * {{
            color: #F8FAFC !important;
        }}

        .stButton > button {{
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 16px rgba(0, 174, 239, 0.3);
        }}

        [data-testid="stMetricValue"] {{
            font-size: 1.8rem !important;
            font-weight: 800 !important;
        }}

        .sr-only {{
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0,0,0,0);
            border: 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(title: str = "CAP AI", subtitle: str = "Accessible Voting Device Locator") -> None:
    st.markdown(
        f"""
        <div class="cap-hero" role="banner" aria-label="CAP AI Application Header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, delta: str | None = None) -> None:
    delta_html = f'<div style="font-size:0.85rem;color:{COLORS["accent"]};">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="glass-card" role="region" aria-label="{label}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="cap-footer" role="contentinfo">
            <strong>CAP AI</strong> — Accessible Voting Device Locator<br>
            © 2026 Civic Accessibility Platform · WCAG 2.1 AA Compliant Design<br>
            <span style="font-size:0.8rem;">Empowering every voter with accessible election resources</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_branding() -> None:
    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), use_container_width=True)
    st.sidebar.markdown("### CAP AI")
    st.sidebar.caption("Accessible Voting Device Locator")
    st.sidebar.divider()


def render_accessibility_controls() -> None:
    st.sidebar.subheader("♿ Accessibility")
    st.session_state.dark_mode = st.sidebar.toggle("Dark Mode", value=st.session_state.get("dark_mode", False))
    st.session_state.high_contrast = st.sidebar.toggle(
        "High Contrast", value=st.session_state.get("high_contrast", False)
    )
    st.session_state.font_scale = st.sidebar.slider(
        "Text Size", min_value=90, max_value=130, value=st.session_state.get("font_scale", 100), step=5
    )


def compliance_badge(score: float) -> str:
    if score >= 85:
        return f'<span class="badge-success">{score:.0f}% Compliant</span>'
    if score >= 60:
        return f'<span class="badge-warning">{score:.0f}% Partial</span>'
    return f'<span class="badge-danger">{score:.0f}% Needs Work</span>'
