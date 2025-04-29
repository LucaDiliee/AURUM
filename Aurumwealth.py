import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# ---- Config ----
st.set_page_config(page_title="Wealth App", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---- Sample Mock Data ----
data = [
    {"name": "Villa in Tuscany", "category": "Real Estate", "value": 500000, "change": 2000},
    {"name": "Tesla Model S", "category": "Cars", "value": 90000, "change": -500},
    {"name": "Rolex Daytona", "category": "Watches", "value": 40000, "change": 100},
    {"name": "Apple Shares", "category": "Shares", "value": 120000, "change": 3000},
    {"name": "Chateau Margaux 2000", "category": "Wine", "value": 10000, "change": 150},
    {"name": "Monet Painting", "category": "Art", "value": 300000, "change": -2500},
]
df = pd.DataFrame(data)

if "assets" not in st.session_state:
    st.session_state.assets = df.copy()

total_value = st.session_state.assets['value'].sum()
total_change = st.session_state.assets['change'].sum()
total_change_percent = (total_change / (total_value - total_change)) * 100 if total_value != total_change else 0

# ---- Wealth Percentile (Mock) ----
def calculate_wealth_percentile(total_wealth):
    wealth_distribution = np.random.lognormal(mean=11, sigma=1.2, size=10000)
    percentile = sum(wealth_distribution < total_wealth) / len(wealth_distribution) * 100
    return percentile

wealth_percentile = calculate_wealth_percentile(total_value)

# ---- Top Search/Add Bar ----
st.text_input("Search or Add Asset", placeholder="Search by name or category")

if "page" not in st.session_state:
    st.session_state.page = "Overview"

st.markdown("""
    <style>
        div.stButton > button {
            width: 100%;
            margin: 0.2rem 0;
        }
        .stApp {
            padding-bottom: 100px;
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Overview"):
        st.session_state.page = "Overview"
with col2:
    if st.button("Performance"):
        st.session_state.page = "Performance by Category"
with col3:
    if st.button("Manage"):
        st.session_state.page = "Manage Assets"

page = st.session_state.page

# ---- Page 1: Overview ----
if page == "Overview":
    st.markdown("<h2 style='text-align: center;'>General Wealth Overview</h2>", unsafe_allow_html=True)
    st.metric(label="Total Wealth", value=f"${total_value:,.2f}", delta=f"{total_change_percent:.2f}%")

    st.markdown("""
        <div style='padding: 1rem; background-color: #1a2b4c; border-radius: 10px; margin: 1rem 0;'>
            <h4 style='margin-bottom: 0.5rem;'>Wealth Percentile</h4>
            <p>You are in the <strong>{:.1f}th</strong> percentile of wealth among app users.</p>
        </div>
    """.format(wealth_percentile), unsafe_allow_html=True)
    st.progress(min(wealth_percentile / 100, 1.0))

    pie_df = st.session_state.assets.groupby("category")['value'].sum().reset_index()
    fig = px.pie(pie_df, values='value', names='category', title='Asset Distribution')
    st.plotly_chart(fig, use_container_width=True)

# ---- Page 2: Performance by Category ----
elif page == "Performance by Category":
    st.markdown("<h2 style='text-align: center;'>Performance by Asset Category</h2>", unsafe_allow_html=True)
    grouped = st.session_state.assets.groupby("category").agg({"value": "sum", "change": "sum"}).reset_index()
    grouped["% Change"] = (grouped["change"] / (grouped["value"] - grouped["change"])) * 100
    st.dataframe(grouped)

    fig = px.bar(grouped, x="category", y="% Change", title="% Change by Category")
    st.plotly_chart(fig, use_container_width=True)

# ---- Page 3: Manage Assets ----
elif page == "Manage Assets":
    st.markdown("<h2 style='text-align: center;'>Add or Modify Assets</h2>", unsafe_allow_html=True)

    with st.form("asset_form"):
        name = st.text_input("Asset Name")
        category = st.selectbox("Category", st.session_state.assets['category'].unique())
        value = st.number_input("Current Value", min_value=0.0, step=100.0)
        change = st.number_input("Daily/Monthly Change", step=10.0)
        submitted = st.form_submit_button("Add Asset")

        if submitted:
            new_row = {"name": name, "category": category, "value": value, "change": change}
            st.session_state.assets = pd.concat([st.session_state.assets, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Asset '{name}' added to {category} with value ${value:.2f}.")

    st.markdown("<h3>Remove Existing Assets</h3>", unsafe_allow_html=True)
    if not st.session_state.assets.empty:
        asset_names = st.session_state.assets['name'].tolist()
        asset_to_remove = st.selectbox("Select asset to remove", options=asset_names)
        if st.button("Delete Asset"):
            st.session_state.assets = st.session_state.assets[st.session_state.assets['name'] != asset_to_remove]
            st.success(f"Asset '{asset_to_remove}' removed.")
    else:
        st.info("No assets to remove.")
