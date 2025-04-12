import streamlit as st
import base64

def display_header(title, logo_path):
    with open(logo_path, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
            .header-container {{
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }}
            .header-container img {{
                width: 60px;
                height: 60px;
                border-radius: 50%;
                margin-right: 15px;
            }}
            .header-container h1 {{
                font-size: 2.2rem;
                margin: 0;
            }}
        </style>
        <div class="header-container">
            <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo">
            <h1>{title}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
