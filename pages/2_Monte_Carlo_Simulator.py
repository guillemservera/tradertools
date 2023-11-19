import streamlit as st
import numpy as np
import plotly.graph_objs as go

st.set_page_config(
    page_title="Monte Carlo Simulator · Tradertools",
    page_icon="🧮"
)

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


# Informative message in the sidebar
st.sidebar.warning("""
    ⚠️This tool requires some time to perform simulations, 
    particularly when a large number of samples is entered.
""")


# Main section
st.markdown("""
    ## Monte Carlo Strategy Simulator
    This Monte Carlo Simulator allows traders to understand the range of potential outcomes of their trading strategy. 
    By inputting basic parameters such as win rate, average gain for winning trades (in terms of R), and average loss for losing trades, 
    you can simulate numerous scenarios of your strategy. The tool will provide visualizations and key metrics like maximum drawdown and consecutive losses,
    offering valuable insights into the risk and profitability of your strategy.
""")

st.divider()

# Inputs del usuario
account_size = st.number_input("Account Size ($)", min_value=0.0, value=10000.0, step=1000.0, format="%.2f")
win_rate = st.slider("Win Rate (%)", min_value=0, max_value=100, value=50)
average_win_r = st.number_input("Average Win (R)", value=1.0)
average_loss_r = st.number_input("Average Loss (R)", value=1.0)
num_simulations = st.number_input("Number of Simulations", min_value=1, value=1000)
num_trades = st.number_input("Number of Trades per Simulation", min_value=1, value=100)

# Función de simulación
def run_monte_carlo_simulations(account_size, win_rate, average_win_r, average_loss_r, num_simulations, num_trades):
    simulation_results = []
    for _ in range(num_simulations):
        trade_results = np.random.choice(
            [average_win_r, -average_loss_r],
            size=num_trades,
            p=[win_rate / 100.0, 1 - win_rate / 100.0]
        )
        equity_curve = np.cumsum(trade_results) * account_size / 100 + account_size
        simulation_results.append(equity_curve)
    return simulation_results

# Botón para ejecutar las simulaciones
if st.button("Run Simulations"):
    simulation_results = run_monte_carlo_simulations(account_size, win_rate, average_win_r, average_loss_r, num_simulations, num_trades)

    # Graficar los resultados con Plotly
    fig = go.Figure()
    for result in simulation_results:
        fig.add_trace(go.Scatter(y=result, mode='lines'))
    fig.update_layout(
        title="Monte Carlo Simulations of Trading Strategy",
        xaxis_title="Number of Trades",
        yaxis_title="Account Equity ($)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
