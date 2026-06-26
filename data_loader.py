import pandas as pd
import streamlit as st
@st.cache_data
def load_data():
    df = pd.read_csv("data/store.csv")

    # Conversion des dates
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])

    return df