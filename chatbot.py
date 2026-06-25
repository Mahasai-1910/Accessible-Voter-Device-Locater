"""CAP AI Assistant chatbot with OpenAI integration."""

from __future__ import annotations

import os

import streamlit as st

from utils.data_loader import filter_locations, load_locations
from utils.recommendation_engine import DISABILITY_PROFILES, recommend_locations

SYSTEM_PROMPT = """You are CAP AI, an expert accessibility voting assistant for the Accessible Voting Device Locator platform.
You help voters with disabilities, election officials, and volunteers find accessible polling locations,
understand voting accessibility services, recommend voting devices, and answer FAQs about election assistance.
Always be empathetic, clear, and accurate. Reference ADA/WCAG accessibility principles when relevant.
If you don't know specific local election dates, advise users to contact their local election office."""


FAQS = {
    "What is an accessible voting device?": (
        "Accessible voting devices include audio ballot readers, braille displays, sip-and-puff interfaces, "
        "large-print ballots, and touchscreen units with accessibility features. These allow voters with "
        "disabilities to cast their ballots privately and independently."
    ),
    "Can I get assistance voting?": (
        "Yes. Under the Help America Vote Act (HAVA), polling places must provide accessible voting systems. "
        "You may also receive assistance from trained poll workers or a person of your choice (except your employer "
        "or union representative)."
    ),
    "What if my polling place isn't accessible?": (
        "Contact your local election office immediately. Alternative options may include curbside voting, "
        "transferring your registration to an accessible location, or using an absentee/early voting option."
    ),
}


def get_openai_response(user_message: str, context: str = "") -> str:
    api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        return local_fallback_response(user_message)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        if context:
            messages.append({"role": "system", "content": f"Context data:\n{context}"})
        messages.extend(st.session_state.get("chat_history", [])[-6:])
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content or "I couldn't generate a response."
    except Exception as exc:
        return f"AI service unavailable ({exc}). Using local knowledge base.\n\n{local_fallback_response(user_message)}"


def local_fallback_response(message: str) -> str:
    msg = message.lower()
    locations = load_locations()

    if any(w in msg for w in ["nearest", "closest", "find location", "where can i vote"]):
        rec = recommend_locations(locations, "Multiple Disabilities")
        if rec["best"]:
            b = rec["best"]
            return (
                f"Based on accessibility features, I recommend **{b.get('Location Name')}** "
                f"at {b.get('Address')}, {b.get('City')}. "
                f"Match score: {b.get('Match Score', 'N/A')}%. "
                f"Contact: {b.get('Contact Number', 'N/A')}."
            )
        return "I couldn't find accessible locations in the database. Please contact your election office."

    if any(w in msg for w in ["visual", "blind", "braille", "audio"]):
        profile = DISABILITY_PROFILES["Visual Impairment"]
        return (
            f"For visual impairments, look for locations with: {', '.join(profile['devices'])}. "
            f"Assistance options: {', '.join(profile['assistance'])}."
        )

    if any(w in msg for w in ["wheelchair", "mobility", "ramp"]):
        profile = DISABILITY_PROFILES["Mobility Impairment"]
        filtered = filter_locations(locations, "City", "", {"wheelchair": True})
        count = len(filtered)
        return (
            f"For mobility needs: {', '.join(profile['devices'])}. "
            f"We have {count} wheelchair-accessible locations in our database."
        )

    if any(w in msg for w in ["hearing", "deaf", "sign language"]):
        profile = DISABILITY_PROFILES["Hearing Impairment"]
        return f"For hearing impairments: {', '.join(profile['assistance'])}."

    for question, answer in FAQS.items():
        if any(w in msg for w in question.lower().split()[:3]):
            return answer

    return (
        "I'm CAP AI, your accessibility voting assistant. I can help you:\n"
        "• Find the nearest accessible polling location\n"
        "• Explain voting accessibility services\n"
        "• Recommend voting devices for your needs\n"
        "• Answer accessibility FAQs\n\n"
        "Try asking: 'Find the nearest accessible location' or 'What devices help visual impairment?'"
    )


def render_chat_panel() -> None:
    st.subheader("🤖 CAP AI Assistant")
    st.caption("Ask about accessible voting locations, devices, and assistance services.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask CAP AI about accessible voting..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        locations = load_locations()
        context = f"Total locations: {len(locations)}. Sample: {locations.head(3).to_string() if not locations.empty else 'None'}"
        response = get_openai_response(prompt, context)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        faq = st.selectbox("Quick FAQ", ["Select a question..."] + list(FAQS.keys()), label_visibility="collapsed")
        if faq != "Select a question...":
            st.info(FAQS[faq])
