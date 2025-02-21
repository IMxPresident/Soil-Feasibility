import streamlit as st
import subprocess

# Title
st.title("Streamlit Web Application Launcher")

# Description
st.markdown("""
Select an application from the list below to launch it. Each application serves a different purpose:
- **TIFF File Processor**: Checks CRS, merges TIFFs, and generates KMZ files.
- **Borehole KMZ Generator**: Converts borehole data into KMZ format.
- **KMZ to TIFF Data Extractor**: Extracts soil property data from TIFF based on KMZ coordinates.
- **Advanced Soil Data Processor**: Processes soil data and computes key geotechnical properties.
""")

# Mapping applications to their respective scripts
apps = {
    "TIFF File Processor": "1.py",
    "Borehole KMZ Generator": "2.py",
    "KMZ to TIFF Data Extractor": "3.py",
    "Advanced Soil Data Processor": "4.py"
}

# Dropdown to select an application
selected_app = st.selectbox("Select an application:", list(apps.keys()))

# Button to launch the selected application
if st.button("Launch Application"):
    script_path = apps[selected_app]
    st.success(f"Launching {selected_app}...")
    
    # Run the selected Streamlit script as a subprocess
    subprocess.Popen(["streamlit", "run", script_path])

st.markdown("---")
st.info("Once an application is launched, it will run in a new process.")
