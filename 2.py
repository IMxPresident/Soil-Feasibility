import streamlit as st
import pandas as pd
import io
import simplekml

# Function to generate a KMZ file
def generate_kmz(data, filename="output.kmz"):
    kml = simplekml.Kml()
    for _, row in data.iterrows():
        latitude = row["Latitude"]
        longitude = row["Longitude"]
        borehole_name = row.get("Borehole", f"Borehole {_+1}")
        kml.newpoint(name=borehole_name, coords=[(longitude, latitude)])
    kmz_data = io.BytesIO()
    kml.savekmz(kmz_data)
    kmz_data.seek(0)
    return kmz_data

# Streamlit Application
def main():
    st.title("Borehole KMZ Generator")
    st.write("Upload an Excel file containing `SR.NO`, `BOREHOLE`, `LATITUDE`, and `LONGITUDE` columns. The app will generate a KMZ file for visualization in Google Earth.")

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        try:
            # Load Excel file
            data = pd.read_excel(uploaded_file)

            # Check for necessary columns (case insensitive)
            required_columns = ['SR.NO', 'BOREHOLE', 'LATITUDE', 'LONGITUDE']
            if not all(col.lower() in data.columns.str.lower() for col in required_columns):
                st.error("The uploaded file must contain 'SR.NO', 'BOREHOLE', 'LATITUDE', and 'LONGITUDE' columns (case insensitive).")
                return

            # Generate and download KMZ file
            kmz_file = generate_kmz(data)
            st.download_button(
                label="Download KMZ File",
                data=kmz_file,
                file_name="boreholes.kmz",
                mime="application/vnd.google-earth.kmz",
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()