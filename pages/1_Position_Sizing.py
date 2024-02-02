import streamlit as st
from math import floor, ceil

# Setting up the page configuration
st.set_page_config(page_title="Position Sizing · Tradertools", page_icon="🧮", layout="wide")

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
            content: "tradertools";
            display: block;
            font-weight: bold; /* Makes the font bold */
            margin-left: 25px;
            margin-top: 0px;
            margin-botton: 0px;
            font-size: 2em;
            position: relative;
            top: 40px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

add_logo()

# Function to apply rounding based on the selected method
def apply_rounding(shares, method):
    if method == "No Rounding":
        return ceil(shares) 
    elif method == "Round nearest 10":
        return round(shares / 10) * 10
    elif method == "Round nearest 50":
        return round(shares / 50) * 50
    elif method == "Round nearest 100":
        return round(shares / 100) * 100
    elif method == "Round nearest 500":
        return round(shares / 500) * 500
    elif method == "Round nearest 1000":
        return round(shares / 1000) * 1000

# Function to calculate the initial number of shares based on risk, stop loss, and rounding method
def calculate_shares(risk_amount, buy_price, stop_loss_price, rounding_method):
    stop_loss_distance = abs(buy_price - stop_loss_price)
    number_of_shares = risk_amount / stop_loss_distance
    return apply_rounding(number_of_shares, rounding_method)

# Function to display the initial number of shares and the real risk
def display_initial_shares():
    real_shares = calculate_shares(risk_amount, buy_price, stop_loss_price, rounding_method)
    stop_loss_distance = abs(buy_price - stop_loss_price)
    real_risk = real_shares * stop_loss_distance
    formatted_shares = "{:,}".format(int(real_shares))
    formatted_real_risk = "${:,.2f}".format(real_risk)  # Formatting real risk for display
    st.markdown(f"<h3 style='text-align: left; color: #56b0f0;'>You should buy <span style='font-size: 1.5em;'>{formatted_shares}</span> shares (R is <span style='font-size: 1em;'>{formatted_real_risk}</span>)</h3>", unsafe_allow_html=True)


# Main section for initial position sizing
st.markdown("""
            ## Position Sizing Helper
            This tool assists you in calculating the ideal number of shares to buy based on 
            your individual risk tolerance and strategy making it easy to manage risk using Risk units (R).
            """)

st.divider()

# Section for Initial Position Sizing
st.markdown("### Initial Position Sizing")

st.markdown("####")

# Radio button for selecting risk type and rounding method
col10, col20 = st.columns(2)
with col10:
    risk_type = st.radio("Risk Method:",
                     ("Percentage of Account", "Fixed Dollar Amount"), horizontal=True)
with col20:
    rounding_options = ["No Rounding", "Round nearest 10", "Round nearest 50", "Round nearest 100", "Round nearest 500", "Round nearest 1000"]
    rounding_method = st.selectbox("Rounding Method:", rounding_options, key="rounding_method") 

st.markdown("#####")

# Conditional inputs based on risk type
if risk_type == "Percentage of Account":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        account_size = st.number_input("Account Size ($):", min_value=0.0, value=2000.00, step=1000.0, format="%.2f", key="account_size")
    with col2:
        risk_percentage = st.number_input("Select your Risk (%):", min_value=0.05, max_value=3.0, value=1.0, step=0.05, format="%.2f", key="risk_percentage")
        risk_amount = account_size * (risk_percentage / 100)
else:
    col2, col3, col4 = st.columns(3)
    with col2:
        risk_amount = st.number_input("Risk Amount ($):", min_value=0, value=100, step=1, key="fixed_risk_amount")

with col3:
    stop_loss_price = st.number_input("Stop Loss Price ($):", min_value=0.01, value=1.0, format="%.2f", key="stop_loss_price")

with col4:
    buy_price = st.number_input("Entry Price ($):", min_value=0.01, value=1.05, format="%.2f", key="buy_price")
    


# Show R size
formatted_risk_amount = "${:,.2f}".format(risk_amount)

# Display the initial number of shares
display_initial_shares()

st.divider()


# Sección para la Piramidación de Posiciones
st.markdown("### Pyramid into your Position")
st.markdown("Section Under Construction ⚠️")