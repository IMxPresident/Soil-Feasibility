import streamlit as st
import subprocess

# Set page layout
st.set_page_config(page_title="Soil Feasibility Analysis Tool", layout="wide")

# Set the image URL (Replace with your actual image URL)
header_image_url = "https://media.licdn.com/dms/image/v2/D4D3DAQHSluopjv1i4Q/image-scale_191_1128/image-scale_191_1128/0/1698217912923/sgurrenergy_cover?e=1740729600&v=beta&t=NHf8MRAc8e5X0T6pOJp_KxuucwoWVtDzM9tFQlP83A4"  # Change this to your image URL

# Custom CSS for full-width header image
header_style = f"""
    <style>
    .header-container {{
        width: 100%;
        height: 200px;  /* Adjust height as needed */
        background: url("{header_image_url}") no-repeat center center;
        background-size: cover;
    }}
    </style>
"""
st.markdown(header_style, unsafe_allow_html=True)

# Header Image
st.markdown("<div class='header-container'></div>", unsafe_allow_html=True)

# Title (Positioned below the image)
st.markdown("<h1 style='text-align: center; margin-top: 20px;'>Soil Feasibility Analysis Tool</h1>", unsafe_allow_html=True)

# Description
st.markdown("""
<p style='text-align: center; font-size: 18px;'>
Select an application from the options below to launch it. Each serves a different purpose:
</p>
""", unsafe_allow_html=True)

# Define app names and script paths
apps = {
    "TIFF File Processor": "1.py",
    "Borehole KMZ Generator": "2.py",
    "KMZ to TIFF Data Extractor": "3.py",
    "Advanced Soil Data Processor": "4.py"
}

# Create columns for a centered layout
col1, col2 = st.columns(2)

# Style buttons with padding
button_style = """
    <style>
    div.stButton > button {
        width: 100%;
        height: 80px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        margin: 5px 0;
    }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

# Add buttons in a 2x2 grid format
with col1:
    if st.button("TIFF File Processor"):
        st.success("Launching TIFF File Processor...")
        subprocess.Popen(["streamlit", "run", apps["TIFF File Processor"]])

    if st.button("KMZ to TIFF Data Extractor"):
        st.success("Launching KMZ to TIFF Data Extractor...")
        subprocess.Popen(["streamlit", "run", apps["KMZ to TIFF Data Extractor"]])

with col2:
    if st.button("Borehole KMZ Generator"):
        st.success("Launching Borehole KMZ Generator...")
        subprocess.Popen(["streamlit", "run", apps["Borehole KMZ Generator"]])

    if st.button("Advanced Soil Data Processor"):
        st.success("Launching Advanced Soil Data Processor...")
        subprocess.Popen(["streamlit", "run", apps["Advanced Soil Data Processor"]])

# Footer
st.markdown("<hr style='margin-top: 30px;'>", unsafe_allow_html=True)
st.info("Once an application is launched, it will run in a new process.")
