
import streamlit as st
import requests
import os

# Flask API running in the sibling backend container
BACKEND_URL = "http://host.docker.internal:7860"

# Page setup
st.set_page_config(page_title="SuperKart Sales Prediction Platform", layout="centered")

# Custom theme: light glassmorphism, frosted cards, soft mesh background
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: "DM Sans", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(900px 480px at 8% -10%, rgba(125, 211, 252, 0.55), transparent 55%),
            radial-gradient(820px 460px at 96% 4%, rgba(196, 181, 253, 0.50), transparent 52%),
            radial-gradient(700px 420px at 50% 110%, rgba(167, 243, 208, 0.45), transparent 50%),
            linear-gradient(180deg, #f8fbff 0%, #eef4ff 45%, #f7f3ff 100%);
        color: #1e293b;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 880px;
    }

    /* Top banner */
    .hero {
        background: rgba(255, 255, 255, 0.42);
        border: 1px solid rgba(255, 255, 255, 0.72);
        border-radius: 24px;
        padding: 2.2rem 2rem 1.8rem;
        box-shadow: 0 18px 50px rgba(148, 163, 184, 0.18);
        backdrop-filter: blur(22px);
        -webkit-backdrop-filter: blur(22px);
        margin-bottom: 1.25rem;
    }

    .eyebrow {
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-size: 0.75rem;
        font-weight: 600;
        color: #0284c7;
        margin-bottom: 0.6rem;
    }

    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 2.05rem;
        line-height: 1.2;
        color: #0f172a;
        font-weight: 700;
    }

    .hero p {
        margin: 0;
        color: #475569;
        font-size: 1.02rem;
        line-height: 1.65;
        max-width: 640px;
    }

    /* Model summary chips */
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin: 0.4rem 0 0.6rem;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.48);
        border: 1px solid rgba(255, 255, 255, 0.78);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        box-shadow: 0 10px 28px rgba(148, 163, 184, 0.12);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .stat-label {
        color: #64748b;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.25rem;
    }

    .stat-value {
        color: #0369a1;
        font-size: 1.05rem;
        font-weight: 700;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 650;
        color: #0f172a;
        margin: 0.4rem 0 1rem;
    }

    .section-copy {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.1rem;
    }

    /* Center and style the predict button */
    div.stButton {
        text-align: center;
        display: flex;
        justify-content: center;
    }

    .stButton button {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 0.8rem 2rem !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.55) !important;
        font-size: 1rem !important;
        max-width: 320px;
        width: 100%;
        box-shadow: 0 12px 28px rgba(99, 102, 241, 0.22);
    }

    .stButton button:hover {
        filter: brightness(1.05);
    }

    /* Result metric card */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 18px;
        padding: 1rem 1.2rem;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 10px 24px rgba(148, 163, 184, 0.14);
    }

    [data-testid="stMetricValue"] {
        color: #0369a1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Page header and short product description
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Retail forecasting</div>
        <h1>SuperKart Sales Desk</h1>
        <p>
            Get a quick store-level sales estimate from product and location details.
            Use it to sense-check pricing, shelf space, and store mix before you lock inventory.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Static model info (display only)
st.markdown(
    """
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-label">Model</div>
            <div class="stat-value">Random Forest</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Holdout fit</div>
            <div class="stat-value">91% R²</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Input section heading
st.markdown('<div class="section-title">Product and store details</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Fill in the fields below. The estimate is for that product in that store.</div>',
    unsafe_allow_html=True,
)

# Two-column form. Field names, defaults, and options stay the same.
col1, col2 = st.columns(2)

with col1:
    Product_Weight = st.number_input(
        "Product Weight",
        min_value=0.0,
        value=13.80,
        help="Weight of the product (numerical value)",
    )

    Product_Sugar_Content = st.selectbox(
        "Product Sugar Content",
        ["Low Sugar", "Regular", "No Sugar"]
    )

    Product_Allocated_Area = st.number_input(
        "Product Allocated Area",
        min_value=0.0,
        value=0.035,
        help="Ratio of the allocated display area of each product to the total display area of all the products in a store",
    )

    Product_MRP = st.number_input(
        "Product MRP",
        min_value=0.0,
        value=123.20,
        help="Maximum retail price of each product (numerical value)",
    )

    Store_Size = st.selectbox(
        "Store Size",
        [ "Small", "Medium", "High"],
    )

with col2:
    Store_Location_City_Type = st.selectbox(
        "Store Location City Type",
        ["Tier 1", "Tier 2", "Tier 3"]
    )

    Store_Type = st.selectbox(
        "Store Type",
        ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"]
    )

    Store_Age_Years = st.number_input(
        "Store Age (Years)",
        min_value=0,
        value=20,
        help="Age of the store")

    Product_Type_Category = st.selectbox(
        "Product Type Category",
        [
          "Perishables",
          "Non Perishables"
        ]
    )

    Product_Id_char = st.selectbox(
        "Product Id char",
        ["FD", "NC", "DR"]
    )

st.divider()

# Send the same payload the backend already expects
if st.button("⚡ Run Prediction", type="primary", use_container_width=True):

    # Basic required-field checks
    if Product_Weight == 0.0:
        st.warning("⚠️ Please enter a valid Product Weight")
    elif Product_MRP == 0.0:
        st.warning("⚠️ Please enter a valid Product MRP")
    else:
        # Request body for POST /v1/predict
        product_data = {
            "Product_Weight": Product_Weight,
            "Product_Sugar_Content": Product_Sugar_Content,
            "Product_Allocated_Area": Product_Allocated_Area,
            "Product_MRP": Product_MRP,
            "Store_Size": Store_Size,
            "Store_Location_City_Type": Store_Location_City_Type,
            "Store_Type": Store_Type,
            "Store_Age_Years": Store_Age_Years,
            "Product_Type_Category": Product_Type_Category,
            "Product_Id_char": Product_Id_char
        }

        # Call the backend and show the predicted sales
        with st.spinner("Running prediction..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/v1/predict",
                    json=product_data,
                    headers={
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    predicted_sales = result.get("Sales", 0)

                    st.success("✅ Prediction Complete!")
                    st.metric(
                            label="Predicted Sales",
                            value=f"£{predicted_sales:.2f}"
                        )
                else:
                    st.error(f"❌ Error in API request: {response.status_code}")

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
