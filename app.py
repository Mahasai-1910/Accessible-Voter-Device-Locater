"""CAP AI – Accessible Voting Device Locator — Main Application."""

from __future__ import annotations

import streamlit as st

from auth import logout , verify_login
from chatbot import render_chat_panel
from theme import (
    LOGO_PATH,
    inject_global_css,
    init_session_defaults,
    render_accessibility_controls,
    render_footer,
    render_hero,
    render_sidebar_branding,
)

st.set_page_config(
    page_title="CAP AI – Accessible Voting Device Locator",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_defaults()
inject_global_css()


def render_login() -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_container_width=True)
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:2rem;">
                <h1 style="color:#0047AB;font-size:2.5rem;font-weight:800;">CAP AI</h1>
                <p style="color:#00AEEF;font-size:1.2rem;font-weight:600;">Accessible Voting Device Locator</p>
                <p style="color:#64748B;">Secure access for election officials, coordinators, volunteers & voters</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            st.markdown("##### 🔐 Secure Login")
            username = st.text_input("Username", placeholder="admin, officer, coordinator, volunteer")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if verify_login(username, password):
                    st.success(f"Welcome, {st.session_state.get('user_name', username)}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try: admin / admin123")

        with st.expander("Demo Credentials"):
            st.markdown(
                """
                | Role | Username | Password |
                |------|----------|----------|
                | Super Admin | admin | admin123 |
                | Election Officer | officer | officer123 |
                | Accessibility Coordinator | coordinator | coord123 |
                | Volunteer | volunteer | volunteer123 |
                """
            )


def render_home() -> None:
    render_sidebar_branding()
    render_accessibility_controls()

    st.sidebar.markdown(f"**👤 {st.session_state.get('user_name', 'User')}**")
    st.sidebar.caption(f"Role: {st.session_state.get('role', 'Unknown')}")
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

    st.sidebar.divider()
    st.sidebar.info("Navigate using the pages menu above ↑")

    if LOGO_PATH.exists():
        lc, hc = st.columns([1, 4])
        with lc:
            st.image(str(LOGO_PATH), width=120)
        with hc:
            render_hero()

    st.markdown("### Welcome to CAP AI")
    st.markdown(
        """
        The **Accessible Voting Device Locator** empowers voters with disabilities to find compatible
        voting equipment, accessibility services, and assistance resources at polling locations nationwide.

        Use the navigation panel to access:
        - **Dashboard** — KPI overview and coverage charts
        - **Device Locator** — Search polling locations by accessibility needs
        - **Accessibility Matcher** — AI-powered location recommendations
        - **Analytics** — Compliance and utilization insights
        - **Reports** — Export compliance and device reports
        - **Admin** — Data import, device management, user controls
        """
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <h4>♿ Accessibility First</h4>
                <p>WCAG 2.1 AA compliant design with high contrast mode, text resize, and screen reader support.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <h4>🗳️ Election Ready</h4>
                <p>Built for election officials, accessibility coordinators, volunteers, and voters.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()
    render_chat_panel()
    render_footer()


def main() -> None:
    if not st.session_state.get("authenticated"):
        render_login()
    else:
        render_home()


if __name__ == "__main__":
    main()
