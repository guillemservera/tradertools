import streamlit as st
from math import floor, ceil

# Setting up the page configuration
st.set_page_config(page_title="Position Sizing | Tradertools", page_icon="🧮", layout="wide")

# Function to apply rounding based on the selected method
def apply_rounding(shares, method):
    if method == "No Rounding":
        # Round up if very close to the next hundred
        if shares % 100 > 90:
            return (shares // 100 + 1) * 100
        return int(shares)
    elif method == "Round Down":
        return floor(shares)
    elif method == "Round Up":
        return ceil(shares)
    elif method == "Round to nearest 10":
        return round(shares / 10) * 10
    elif method == "Round to nearest 50":
        return round(shares / 50) * 50
    elif method == "Round to nearest 100":
        return round(shares / 100) * 100

# Function to calculate the initial number of shares based on risk, stop loss, and rounding method
def calculate_shares(risk_amount, stop_loss, rounding_method):
    number_of_shares = risk_amount / stop_loss
    return apply_rounding(number_of_shares, rounding_method)

# Function to display the initial number of shares to buy
def display_initial_shares():
    shares = calculate_shares(risk_amount, stop_loss, rounding_method)
    formatted_shares = "{:,}".format(int(shares))
    st.markdown(f"<h3 style='text-align: left; color: #56b0f0;'>You should buy <span style='font-size: 1.5em;'>{formatted_shares}</span> shares (R is <span style='font-size: 1em;'>{formatted_risk_amount}</span>)</h3>", unsafe_allow_html=True)

# Main section for initial position sizing
st.markdown("""
    ## Position Sizing Tool for Traders
    Use this tool to calculate the ideal number of shares to buy based on your own risk management.
    Simply input your account size, risk preference, and stop loss to get started.
""")

st.divider()

# Section for Initial Position Sizing
st.markdown("### Initial Position Sizing")

st.markdown("####")

# Radio button for selecting risk type
risk_type = st.radio("Risk Method:",
                     ("Percentage of Account", "Fixed Dollar Amount"), horizontal=True)

st.markdown("#####")

# Conditional inputs based on risk type
if risk_type == "Percentage of Account":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        account_size = st.number_input("Account Size ($):", min_value=0.0, value=10000.00, step=1000.0, format="%.2f", key="account_size")
    with col2:
        risk_percentage = st.number_input("Select your Risk (%):", min_value=0.05, max_value=3.0, value=1.0, step=0.05, format="%.2f", key="risk_percentage")
        risk_amount = account_size * (risk_percentage / 100)
else:
    col2, col3, col4 = st.columns(3)
    with col2:
        risk_amount = st.number_input("Risk Amount ($):", min_value=0, value=100, step=1, key="fixed_risk_amount")

with col3:
    stop_loss = st.number_input("Stop Loss Distance ($):", min_value=0.01, value=0.10, format="%.2f", key="stop_loss")

with col4:
    rounding_options = ["No Rounding", "Round Down", "Round Up", "Round to nearest 10", "Round to nearest 50", "Round to nearest 100"]
    rounding_method = st.selectbox("Rounding Method:", rounding_options, key="rounding_method")

# Show R size in a styled manner if Percentage of Account is selected
formatted_risk_amount = "${:,.2f}".format(risk_amount)

# Display the initial number of shares
display_initial_shares()

st.divider()

# Sección de Piramidación de Posiciones
st.markdown("### Pyramid into your Position")

st.markdown("####")

# Botón de radio para el estilo de piramidación
pyramid_style = st.radio("Pyramid Style:", ("Full R", "Half R"), horizontal=True)

st.markdown("#####")

# Inputs for pyramid position sizing
col5, col6, col7, col8 = st.columns(4)

with col5:
    current_shares = st.number_input("Current Position (shares):", min_value=0, value=int(calculate_shares(risk_amount, stop_loss, rounding_method)), format="%d")

with col6:
    average_price_paid = st.number_input("Average Price Paid ($):", min_value=0.01, value=1.00, format="%.2f")

with col7:
    current_price = st.number_input("Current Price ($):", min_value=0.01, value=1.00, format="%.2f")

with col8:
    distance_to_stop = st.number_input("Distance to New Stop ($):", min_value=0.01, value=0.10, format="%.2f")

# Función to calculate additional shares
def calculate_additional_shares():
    profit_loss_per_share = current_price - average_price_paid
    total_profit_loss = profit_loss_per_share * current_shares
    adjusted_risk_amount = (risk_amount / 2) if pyramid_style == "Half R" else risk_amount  # Ajuste del riesgo basado en el estilo de piramidación
    adjusted_risk_amount += total_profit_loss
    new_stop_loss = current_price - distance_to_stop
    new_risk_per_share = current_price - new_stop_loss
    total_shares_possible = adjusted_risk_amount / new_risk_per_share if new_risk_per_share > 0 else 0
    additional_shares = max(0, total_shares_possible - current_shares)
    return apply_rounding(additional_shares, rounding_method)

additional_shares = calculate_additional_shares()
formatted_additional_shares = "{:,}".format(int(additional_shares))
st.markdown(f"<h3 style='text-align: left; color: #56b0f0;'>You should add <span style='font-size: 1.5em;'>{formatted_additional_shares}</span> shares</h3>", unsafe_allow_html=True)
