#!/usr/bin/env python3


import streamlit as st
import pandas_datareader.data as web
import pandas as pd
import datetime

FRED_CODES = {
    "EUR": "DEXUSEU",
    "GBP": "DEXUSUK",
    "JPY": "DEXJPUS",
    "CHF": "DEXSZUS",
    "CAD": "DEXCAUS",
    "AUD": "DEXUSAL",
    "SEK": "DEXSDUS",
    "NOK": "DEXNOUS",
}

st.set_page_config(page_title="FRED Currency Downloader", page_icon="💹", layout="centered")
st.title("💹 Federal Reserve Daily FX Downloader")

st.markdown(
    """
Use this app to download daily official USD exchange rates from FRED.  
Supports inversion (e.g. CHF/USD as well as USD/CHF).  
Simply choose your currencies and date range, then click **Download CSV**.
"""
)

# --- Inputs ---
col1, col2 = st.columns(2)
with col1:
    base = st.text_input("Base currency (e.g. USD):", "USD").upper()
with col2:
    quote = st.text_input("Quote currency (e.g. CHF):", "CHF").upper()

today = datetime.date.today()
start_date = st.date_input("Start date", datetime.date(today.year, 1, 1))
end_date = st.date_input("End date", today)

if st.button("Fetch Data"):
    fred_code = None
    invert = False

    # Determine correct series and direction
    if base == "USD" and quote in FRED_CODES:
        fred_code = FRED_CODES[quote]
        invert = False
    elif quote == "USD" and base in FRED_CODES:
        fred_code = FRED_CODES[base]
        invert = True

    if not fred_code:
        st.error(
            "⚠️ Unsupported pair. Available currencies: "
            + ", ".join(sorted(FRED_CODES.keys()))
        )
    else:
        try:
            st.info(f"Fetching {base}/{quote} data from FRED ({fred_code}) …")
            data = web.DataReader(fred_code, "fred", start_date, end_date).dropna()

            pair = f"{base}/{quote}"
            data[pair] = 1 / data[fred_code] if invert else data[fred_code]
            data = data[[pair]].rename_axis("Date")

            csv = data.to_csv().encode("utf-8")
            st.success(f"✅ Retrieved {len(data)} rows of data")

            st.download_button(
                "⬇️ Download CSV File",
                data=csv,
                file_name=f"{base}_{quote}_{start_date}_{end_date}_FRED.csv",
                mime="text/csv",
            )

            st.dataframe(data.tail(10))
        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")
