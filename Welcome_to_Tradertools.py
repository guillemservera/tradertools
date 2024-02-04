
import streamlit as st

st.set_page_config(
    page_title="Tradertools · Simple & Useful Tools for Traders",
    page_icon="🛠️",
    layout="wide",
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

# Page content
st.markdown("""
    ## Welcome to TraderTools!

    ##
    
    Feel free to share feedback and ideas.

                   
    Developed by [Guillem Servera](https://twitter.com/guillemservera)
""")

# Disclaimer
st.markdown("""    
    ---
    *This tool is intended for educational purposes only and its results should not be considered as investment advice.*
""")