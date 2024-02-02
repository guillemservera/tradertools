import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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


# Monte Carlo simulation function including drawdown statistics
def monte_carlo_simulation(avg_win, avg_loss, std_dev, win_ratio, num_trades, num_simulations):
    simulations_results = np.zeros((num_simulations, num_trades))
    all_drawdowns = []

    expected_performance = avg_win * win_ratio + avg_loss * (1 - win_ratio)

    for sim in range(num_simulations):
        trade_results = []
        equity_curve = []
        for trade in range(num_trades):
            result = (avg_win + np.random.randn() * std_dev) if np.random.rand() < win_ratio else (avg_loss + np.random.randn() * std_dev)
            trade_results.append(result)
            equity_curve.append(sum(trade_results))

        simulations_results[sim] = equity_curve

        equity_highs = np.maximum.accumulate(equity_curve)
        drawdowns = (equity_curve - equity_highs) / equity_highs
        all_drawdowns.extend(drawdowns[drawdowns < 0])  # Only consider negative values as valid drawdowns

    max_drawdown = min(all_drawdowns)
    avg_drawdown = np.mean(all_drawdowns)
    median_drawdown = np.median(all_drawdowns)

    expected_equity_curve = np.arange(1, num_trades + 1) * expected_performance

    drawdown_stats = {
        'Max Drawdown (R)': max_drawdown,
        'Avg Drawdown (R)': avg_drawdown,
        'Median Drawdown (R)': median_drawdown
    }

    return simulations_results, expected_equity_curve, drawdown_stats



# Function to plot the simulation results with enhanced styling
def plot_monte_carlo_simulations(simulations_results, expected_equity_curve):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.subplots_adjust(top=0.85)

    for sim_results in simulations_results:
        ax.plot(sim_results, alpha=0.5, linewidth=0.5)

    ax.plot(expected_equity_curve, color='white', linestyle='--', label='Expected Performance', linewidth=2)
    ax.set_title('Monte Carlo Simulation of Trading Performance', fontsize=18, color='white', fontweight='bold', pad=20)
    ax.set_xlabel('Trade Number', fontsize=14, color='white')
    ax.set_ylabel('Cumulative Gain (R)', fontsize=14, color='white')
    ax.grid(color='gray', linestyle='-', linewidth=0.5)
    ax.spines['bottom'].set_color('grey')
    ax.spines['top'].set_color('grey') 
    ax.spines['right'].set_color('grey')
    ax.spines['left'].set_color('grey')
    ax.legend(loc='upper left', frameon=False)
    fig.text(0.95, 0.01, 'tradertools.streamlit.app | by @guillemservera', ha='right', va='bottom', fontsize=10, color='white', alpha=0.5)

    # Display the plot in Streamlit
    st.pyplot(fig)


# Main section
st.markdown("""
    ## Know your System | Monte Carlo Simulator
    Under construction. Coming soon... 
""")

st.divider()

# Input columns using number_input for better user input control
col1, col2, col3 = st.columns(3)

with col1:
    avg_win = st.number_input("Average Winning Trade (R)", value=1.0)
    avg_loss = st.number_input("Average Losing Trade (R)", value=-1.0)

with col2:
    std_dev = st.number_input("Trade Std. Dev. (R)", value=1.0)
    win_ratio = st.number_input("Win %", min_value=0.0, max_value=100.0, value=50.0) / 100  # Use a slider for percentage

with col3:
    num_trades = st.number_input("Number of Trades", min_value=1, value=100)
    num_simulations = st.number_input("Number of Simulations", min_value=1, value=100)



# Run the simulation and plot the results
if st.button('Run Simulation'):
    st.warning('Simulations may take some time to complete. Please, wait patiently...')
    results, expected_curve, drawdown_stats = monte_carlo_simulation(avg_win, avg_loss, std_dev, win_ratio, num_trades, num_simulations)
    
    # Clear the warning message
    st.empty()

    # Display the simulation chart
    st.markdown("#### Simulation Visualization")
    plot_monte_carlo_simulations(results, expected_curve)
    
    # Display the drawdown statistics below the plot
    st.markdown("#### Simulation Statistics")
    drawdown_data = {
        'Max Drawdown (R)': drawdown_stats['Max Drawdown (R)'],
        'Average Drawdown (R)': drawdown_stats['Avg Drawdown (R)'],
        'Median Drawdown (R)': drawdown_stats['Median Drawdown (R)']
    }
    st.table(drawdown_data)
