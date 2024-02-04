import streamlit as st
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_UP
import re
import base64
from io import StringIO


st.set_page_config(
    page_title="TraderSync Helper · Tradertools",
    page_icon="⚙️",
    layout="wide"  # Set the layout to wide
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

# Constants for the fees
FINRA_TAF_RATE = Decimal('0.000145')
FINRA_TAF_CAP = Decimal('7.27')
SEC_FEE_RATE = Decimal('0.000008')

def calculate_finra_taf(quantity):
    # Calculate the FINRA TAF fee with a cap and round up to 0.0001
    fee = (FINRA_TAF_RATE * quantity).quantize(Decimal('0.0001'), rounding=ROUND_UP)
    return min(fee, FINRA_TAF_CAP)

def calculate_sec_fee(quantity, price):
    # Calculate the SEC fee and round up to the next penny only for sells
    fee = (SEC_FEE_RATE * quantity * price).quantize(Decimal('0.01'), rounding=ROUND_UP)
    return fee

def calculate_transaction_fee(quantity, price, side):
    # Calculate FINRA TAF for both buy and sell
    finra_taf_fee = calculate_finra_taf(quantity)

    # Initialize SEC fee to 0
    sec_fee = Decimal('0')

    # Calculate SEC fee only for sells
    if side == 'Sell':
        sec_fee = calculate_sec_fee(quantity, price)

    # The total transaction fee is the sum of both fees
    total_fee = finra_taf_fee + sec_fee
    return total_fee

def parse_trade_line(line):
    match = re.search(
        r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\s+(AM|PM)\s+ET\s+(Buy(?: to cover)?|Sell(?: Short)?)\s+(\d+)\s+([A-Z]+)\s+Executed\s+@\s+\$(\d+\.?\d*)', line
    )
    if match:
        date_ymd = datetime.strptime(match.group(1), '%m/%d/%y').strftime('%m/%d/%Y')
        time_24h = datetime.strptime(
            f"{match.group(1)} {match.group(2)} {match.group(3)}", '%m/%d/%y %I:%M %p'
        ).time()
        side = "Buy" if "Buy" in match.group(4) else "Sell"
        price = Decimal(match.group(7))
        return {
            'date': date_ymd,
            'time': time_24h,
            'side': side,
            'quantity': int(match.group(5)),
            'symbol': match.group(6),
            'price': price
        }
    else:
        return None

# Resto del código...


def format_trade(trade):
    trans_fee = calculate_transaction_fee(trade['quantity'], trade['price'], trade['side'])
    time_str = trade['time'].strftime('%H:%M:%S')
    return ','.join([
        trade['date'],
        time_str,
        trade['symbol'],
        str(trade['quantity']),
        str(trade['price']),
        trade['side'],
        '0.00',  # Comisión siempre es 0.00
        str(trans_fee)  # Tarifa de transacción
    ])

def main(file_obj):
    trades = []
    trade_times = {}
    formatted_trades = []

    trade_lines = [line.decode('utf-8') if isinstance(line, bytes) else line for line in file_obj.readlines()]

    for line in trade_lines:
        if 'Cancelled' not in line and 'Rejected' not in line:
            trade = parse_trade_line(line)
            if trade:
                trade_key = (trade['date'], trade['time'])
                if trade_key in trade_times:
                    previous_trade_index = trade_times[trade_key]
                    trades[previous_trade_index]['time'] = (datetime.combine(datetime.today(), trades[previous_trade_index]['time']) + timedelta(seconds=1)).time()
                trade_times[trade_key] = len(trades)
                trades.append(trade)
    
    for trade in trades:
        formatted_trades.append(format_trade(trade))
    
    return formatted_trades

def display_results_and_download_button(results, key):
    if results:
        header = "Date,Time,Symbol,Quantity,Price,Buy/Sell,Commission,Fee"
        result_text = '\n'.join([header] + results)
        st.text_area("Results", result_text, height=300, key=key)
        st.markdown(get_table_download_link_csv([header] + results), unsafe_allow_html=True)

def get_table_download_link_csv(results):
    csv = '\n'.join(results).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="tradersync_import.csv">Download CSV file</a>'
    return href


# Main section for initial position sizing
st.markdown("""
    ## TraderSync Trade Import Helper
    This tool is designed to format and adapt brokerage trade data for import into TraderSync. 
    Simply import or paste your data here, and the tool will convert it into the "Generic Import" required by TraderSync. 
    It will format the data correctly, including the date, time, symbol, quantity, price, side (buy/sell), and calculate fees, ensuring a seamless import process.
""")

st.divider()

broker = st.selectbox("Choose your broker", ["E*Trade Web Alerts"], index=0)


st.markdown("---")
st.subheader("Upload your text file with Alerts")
uploaded_file = st.file_uploader("Choose a file", type=['txt'])
if uploaded_file is not None:
    results = main(uploaded_file)
    # Pass a unique key for the uploaded file's results
    display_results_and_download_button(results, key="uploaded_file_results_text_area")

st.markdown("---")
st.subheader("Or paste your Alerts Text here")
trade_data = st.text_area("Paste the alerts", height=300, key="trade_data_text_area")
apply_button = st.button('Apply pasted data')
if apply_button and trade_data:
    from io import StringIO
    trade_data_file = StringIO(trade_data)
    results = main(trade_data_file)
    # Pass a unique key for the pasted data's results
    display_results_and_download_button(results, key="pasted_data_results_text_area")

# Disclaimer
st.markdown("""
    #     
    ---
    *This tool is intended for educational purposes only and its results should not be considered as investment advice.*
""")