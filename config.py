import streamlit as st

def apply_custom_css():
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; }
        label, p, .stText, .stMarkdown, .stSubheader, [data-testid="stWidgetLabel"] p { color: #e0e0e0 !important; }
        h1, h2, h3 { color: #ffffff !important; }
        button[data-baseweb="tab"] p { color: #b0b3b8 !important; }
        button[aria-selected="true"] p { color: #ffffff !important; font-weight: bold; }
        div[data-testid="stButton"] button {
            background-color: #ff4b4b !important; color: #ffffff !important;
            border: 1px solid #ff4b4b !important; border-radius: 4px !important;
        }
        div[data-testid="stButton"] button:hover { background-color: #ff3333 !important; border-color: #ff3333 !important; }
        
        .rodape-vini {
            position: fixed; 
            left: 0; 
            bottom: 0; 
            width: 100%; 
            background-color: transparent;
            color: #888888; 
            text-align: left;       
            padding-left: 20px; 
            padding-bottom: 10px; 
            font-size: 12px; 
            z-index: 9999;
        }
        </style>
        <div class="rodape-vini">by Vini Matos</div>
        """,
        unsafe_allow_html=True
    )
