"""Accessibility matching and recommendation engine."""

from __future__ import annotations

from typing import Any

import pandas as pd

from utils.data_loader import BOOL_COLS, add_compliance_scores, haversine_km

DISABILITY_PROFILES: dict[str, dict[str, Any]] = {
    "Visual Impairment": {
        "required": ["Braille Device", "Audio Ballot", "Large Print Ballot"],
        "recommended": ["Staff Assistance"],
        "devices": ["Audio Ballot Device (AVC)", "Braille Voting Machine", "Large Print Ballot"],
        "assistance": ["Trained poll worker guidance", "Curbside voting if needed"],
    },
    "Hearing Impairment": {
        "required": ["Sign Language Assistance"],
        "recommended": ["Staff Assistance"],
        "devices": ["Visual display voting unit", "Written instruction cards"],
        "assistance": ["Sign language interpreter", "Written communication support"],
    },
    "Mobility Impairment": {
        "required": ["Wheelchair Access"],
        "recommended": ["Staff Assistance", "Transportation Assistance"],
        "devices": ["Wheelchair-accessible booth", "Sip-and-Puff Device"],
        "assistance": ["Ramp access", "Curbside voting", "Personal assistance"],
    },
    "Cognitive Disability": {
        "required": ["Staff Assistance"],
        "recommended": ["Large Print Ballot", "Audio Ballot"],
        "devices": ["Simplified ballot interface", "Large print materials"],
        "assistance": ["Patient poll worker support", "Companion assistance (where permitted)"],
    },
    "Multiple Disabilities": {
        "required": ["Wheelchair Access", "Staff Assistance"],
        "recommended": ["Audio Ballot", "Braille Device", "Sign Language Assistance", "Large Print Ballot"],
        "devices": ["Universal voting device", "Full accessibility suite"],
        "assistance": ["Dedicated accessibility coordinator on-site", "Multi-modal assistance"],
    },
}


def compute_match_score(row: pd.Series, profile: dict[str, Any]) -> float:
    required = profile.get("required", [])
    recommended = profile.get("recommended", [])
    if not required:
        return 0.0

    req_score = sum(int(row.get(c, 0)) for c in required if c in row.index) / len(required)
    rec_score = (
        sum(int(row.get(c, 0)) for c in recommended if c in row.index) / len(recommended) if recommended else 1.0
    )
    compliance = row.get("Compliance Score", 50) / 100 if "Compliance Score" in row.index else 0.5
    return round((req_score * 0.6 + rec_score * 0.2 + compliance * 0.2) * 100, 1)


def recommend_locations(
    df: pd.DataFrame,
    disability: str,
    user_lat: float | None = None,
    user_lon: float | None = None,
    top_n: int = 5,
) -> dict[str, Any]:
    profile = DISABILITY_PROFILES.get(disability, DISABILITY_PROFILES["Multiple Disabilities"])
    if df.empty:
        return {"locations": pd.DataFrame(), "profile": profile, "best": None}

    scored = add_compliance_scores(df.copy())
    scored["Match Score"] = scored.apply(lambda r: compute_match_score(r, profile), axis=1)

    if user_lat is not None and user_lon is not None:
        scored["Distance (km)"] = scored.apply(
            lambda r: haversine_km(user_lat, user_lon, float(r["Latitude"]), float(r["Longitude"])),
            axis=1,
        )
        scored["Combined Score"] = scored["Match Score"] - scored["Distance (km)"] * 0.5
        scored = scored.sort_values(["Combined Score", "Match Score"], ascending=False)
    else:
        scored = scored.sort_values("Match Score", ascending=False)

    top = scored.head(top_n)
    best = top.iloc[0].to_dict() if not top.empty else None

    return {
        "locations": top,
        "profile": profile,
        "best": best,
        "disability": disability,
    }


def get_compatibility_details(row: pd.Series, profile: dict[str, Any]) -> list[str]:
    details = []
    for col in profile.get("required", []):
        status = "✅" if int(row.get(col, 0)) else "❌"
        details.append(f"{status} {col} (Required)")
    for col in profile.get("recommended", []):
        if col not in profile.get("required", []):
            status = "✅" if int(row.get(col, 0)) else "⚠️"
            details.append(f"{status} {col} (Recommended)")
    return details
