import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ---- Sample Mock Data ----
if "assets_data" not in st.session_state:
    st.session_state.assets_data = [
        {"name": "Villa in Tuscany", "category": "Real Estate", "value": 500000, "change": 2000},
        {"name": "Tesla Model S", "category": "Cars", "value": 90000, "change": -500},
        {"name": "Rolex Daytona", "category": "Watches", "value": 40000, "change": 100},
        {"name": "Apple Shares", "category": "Shares", "value": 120000, "change": 3000},
        {"name": "Chateau Margaux 2000", "category": "Wine", "value": 10000, "change": 150},
        {"name": "Monet Painting", "category": "Art", "value": 300000, "change": -2500},
    ]

df = pd.DataFrame(st.session_state.assets_data)
total_value = df['value'].sum()
total_change = df['change'].sum()
total_change_percent = (total_change / (total_value - total_change)) * 100 if (total_value - total_change) != 0 else 0

# Function to calculate wealth percentile (mock function)
def calculate_wealth_percentile(total_wealth):
    # This is a mock calculation - in a real app, this would compare against real user data
    # For demonstration, using a log-normal distribution to simulate wealth distribution
    wealth_distribution = np.random.lognormal(mean=11, sigma=1.2, size=10000)
    percentile = sum(wealth_distribution < total_wealth) / len(wealth_distribution) * 100
    return percentile

# Calculate wealth percentile
wealth_percentile = calculate_wealth_percentile(total_value)

# ---- Top Search/Add Bar ----
st.text_input("Search or Add Asset", placeholder="Search by name or category")

# ---- Persistent Page State ----
if "page" not in st.session_state:
    st.session_state.page = "Overview"

# ---- Bottom Navigation Buttons with Session State ----
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
    
    # Main metrics
    st.metric(label="Total Wealth", value=f"${total_value:,.2f}", delta=f"{total_change_percent:.2f}%")
    
    # Wealth percentile indicator
    st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <h3 style='margin-top: 0;'>Wealth Percentile</h3>
            <p>You are in the <span style='font-size: 24px; font-weight: bold; color: #1f77b4;'>{wealth_percentile:.1f}th</span> percentile of wealth among app users.</p>
            <div style='background-color: #ddd; height: 20px; border-radius: 10px; margin-top: 10px;'>
                <div style='background-color: #1f77b4; width: {wealth_percentile}%; height: 100%; border-radius: 10px;'></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Pie Chart
    if not df.empty:
        pie_df = df.groupby("category")['value'].sum().reset_index()
        fig = px.pie(pie_df, values='value', names='category', title='Asset Distribution')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No assets available. Please add assets in the Manage Assets section.")

# ---- Page 2: Performance by Category ----
elif page == "Performance by Category":
    st.markdown("<h2 style='text-align: center;'>Performance by Asset Category</h2>", unsafe_allow_html=True)
    
    if not df.empty:
        grouped = df.groupby("category").agg({"value": "sum", "change": "sum"}).reset_index()
        grouped["% Change"] = grouped.apply(lambda x: (x["change"] / (x["value"] - x["change"])) * 100 if (x["value"] - x["change"]) != 0 else 0, axis=1)
        
        # Format for display
        display_df = grouped.copy()
        display_df["value"] = display_df["value"].apply(lambda x: f"${x:,.2f}")
        display_df["change"] = display_df["change"].apply(lambda x: f"${x:,.2f}")
        display_df["% Change"] = display_df["% Change"].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df)
        
        fig = px.bar(grouped, x="category", y="% Change", title="% Change by Category")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No assets available. Please add assets in the Manage Assets section.")

# ---- Page 3: Manage Assets ----
elif page == "Manage Assets":
    st.markdown("<h2 style='text-align: center;'>Add or Modify Assets</h2>", unsafe_allow_html=True)
    
    # Add new asset form
    with st.form("asset_form"):
        st.subheader("Add New Asset")
        name = st.text_input("Asset Name")
        
        # Get existing categories or provide defaults
        existing_categories = df['category'].unique().tolist() if not df.empty else []
        default_categories = ["Real Estate", "Cars", "Watches", "Shares", "Wine", "Art", "Crypto", "Cash"]
        all_categories = list(set(existing_categories + default_categories))
        
        category = st.selectbox("Category", all_categories)
        value = st.number_input("Current Value", min_value=0.0, step=100.0)
        change = st.number_input("Daily/Monthly Change", step=10.0)
        submitted = st.form_submit_button("Add Asset")
        
        if submitted and name:  # Ensure name is not empty
            # Add new asset to session state
            new_asset = {"name": name, "category": category, "value": value, "change": change}
            st.session_state.assets_data.append(new_asset)
            st.success(f"Asset '{name}' added to {category} with value ${value:.2f}.")
            st.experimental_rerun()
    
    # Remove assets section
    st.subheader("Remove Assets")
    
    if not df.empty:
        # Display current assets with delete buttons
        for i, asset in enumerate(st.session_state.assets_data):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(asset["name"])
            with col2:
                st.write(asset["category"])
            with col3:
                st.write(f"${asset['value']:,.2f}")
            with col4:
                if st.button("Delete", key=f"delete_{i}"):
                    # Remove the asset and rerun
                    st.session_state.assets_data.pop(i)
                    st.success(f"Asset '{asset['name']}' removed.")
                    st.experimental_rerun()
    else:
        st.info("No assets available to remove. Please add assets using the form above.")
