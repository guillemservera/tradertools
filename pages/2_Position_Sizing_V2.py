import streamlit as st
from math import floor, ceil
import pandas as pd

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

# SECTION FOR DEFINING FUNCTIONS ##################################

# Global list to store executions
if 'executions' not in st.session_state:
    st.session_state['executions'] = []

# Function to add an execution
def add_execution():
    entry = len(st.session_state['executions']) + 1
    shares = round(risk_amount / (entry_price - stop_price))  # Example calculation
    price_paid = entry_price
    stop_per_share = entry_price - stop_price
    st.session_state['executions'].append({
        "Entry": entry,
        "Shares": shares,
        "Risk": risk_amount,
        "Price Paid": price_paid,
        "Stop Price": stop_price,
        "Stop per Share": stop_per_share
    })

# Function to clean executions
def clean_executions():
    st.session_state['executions'] = []

####################################################################


# Main section for initial position sizing
st.markdown("""
    ## Position Sizing Tool
    Under construction. Coming soon... 

""")

st.divider()



col10, col20 = st.columns([3, 2])
with col10:
    # Section for Initial Position Sizing
    tab1, tab2 = st.tabs(["Initial Postion", "Pyramid"])


    with tab1:
        # Determine the risk type (assuming 'risk_type' is defined in your code)
        risk_type = st.radio("Select Risk Type:", ["Percentage of Account", "Fixed Amount"], key="risk_type", horizontal=True)

        if risk_type == "Percentage of Account":
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                account_size = st.number_input("Account Size ($):", min_value=0.0, value=25000.00, step=1000.0, format="%.2f",
                                            placeholder="Type your account size...", key="account_size")
            with col2:
                risk_percentage = st.number_input("Select your Risk (%):", min_value=0.05, max_value=10.0, value=1.0, step=0.05, format="%.2f",
                                                placeholder="Type your risk percentage...", key="risk_percentage")
                risk_amount = account_size * (risk_percentage / 100)
            with col3:
                stop_price = st.number_input("Stop Loss Price ($):", min_value=0.01, value=3.00, format="%.2f",
                                            placeholder="Type your stop price...", key="stop_price")
            with col4:
                entry_price = st.number_input("Entry Price ($):", min_value=stop_price, value=(stop_price + 0.01), format="%.2f",
                                            placeholder="Type your entry price...", key="entry_price")
        else:
            col2, col3, col4 = st.columns(3)
            with col2:
                risk_amount = st.number_input("Risk Amount ($):", min_value=0, value=100, step=1, key="fixed_risk_amount")

            with col3:
                stop_price = st.number_input("Stop Loss Price ($):", min_value=0.01, value=0.10, format="%.2f",
                                            placeholder="Type your stop price...", key="stop_loss")
            with col4:
                entry_price = st.number_input("Entry Price ($):", min_value=stop_price, value=(stop_price + 0.01), format="%.2f",
                                            placeholder="Type your entry price...", key="entry_price")


    with tab2:
        st.header("hi")

with col20:

    # Añadir botones con alineación y estilos personalizados
    col101, col201 = st.columns([1, 1])  # Ajusta el ratio según tus necesidades

    with col101:
        st.button("Add Execution", on_click=add_execution)

    with col201:
        st.button("Clean Executions", on_click=clean_executions)

    # Convertir la lista de ejecuciones en un DataFrame de Pandas
    df_executions = pd.DataFrame(st.session_state['executions'])

    # Estilo CSS personalizado para la tabla con el tema oscuro
    st.markdown("""
    <style>
    table {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
        background-color: #333333; /* Secondary background color */
    }
    th, td {
        border: 1px solid #444444;
        text-align: left;
        padding: 8px;
    }
    th {
        background-color: #56b0ff; /* Primary color */
        color: white;
    }
    tr:nth-child(even) {
        background-color: #242424; /* Slightly lighter than background for contrast */
    }
    tr:nth-child(odd) {
        background-color: #181818; /* Background color */
    }
    </style>
    """, unsafe_allow_html=True)

    # Mostrar la tabla sin el índice de fila
    st.write(df_executions.to_html(index=False), unsafe_allow_html=True)



st.metric("Risk (R)", f"{risk_amount} $")
st.metric("Shares", f"{account_size} sh")
st.metric("Average Price", "30")
st.metric("Average Price", "26")

st.markdown("####")



st.divider()



