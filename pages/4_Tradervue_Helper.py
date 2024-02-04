import streamlit as st
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_UP
import re
import base64
from io import StringIO
import pandas as pd


st.set_page_config(
    page_title="Tradervue Helper · Tradertools",
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
    # La tarifa FINRA TAF se aplica tanto a compras como a ventas
    finra_taf_fee = calculate_finra_taf(quantity)

    # Inicializar la tarifa SEC a 0
    sec_fee = Decimal('0')

    # Aplicar la tarifa SEC solo para ventas (Sell y Short)
    if side in ['Sell', 'Short']:
        sec_fee = calculate_sec_fee(quantity, price)

    # La tarifa total de la transacción es la suma de ambas tarifas
    return finra_taf_fee + sec_fee


def parse_trade_line(line):
    # Ajustamos la expresión regular para capturar "Sell Short", "Buy to cover", además de "Buy" y "Sell"
    match = re.search(
        r'(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\s+(AM|PM)\s+ET\s+(Buy(?: to cover)?|Sell(?: Short)?)\s+(\d+)\s+([A-Z]+)\s+(?:Executed\s+)?@\s+\$(\d+\.?\d*)\s*(?:Executed)?', line
    )
    if match:
        time_24h = datetime.strptime(
            f"{match.group(1)} {match.group(2)} {match.group(3)}", '%m/%d/%y %I:%M %p'
        ).time()

        # Cambiamos la lógica aquí para asignar correctamente "Short", "Cover", "Buy" o "Sell"
        if "Sell Short" in match.group(4):
            side = "Short"
        elif "Buy to cover" in match.group(4):
            side = "Cover"
        else:
            side = match.group(4)  # Será "Buy" o "Sell"

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

def process_power_etrade_csv(file_obj):
    # Leer el archivo CSV, omitiendo la primera fila que es un encabezado
    df = pd.read_csv(file_obj, skiprows=1)

    # Procesar cada fila
    processed_trades = []
    for _, row in df.iterrows():
        processed_trade = process_power_etrade_trade(row)
        if processed_trade:
            processed_trades.append(processed_trade)
    return processed_trades

def process_power_etrade_trade(row):
    # Extraer los campos relevantes
    symbol = row['Symbol']
    status = row['Status']
    fill_info = row['Fill']
    description = row['Description']
    time_str = row['Time']

    # Ignorar las filas sin información de "Fill"
    if fill_info == '--':
        return None

    # Extraer cantidad y precio
    quantity_str, price_str = fill_info.split('@')
    quantity = Decimal(re.search(r'(\d+)', quantity_str).group(1))
    price = Decimal(price_str.strip()) if '@' in fill_info else Decimal('0.00')

    # Determinar el tipo de operación (Side)
    if "Sell" in description and "to Open" in description:
        side = "Short"
    elif "Buy" in description and "to Close" in description:
        side = "Cover"
    elif "Buy" in description and "to Open" in description:
        side = "Buy"
    elif "Sell" in description and "to Close" in description:
        side = "Sell"
    else:
        side = 'Unknown'

    # Extraer fecha y hora
    date = datetime.strptime(time_str.split(',')[0], '%m/%d/%Y').date()
    time = datetime.strptime(time_str.split(',')[1].strip(), '%I:%M:%S %p').time()

    # Calcular tarifas
    trans_fee = calculate_transaction_fee(quantity, price, side)

    # Formatear la operación al estilo de Tradervue
    trade_format = ','.join([
        date.strftime('%m/%d/%Y'),
        time.strftime('%H:%M:%S'),
        symbol,
        str(quantity),
        str(price),
        side,
        '0.00',  # Comisión siempre es 0.00
        str(trans_fee)  # Tarifa de transacción
    ])
    return trade_format


def main(file_obj):
    trades = {}
    formatted_trades = []

    trade_lines = [line.decode('utf-8') if isinstance(line, bytes) else line for line in file_obj.readlines()]

    for line in trade_lines:
        if 'Cancelled' not in line and 'Rejected' not in line:
            trade = parse_trade_line(line)
            if trade:
                # Creamos una clave única basada en la fecha, hora, símbolo, precio y lado de la transacción
                trade_key = (trade['date'], trade['time'], trade['symbol'], trade['price'], trade['side'])
                
                # Si la clave existe, agregamos la cantidad a la ejecución existente
                if trade_key in trades:
                    trades[trade_key]['quantity'] += trade['quantity']
                else:
                    trades[trade_key] = trade

    for trade in trades.values():
        formatted_trades.append(format_trade(trade))
    
    return formatted_trades

def display_results_and_download_button(results, key, filename="tradervue_generic_import.txt"):
    if results:
        header = "Date,Time,Symbol,Quantity,Price,Side,Commission,TransFee"
        result_text = '\n'.join([header] + results)
        st.text_area("Results", result_text, height=300, key=key)
        b64 = base64.b64encode(result_text.encode()).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download TXT file</a>'
        st.markdown(href, unsafe_allow_html=True)



def get_table_download_link_txt(results):
    csv = '\n'.join(results).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="tradervue_generic_import.txt">Download TXT file</a>'
    return href


st.markdown("""
    ## Tradervue Trade Import Helper
    This tool is designed to resolve common problems encountered when importing brokerage trade data into Tradervue. 
    Simply import or paste your data here, and the tool will generate a "Generic Import Format" suitable for Tradervue. 
    It will automatically correct known issues and include Fees & Commissions in the trade executions.
""")


st.divider()


# Selector de bróker actualizado con las dos opciones
broker_options = ["E*Trade Web Alerts", "Power E*Trade Web App"]
broker = st.selectbox("Choose your broker", broker_options, index=0)

st.divider()

# Condición para mostrar diferentes interfaces según el bróker seleccionado
if broker == "E*Trade Web Alerts":
    # La interfaz actual para E*Trade Web Alerts
    st.subheader("Upload your text file with Alerts")
    uploaded_file = st.file_uploader("Choose a file", type=['txt'])
    if uploaded_file is not None:
        results = main(uploaded_file)
        display_results_and_download_button(results, key="uploaded_file_results_text_area")

    st.markdown("---")
    st.subheader("Or paste your Alerts Text here")
    trade_data = st.text_area("Paste the alerts", height=300, key="trade_data_text_area")
    apply_button = st.button('Apply pasted data')
    if apply_button and trade_data:
        from io import StringIO
        trade_data_file = StringIO(trade_data)
        results = main(trade_data_file)
        display_results_and_download_button(results, key="pasted_data_results_text_area")

if broker == "Power E*Trade Web App":
    st.subheader("Upload your Power E*Trade CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    if uploaded_file is not None:
        results = process_power_etrade_csv(uploaded_file)
        display_results_and_download_button(results, key="power_etrade_results_text_area")



# Disclaimer
st.markdown("""
    #     
    ---
    *This tool is intended for educational purposes only and its results should not be considered as investment advice.*
""")