import streamlit as st
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_UP
import re
import base64
from io import StringIO


st.set_page_config(
    page_title="Tradervue Fixer · Tradertools",
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
    # Ajustamos la expresión regular para capturar tanto "Sell Short" como "Buy to cover"
    match = re.search(
        r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\s+(AM|PM)\s+ET\s+(Buy(?: to cover)?|Sell(?: Short)?)\s+(\d+)\s+([A-Z]+)\s+Executed\s+@\s+\$(\d+\.?\d*)', line
    )
    if match:
        time_24h = datetime.strptime(
            f"{match.group(1)} {match.group(2)} {match.group(3)}", '%m/%d/%y %I:%M %p'
        ).time()
        side = "Buy" if "Buy" in match.group(4) else "Sell"  # Usamos "Buy" o "Sell" independientemente de si es corto o no
        price = Decimal(match.group(7))
        return {
            'date': match.group(1),
            'time': time_24h,
            'side': side,
            'quantity': int(match.group(5)),
            'symbol': match.group(6),
            'price': price
        }
    else:
        return None

def format_trade(trade):
    trans_fee = calculate_transaction_fee(trade['quantity'], trade['price'], trade['side'])
    # Format the time as a string again.
    time_str = trade['time'].strftime('%H:%M:%S')
    return ','.join([
        trade['date'],
        time_str,
        trade['symbol'],
        str(trade['quantity']),
        str(trade['price']),
        trade['side'],
        '0.00',  # Commission is always 0.00 as per the requirement
        str(trans_fee)  # Transaction Fee instead of Commission
    ])


# En la función main, decodifica cada línea antes de procesarla.
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
        header = "Date,Time,Symbol,Quantity,Price,Side,Commission,TransFee"
        result_text = '\n'.join([header] + results)
        st.text_area("Results", result_text, height=300, key=key)
        st.markdown(get_table_download_link_txt(results), unsafe_allow_html=True)


# Asegúrate de cambiar la función `get_table_download_link` para generar un enlace de descarga de .txt
def get_table_download_link_txt(results):
    csv = '\n'.join(results).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="trade_results.txt">Download TXT file</a>'
    return href


# Main section for initial position sizing
st.markdown("""
    ## Tradervue Trade Import Fixer
    This tool is designed to resolve common problems encountered when importing brokerage trade data into Tradervue. 
    Simply import or paste your data here, and the tool will generate a "Generic Import Format" suitable for Tradervue. 
    It will automatically correct known issues and include Fees & Commissions in the trade executions.
""")


st.divider()

broker = st.selectbox("Choose your broker", ["E*Trade Web Alerts"], index=0)


# Sección para subir archivo
st.markdown("---")  # Esto añadirá una línea horizontal.
st.subheader("Upload your text file with Alerts")
uploaded_file = st.file_uploader("Choose a file", type=['txt'])
if uploaded_file is not None:
    results = main(uploaded_file)
    # Pass a unique key for the uploaded file's results
    display_results_and_download_button(results, key="uploaded_file_results_text_area")

# Sección para pegar el contenido
st.markdown("---")  # Esto añadirá una línea horizontal.
st.subheader("Or paste your Alerts Text here")
trade_data = st.text_area("Paste the alerts", height=300, key="trade_data_text_area")
apply_button = st.button('Apply pasted data')
if apply_button and trade_data:
    from io import StringIO
    trade_data_file = StringIO(trade_data)
    results = main(trade_data_file)
    # Pass a unique key for the pasted data's results
    display_results_and_download_button(results, key="pasted_data_results_text_area")