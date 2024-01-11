import streamlit as st
from math import floor, ceil

# Setting up the page configuration
st.set_page_config(page_title="Position Sizing Helper · Tradertools", page_icon="🧮", layout="wide")

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
    elif method == "Round nearest 5":
        return round(shares / 5) * 5
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
def calculate_shares(risk_amount, stop_loss, rounding_method):
    number_of_shares = risk_amount / stop_loss
    return apply_rounding(number_of_shares, rounding_method)

# Function to display the initial number of shares and the real risk
def display_initial_shares():
    real_shares = calculate_shares(risk_amount, stop_loss, rounding_method)
    real_risk = real_shares * stop_loss  # Calculating real risk
    formatted_shares = "{:,}".format(int(real_shares))
    formatted_real_risk = "${:,.2f}".format(real_risk)  # Formatting real risk for display
    st.markdown(f"<h3 style='text-align: left; color: #56b0f0;'>You should buy <span style='font-size: 1.5em;'>{formatted_shares}</span> shares (R is <span style='font-size: 1em;'>{formatted_real_risk}</span>)</h3>", unsafe_allow_html=True)

# Main section for initial position sizing
st.markdown("""
    ## Position Sizing Tool
    Under construction. Coming soon... 

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
    rounding_options = ["No Rounding", "Round nearest 5", "Round nearest 10", "Round nearest 50", "Round nearest 100", "Round nearest 500", "Round nearest 1000"]
    rounding_method = st.selectbox("Rounding Method:", rounding_options, key="rounding_method")

# Show R size in a styled manner if Percentage of Account is selected
formatted_risk_amount = "${:,.2f}".format(risk_amount)

# Display the initial number of shares
display_initial_shares()

st.divider()


# Sección de Piramidación de Posiciones
st.markdown("### Pyramid into your Position")

# Botón de radio para el estilo de piramidación
pyramid_style = st.radio("Pyramid Style:", ("Full R", "Half R"), horizontal=True)

# Inputs para la piramidación
col5, col6, col7, col8 = st.columns(4)

with col5:
    current_shares = st.number_input("Current Position (shares):", min_value=0, value=int(calculate_shares(risk_amount, stop_loss, rounding_method)), format="%d")

with col6:
    average_price_paid = st.number_input("Average Price Paid ($):", min_value=0.01, value=st.session_state.get('average_price_paid', 1.00), format="%.2f")

with col7:
    current_price = st.number_input("Current Price ($):", min_value=0.01, value=(average_price_paid), format="%.2f")  # 10% más que el precio medio pagado

with col8:
    # El valor por defecto del Stop Price es igual al Average Price Paid
    stop_price = st.number_input("Stop Price ($):", min_value=0.01, value=average_price_paid, format="%.2f")

# Calcular la distancia al nuevo stop
distance_to_stop = current_price - stop_price


# Función para calcular acciones adicionales y el R
def calculate_additional_shares():
    profit_loss_per_share = current_price - average_price_paid
    total_profit_loss = profit_loss_per_share * current_shares

    # No permitir piramidación si se está añadiendo riesgo o promediando a la baja
    if current_price <= average_price_paid or total_profit_loss <= 0:
        return 0, "You can't pyramid, you are adding risk or averaging down!"

    # Verificamos que el stop price no sea superior al current price
    if stop_price >= current_price:
        return 0, "Warning: Stop price should be lower than current price."


    # Utilizamos ganancias no realizadas para determinar cuántas acciones adicionales se pueden comprar
    additional_risk_allowed = total_profit_loss if pyramid_style == "Full R" else total_profit_loss / 2
    additional_shares_potential = additional_risk_allowed / distance_to_stop
    rounded_additional_shares_potential = apply_rounding(additional_shares_potential, rounding_method)

    # Calculamos el riesgo real considerando solo las acciones que exceden el número de acciones financiadas por ganancias no realizadas
    additional_shares_real = max(0, rounded_additional_shares_potential - current_shares)
    real_risk = additional_shares_real * distance_to_stop

    return rounded_additional_shares_potential, real_risk

# Mostrar acciones adicionales y el R
additional_shares_potential, real_risk = calculate_additional_shares()

if isinstance(real_risk, str):
    st.error(real_risk)
else:
    formatted_additional_shares = "{:,}".format(additional_shares_potential)
    formatted_real_risk = "${:,.2f}".format(real_risk)
    st.markdown(f"<h3 style='text-align: left; color: #56b0f0;'>You can add <span style='font-size: 1.5em;'>{formatted_additional_shares}</span> more shares</h3>", unsafe_allow_html=True)
