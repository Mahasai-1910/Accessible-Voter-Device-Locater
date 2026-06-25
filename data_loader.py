"""Data loading, validation, import/export utilities."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

from utils.theme import COLUMN_ALIASES, REQUIRED_COLUMNS, ROOT

DATA_DIR = ROOT / "data"
LOCATIONS_FILE = DATA_DIR / "polling_locations.csv"
DEVICES_FILE = DATA_DIR / "voting_devices.csv"
REQUESTS_FILE = DATA_DIR / "assistance_requests.csv"

BOOL_COLS = [
    "Wheelchair Access",
    "Braille Device",
    "Audio Ballot",
    "Sip-and-Puff Device",
    "Large Print Ballot",
    "Sign Language Assistance",
    "Staff Assistance",
]

FEATURE_MAP = {
    "wheelchair": "Wheelchair Access",
    "braille": "Braille Device",
    "audio": "Audio Ballot",
    "sip_puff": "Sip-and-Puff Device",
    "large_print": "Large Print Ballot",
    "sign_language": "Sign Language Assistance",
    "staff": "Staff Assistance",
    "transportation": "Transportation Assistance",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        key = str(col).strip().lower().replace("-", " ").replace("_", " ")
        key = key.replace("  ", " ")
        if key in COLUMN_ALIASES:
            renamed[col] = COLUMN_ALIASES[key]
        elif col.strip() in REQUIRED_COLUMNS:
            renamed[col] = col.strip()
    out = df.rename(columns=renamed)
    if "District" not in out.columns:
        out["District"] = out.get("City", pd.Series(["Unknown"] * len(out)))
    if "Transportation Assistance" not in out.columns:
        out["Transportation Assistance"] = 0
    return out


def parse_bool_series(series: pd.Series) -> pd.Series:
    truthy = {"yes", "y", "true", "1", "1.0", "available", "x", "✓", "✔"}
    return series.apply(
        lambda v: 1
        if (isinstance(v, (int, float)) and v == 1)
        or (isinstance(v, bool) and v)
        or (isinstance(v, str) and v.strip().lower() in truthy)
        else 0
    )


def validate_import(df: pd.DataFrame) -> dict[str, Any]:
    df = normalize_columns(df.copy())
    errors: list[str] = []
    warnings: list[str] = []

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")

    if "Location ID" in df.columns:
        dupes = df[df["Location ID"].duplicated(keep=False)]
        if not dupes.empty:
            warnings.append(f"Duplicate Location IDs found: {dupes['Location ID'].nunique()} records")

    for col in ["Latitude", "Longitude"]:
        if col in df.columns:
            invalid = df[col].isna() | ~pd.to_numeric(df[col], errors="coerce").between(-180, 180)
            if col == "Latitude":
                invalid = df[col].isna() | ~pd.to_numeric(df[col], errors="coerce").between(-90, 90)
            if invalid.any():
                warnings.append(f"{invalid.sum()} rows with invalid {col}")

    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = parse_bool_series(df[col])

    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    for col, count in null_cols.items():
        if col in REQUIRED_COLUMNS:
            warnings.append(f"{count} missing values in '{col}'")

    return {"df": df, "errors": errors, "warnings": warnings, "valid": len(errors) == 0}


@st.cache_data(show_spinner=False)
def load_locations() -> pd.DataFrame:
    if "locations_override" in st.session_state and st.session_state.locations_override is not None:
        return st.session_state.locations_override.copy()
    if LOCATIONS_FILE.exists():
        df = pd.read_csv(LOCATIONS_FILE)
        return normalize_columns(df)
    return pd.DataFrame(columns=REQUIRED_COLUMNS + ["District", "Transportation Assistance"])


@st.cache_data(show_spinner=False)
def load_devices() -> pd.DataFrame:
    if "devices_override" in st.session_state and st.session_state.devices_override is not None:
        return st.session_state.devices_override.copy()
    if DEVICES_FILE.exists():
        return pd.read_csv(DEVICES_FILE)
    return pd.DataFrame(
        columns=[
            "Device ID",
            "Device Type",
            "Manufacturer",
            "Quantity",
            "Polling Location",
            "Status",
            "Last Inspection Date",
        ]
    )


@st.cache_data(show_spinner=False)
def load_assistance_requests() -> pd.DataFrame:
    if REQUESTS_FILE.exists():
        return pd.read_csv(REQUESTS_FILE)
    return pd.DataFrame(columns=["Request ID", "Date", "Location", "Need Type", "Status", "Voter ID"])


def save_locations(df: pd.DataFrame) -> None:
    df.to_csv(LOCATIONS_FILE, index=False)
    st.session_state.locations_override = df.copy()
    load_locations.clear()


def save_devices(df: pd.DataFrame) -> None:
    df.to_csv(DEVICES_FILE, index=False)
    st.session_state.devices_override = df.copy()
    load_devices.clear()


def import_file(uploaded_file) -> dict[str, Any]:
    name = uploaded_file.name.lower()
    if name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    elif name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        return {"valid": False, "errors": ["Unsupported file format. Use .xlsx or .csv"], "warnings": [], "df": pd.DataFrame()}
    return validate_import(df)


def compute_compliance_score(row: pd.Series) -> float:
    features = BOOL_COLS + ["Transportation Assistance"]
    present = [c for c in features if c in row.index]
    if not present:
        return 0.0
    return round(row[present].astype(float).mean() * 100, 1)


def add_compliance_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Compliance Score"] = out.apply(compute_compliance_score, axis=1)
    return out


def compute_kpis(locations: pd.DataFrame, devices: pd.DataFrame, requests: pd.DataFrame) -> dict[str, Any]:
    locs = add_compliance_scores(locations) if not locations.empty else locations
    total_locs = len(locs)
    accessible = int((locs["Compliance Score"] >= 70).sum()) if not locs.empty and "Compliance Score" in locs else 0
    total_devices = int(devices["Quantity"].sum()) if not devices.empty and "Quantity" in devices.columns else 0
    assistance = len(requests)
    voters_supported = int(total_locs * 847 + assistance * 12) if total_locs else 0
    avg_compliance = round(locs["Compliance Score"].mean(), 1) if not locs.empty and "Compliance Score" in locs else 0.0

    return {
        "total_locations": total_locs,
        "accessible_locations": accessible,
        "total_devices": total_devices,
        "assistance_requests": assistance,
        "voters_supported": voters_supported,
        "compliance_score": avg_compliance,
    }


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return round(2 * r * np.arcsin(np.sqrt(a)), 2)


def filter_locations(
    df: pd.DataFrame,
    search_type: str,
    query: str,
    filters: dict[str, bool],
    user_lat: float | None = None,
    user_lon: float | None = None,
    radius_km: float = 50.0,
) -> pd.DataFrame:
    if df.empty:
        return df

    out = add_compliance_scores(df.copy())

    if query.strip():
        q = query.strip().lower()
        col_map = {
            "ZIP Code": "ZIP Code",
            "City": "City",
            "District": "District",
            "Polling Location Name": "Location Name",
        }
        col = col_map.get(search_type, "Location Name")
        if col in out.columns:
            out = out[out[col].astype(str).str.lower().str.contains(q, na=False)]

    for key, col in FEATURE_MAP.items():
        if filters.get(key) and col in out.columns:
            out = out[out[col].astype(int) == 1]

    if user_lat is not None and user_lon is not None and "Latitude" in out.columns:
        out["Distance (km)"] = out.apply(
            lambda r: haversine_km(user_lat, user_lon, float(r["Latitude"]), float(r["Longitude"])),
            axis=1,
        )
        out = out[out["Distance (km)"] <= radius_km].sort_values("Distance (km)")

    return out


def export_dataframe(df: pd.DataFrame, fmt: str = "csv") -> bytes:
    buffer = io.BytesIO()
    if fmt == "xlsx":
        df.to_excel(buffer, index=False, engine="openpyxl")
    else:
        df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()
