import streamlit as st
from math import floor, ceil

st.set_page_config(
    page_title="Position Sizing | Tradertools",
    page_icon="🧮",
    layout="wide"  # Set the layout to wide
)

# Define the function to calculate and round the number of shares
def calculate_shares(risk_amount, stop_loss, rounding_method):
    number_of_shares = risk_amount / stop_loss
    if rounding_method == "Round Down":
        return floor(number_of_shares)
    elif rounding_method == "Round Up":
        return ceil(number_of_shares)
    elif rounding_method == "Round to nearest 10":
        return round(number_of_shares / 10) * 10
    elif rounding_method == "Round to nearest 50":
        return round(number_of_shares / 50) * 50
    elif rounding_method == "Round to nearest 100":
        return round(number_of_shares / 100) * 100
    else:
        return int(number_of_shares)  # No rounding

def display_results():
    shares = calculate_shares(risk_amount, stop_loss, rounding_method)
    formatted_shares = "{:,}".format(shares)
    st.markdown(f"<h3 style='text-align: left; color: white;'>You should buy <span style='font-size: 1.5em;'>{formatted_shares}</span> shares.</h3>", unsafe_allow_html=True)

st.header("Position Sizing")

st.divider()

# Radio button for selecting risk type
risk_type = st.radio("Choose your risk method:",
                     ("Percentage of Account", "Fixed Dollar Amount"), horizontal=True)

st.markdown('#####')

account_size = 0
risk_amount = 0
risk_percentage = 0
stop_loss = 0.01  # Default value
rounding_method = "No Rounding"  # Default value

# Conditional inputs based on risk type
if risk_type == "Percentage of Account":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        account_size = st.number_input("Enter the size of your account ($):", min_value=0.0, value=5000.00, step=1000.0, format="%.2f", key="account_size")
    with col2:
        risk_percentage = st.slider("Select your Risk (R) percentage:", 
                                    min_value=0.1, 
                                    max_value=3.0, 
                                    value=1.0, 
                                    step=0.10, 
                                    format="%.2f%%", key="risk_percentage")
        risk_amount = account_size * (risk_percentage / 100)
else:
    col2, col3, col4 = st.columns(3)
    with col2:
        risk_amount = st.number_input("Enter your fixed Risk amount ($):", min_value=0, value=100, step=1, key="fixed_risk_amount")

with col3:
    stop_loss = st.number_input("Enter your Stop Loss value ($):", min_value=0.01, format="%.2f", key="stop_loss")

with col4:
    rounding_options = ["No Rounding", "Round Down", "Round Up", "Round to nearest 10", "Round to nearest 50", "Round to nearest 100"]
    rounding_method = st.selectbox("Choose your rounding method:", rounding_options, key="rounding_method")

# Show R size in a styled manner if Percentage of Account is selected
if risk_type == "Percentage of Account":
    formatted_risk_amount = "${:,.2f}".format(risk_amount)
    st.markdown(f"<h4 style='text-align: left; color: white;'>Your R is: <span style='font-size: 1.2em;'>{formatted_risk_amount}</span></h4>", unsafe_allow_html=True)

# Call the function to display results at the end
display_results()
