"""AG-Grid table utilities."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def render_aggrid(
    df: pd.DataFrame,
    key: str,
    height: int = 400,
    selection_mode: str = "single",
    enable_export: bool = True,
) -> dict:
    if df.empty:
        st.info("No data to display.")
        return {}

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True,
        editable=False,
        wrapText=True,
        autoHeight=True,
    )
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_selection(selection_mode=selection_mode, use_checkbox=True)
    gb.configure_grid_options(
        domLayout="normal",
        enableCellTextSelection=True,
        ensureDomOrder=True,
        suppressRowClickSelection=False,
    )

    if enable_export:
        gb.configure_side_bar(filters_panel=True, columns_panel=True)

    grid_options = gb.build()

    custom_css = {
        ".ag-header-cell-label": {"justify-content": "center", "font-weight": "600"},
        ".ag-row-hover": {"background-color": "rgba(0, 174, 239, 0.12) !important"},
    }

    return AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=height,
        theme="streamlit",
        custom_css=custom_css,
        key=key,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
    )
