import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter


# Set page configuration
st.set_page_config(page_title="Know your System · Tradertools", page_icon="🔢", layout="wide")

# Function to add custom logo
def add_logo():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "tradertools";
                display: block;
                font-weight: bold;
                margin-left: 25px;
                margin-top: 0px;
                margin-bottom: 0px;
                font-size: 2em;
                position: relative;
                top: 40px;
            }
        </style>
        """, unsafe_allow_html=True)

# Call the function to add the logo
add_logo()


# Function for Monte Carlo simulation including drawdown statistics
def monte_carlo_simulation(avg_win, avg_loss, std_dev, win_ratio, num_trades, num_simulations):
    # Initialize arrays to store simulation results and drawdowns
    simulations_results = np.zeros((num_simulations, num_trades))
    all_drawdowns = []

    # Calculate expected performance based on given stats
    expected_performance = avg_win * win_ratio + avg_loss * (1 - win_ratio)

    # Loop over each simulation
    for sim in range(num_simulations):
        trade_results = []
        equity_curve = []
        # Loop over each trade within a simulation
        for trade in range(num_trades):
            # Determine trade result based on win ratio and add random variation
            result = (avg_win + np.random.randn() * std_dev) if np.random.rand() < win_ratio else (avg_loss + np.random.randn() * std_dev)
            trade_results.append(result)
            equity_curve.append(sum(trade_results))

        simulations_results[sim] = equity_curve

        # Calculate drawdowns from the equity curve
        equity_highs = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - equity_highs) / equity_highs
        all_drawdowns.extend(drawdowns[drawdowns < 0])  # Only negative values are considered valid drawdowns

    # Calculate drawdown statistics
    max_drawdown = min(all_drawdowns)
    avg_drawdown = np.mean(all_drawdowns)
    median_drawdown = np.median(all_drawdowns)

    # Calculate expected equity curve based on expected performance
    expected_equity_curve = np.arange(1, num_trades + 1) * expected_performance

    # Package drawdown stats in a dictionary
    drawdown_stats = {
        'Max Drawdown (R)': max_drawdown,
        'Avg Drawdown (R)': avg_drawdown,
        'Median Drawdown (R)': median_drawdown
    }

    return simulations_results, expected_equity_curve


# Function to simulate the equity curve based on trading parameters
def simulate_equity_curve(balance, risk_per_trade, win_percent, win_loss_ratio, num_trades, num_simulations, risk_type):
    """
    Simulate multiple equity curves based on the specified trading parameters.
    
    Args:
    - balance: Initial trading balance.
    - risk_per_trade: Risk per trade, as a percentage of equity or fixed dollar amount.
    - win_percent: Percentage of winning trades.
    - win_loss_ratio: Ratio of average win to average loss.
    - num_trades: Number of trades per simulation.
    - num_simulations: Number of simulations to run.
    - risk_type: 'Percentage of Equity' or 'Fixed Dollar Amount' to specify how risk is calculated.
    
    Returns:
    - A list of equity curves, one for each simulation.
    """
    simulations_results = []
    for _ in range(num_simulations):
        equity_curve = [balance]
        for _ in range(num_trades):
            current_balance = equity_curve[-1]
            if risk_type == "Percentage of Equity":
                trade_risk = current_balance * (risk_per_trade / 100)
            else:  # Fixed Dollar Amount
                trade_risk = risk_per_trade

            trade_result = np.random.rand()
            if trade_result < win_percent / 100:
                # Win
                profit_loss = trade_risk * win_loss_ratio
            else:
                # Loss
                profit_loss = -trade_risk

            new_balance = current_balance + profit_loss
            equity_curve.append(new_balance)

        simulations_results.append(equity_curve)

    return simulations_results


# Custom formatter function for the Y-axis
def format_func(value, tick_number):
    """
    Converts numerical value to a string with K, M, or B suffix.
    Args:
    - value: The numerical value of the tick.
    - tick_number: The tick number (unused here but required by FuncFormatter).
    Returns:
    - Formatted string with appropriate suffix.
    """
    if value >= 1_000_000_000:
        return f'{value / 1_000_000_000:.1f}B'
    elif value >= 1_000_000:
        return f'{value / 1_000_000:.1f}M'
    elif value >= 1_000:
        return f'{value / 1_000:.1f}K'
    else:
        return int(value)


# Custom formatter for logarithmic scale, adjusting labels to reflect K, M, or B
def log_format_func(value, pos):
    """
    Converts log-scaled tick values to formatted strings with K, M, or B suffix.
    This function assumes that the input 'value' is the logarithm of the actual value.
    """
    # Convert the log value back to the real value
    real_value = np.power(10, value)
    if real_value >= 1_000_000_000:
        return f'{real_value / 1_000_000_000:.1f}B'
    elif real_value >= 1_000_000:
        return f'{real_value / 1_000_000:.1f}M'
    elif real_value >= 1_000:
        return f'{real_value / 1_000:.1f}K'
    else:
        return f'{real_value:.1f}'
    
class CustomScalarFormatter(ScalarFormatter):
    def __call__(self, x, pos=None):
        # Esta función se llama para cada tick; `x` es el valor original
        if x >= 1_000_000_000:
            return f'{x / 1_000_000_000:.1f}B'
        elif x >= 1_000_000:
            return f'{x / 1_000_000:.1f}M'
        elif x >= 1_000:
            return f'{x / 1_000:.1f}K'
        else:
            return f'{x:.1f}'

# Adjust the plot_monte_carlo_simulations function to use the custom formatter
def plot_monte_carlo_simulations(simulations_results, expected_equity_curve, x_label='Trade Number', y_label='Equity ($)', scale_type='Arithmetic Scale'):
    """
    Plots the results of Monte Carlo simulations with options for custom axis labels
    and a choice between arithmetic and logarithmic scale for the Y-axis.

    Args:
    - simulations_results: A list of lists or a numpy array containing the simulation results.
    - expected_equity_curve: A list containing the expected equity curve. Can be None.
    - x_label: The label for the X-axis.
    - y_label: The label for the Y-axis.
    - scale_type: 'Arithmetic Scale' or 'Logarithmic Scale' to specify the Y-axis scale.
    """
    plt.style.use('dark_background')  # Use dark theme for the plot
    fig, ax = plt.subplots(figsize=(14, 8))  # Set figure size


    # Apply 'plain' formatting to avoid scientific notation
    ax.ticklabel_format(style='plain', axis='y', useOffset=False)

    # Set the Y-axis scale and formatter based on the user's choice
    if scale_type == 'Logarithmic Scale':
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(CustomScalarFormatter())
    else:
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))


    # Plot simulation results and expected performance curve if provided
    for sim_results in simulations_results:
        ax.plot(sim_results, alpha=0.75, linewidth=0.7)
    if expected_equity_curve is not None:
        ax.plot(expected_equity_curve, color='white', linestyle='--', label='Expected Performance', linewidth=2)

    # Set plot properties including custom axis labels
    ax.set_xlabel(x_label, fontsize=14, color='white')
    ax.set_ylabel(y_label, fontsize=14, color='white')
    ax.set_title('Monte Carlo Simulation of Trading Performance', fontsize=18, color='white', fontweight='bold')
    ax.grid(color='gray', linestyle='-', linewidth=0.5)
    ax.spines['bottom'].set_color('grey')
    ax.spines['top'].set_color('grey')
    ax.spines['right'].set_color('grey')
    ax.spines['left'].set_color('grey')
    if expected_equity_curve is not None:
        ax.legend(loc='upper left', frameon=False)
    fig.text(0.95, 0.01, 'tradertools.streamlit.app', ha='right', va='bottom', fontsize=10, color='white', alpha=0.85)

    # Display the plot in Streamlit
    st.pyplot(fig)



# Main section with introduction to Monte Carlo simulation
st.markdown("""
            ## Know Your System - Monte Carlo Simulator
            Monte Carlo Simulation, or the Monte Carlo Method, is a computer simulation technique designed to estimate the potential outcomes of various scenarios. For traders, this method is invaluable for estimating a strategy's viability and potential return variability.
            # 
            """)

# Create tabs for different simulation options
tab1, tab2 = st.tabs(["Equity Curve Simulator", "Know Your System"])

# Tab 1: Equity Curve Simulator
with tab1:
    st.markdown("""
    ##### Monte Carlo Equity Curve Simulator
    Simulate the evolution of your trading equity using your own trading stats. Adjust your initial balance, risk per trade, and other parameters to visualize how your capital might grow over time under different market conditions.
    # 
    """)

    # Create two columns for log scale option and risk method selection
    col_risk, col_scale = st.columns(2)

    with col_risk:
        risk_type = st.radio(
            "Choose How to Compute your Risk per Trade:",
            ("Percentage of Equity", "Fixed Dollar Amount"),
            key='risk_type_tab2', horizontal=True
        )

    with col_scale:
        use_log_scale = st.radio(
            "Choose scale for Y-axis:",
            ("Arithmetic Scale", "Logarithmic Scale"),
            key='use_log_scale', horizontal=True
        )



    # Initialize input columns for initial balance and trading stats below the options
    col4, col5, col6 = st.columns(3)
    with col4:
        balance = st.number_input("Initial Balance ($)", value=10000.0, key='balance_tab2')
        # Conditional input for risk per trade based on the selected risk method
        if risk_type == "Percentage of Equity":
            risk_per_trade = st.number_input("Risk per Trade (%)", min_value=0.01, max_value=100.0, value=1.0, step=0.01, key='risk_per_trade_percent')
        else:
            risk_per_trade = st.number_input("Risk per Trade ($)", min_value=1.0, value=100.0, step=1.0, key='risk_per_trade_dollar')

    with col5:
        win_percent = st.number_input("Winning Trades (%)", value=50.0, key='win_percent_tab2')
        win_loss_ratio = st.number_input("Win/Loss Ratio", value=1.0, key='win_loss_ratio_tab2')

    with col6:
        trades = st.number_input("Number of Trades", min_value=1, value=100, key='trades_tab2')
        simulations = st.number_input("Number of Simulations", min_value=1, value=100, key='simulations_tab2')

    # Button to trigger the simulation
    if st.button('Run Simulation', key='simulate_equity_curve'):
        st.warning('Simulations may take some time to complete. Please, wait patiently...')
        # Perform Monte Carlo simulation and display results
        simulations_results = simulate_equity_curve(balance, risk_per_trade, win_percent, win_loss_ratio, trades, 
                                                    simulations, risk_type)
        st.empty()
        
        st.markdown("#### Simulation Visualization")
        plot_monte_carlo_simulations(
            simulations_results=simulations_results, 
            expected_equity_curve=None,
            x_label='Trade Number', 
            y_label='Equity ($)', 
            scale_type=use_log_scale 
        )


# Tab 2: Know Your System
with tab2:
    st.markdown("""
    ##### 
    ##### Monte Carlo Simulator Based on Van K. Tharp's Methods
    Input your trading system's stats in R (Risk) units, including standard deviation. This tool will help you understand the expected variability in your trading outcomes, making informed strategic decisions easier.
    #
    """)
    # Initialize input columns for trading system stats
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_win = st.number_input("Average Winning Trade (R)", value=1.0, key='avg_win')
        avg_loss = st.number_input("Average Losing Trade (R)", value=-1.0, key='avg_loss')

    with col2:
        std_dev = st.number_input("Trade Std. Dev. (R)", value=1.0, key='std_dev')
        win_ratio = st.number_input("Win %", min_value=0.0, max_value=100.0, value=50.0, key='win_ratio') / 100

    with col3:
        num_trades = st.number_input("Number of Trades", min_value=1, value=100, key='num_trades_tab1')
        num_simulations = st.number_input("Number of Simulations", min_value=1, value=100, key='num_simulations_tab1')

    # Button to run the simulation
    if st.button('Run Simulation'):
        st.warning('Simulations may take some time to complete. Please, wait patiently...')
        # Perform Monte Carlo simulation and display results
        results, expected_curve = monte_carlo_simulation(avg_win, avg_loss, std_dev, win_ratio, num_trades, num_simulations)
        
        # Clear warning message after simulation is complete
        st.empty()

        # Display the simulation chart
        st.markdown("#### Simulation Visualization")
        plot_monte_carlo_simulations(results, expected_curve)
        

# Display a disclaimer for educational purposes
st.markdown("""
    #     
    ---
    *This tool is intended for educational purposes only and its results should not be considered as investment advice.*
""")