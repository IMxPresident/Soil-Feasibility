import io
import zipfile
import pandas as pd
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform
import streamlit as st
from xml.etree import ElementTree as ET


def extract_kml_from_kmz(kmz_buffer):
    """Extract KML file from KMZ or parse it directly if it's raw KML."""
    try:
        # Try to open the file as a ZIP (KMZ)
        with zipfile.ZipFile(io.BytesIO(kmz_buffer), 'r') as kmz:
            for file in kmz.namelist():
                if file.endswith('.kml'):  # Check for .kml files inside the archive
                    with kmz.open(file) as kml_file:
                        return io.BytesIO(kml_file.read())
    except zipfile.BadZipFile:
        # If not a valid ZIP file, check if it's raw KML
        if kmz_buffer.startswith(b"<?xml") or b"<kml" in kmz_buffer[:100].lower():
            return io.BytesIO(kmz_buffer)  # Treat buffer as raw KML
    except Exception as e:
        st.error(f"Unexpected error while extracting KML: {e}")
    
    return None


def parse_kml(kml_file):
    """Parse KML file to extract coordinates."""
    try:
        namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
        tree = ET.parse(kml_file)
        root = tree.getroot()

        coordinates = []
        for placemark in root.findall(".//kml:Placemark", namespace):
            coords = placemark.find(".//kml:coordinates", namespace)
            name = placemark.find("kml:name", namespace)
            if coords is not None:
                lon, lat, *_ = coords.text.strip().split(",")
                coordinates.append({
                    "Name": name.text if name is not None else "Unknown",
                    "Longitude": float(lon),
                    "Latitude": float(lat)
                })

        return pd.DataFrame(coordinates)
    except Exception as e:
        st.error(f"Error parsing KML: {e}")
        return pd.DataFrame()


def extract_tiff_data(tiff_buffer, coordinates_df):
    """Extract data from TIFF file based on coordinates."""
    try:
        with rasterio.open(io.BytesIO(tiff_buffer)) as src:
            band_names = src.descriptions  # Dynamically fetch band descriptions
            if not band_names:
                band_names = [f"Band_{i+1}" for i in range(src.count)]

            extracted_data = []
            progress = st.progress(0)  # Initialize progress bar
            for i, row in coordinates_df.iterrows():
                try:
                    lon, lat = row["Longitude"], row["Latitude"]

                    # Transform coordinates to TIFF CRS
                    lon_transformed, lat_transformed = transform(
                        CRS.from_epsg(4326), src.crs, [lon], [lat]
                    )

                    # Ensure the transformed arrays have values
                    if len(lon_transformed) > 0 and len(lat_transformed) > 0:
                        row_idx, col_idx = src.index(lon_transformed[0], lat_transformed[0])

                        # Read all band values at the location
                        values = src.read()[:, row_idx, col_idx]
                        extracted_data.append(values.tolist())  # Convert array to list for easier handling
                    else:
                        extracted_data.append([None] * src.count)  # Append None if transformation fails
                except Exception as e:
                    extracted_data.append([None] * src.count)  # Append None for failed lookups

                progress.progress((i + 1) / len(coordinates_df))  # Update progress bar

            progress.empty()  # Clear progress bar

        # Add extracted data to DataFrame
        for i, band_name in enumerate(band_names):
            coordinates_df[band_name] = [data[i] if data else None for data in extracted_data]

        return coordinates_df
    except Exception as e:
        st.error(f"Error extracting TIFF data: {e}")
        return pd.DataFrame()


# Streamlit UI
st.title("KMZ to TIFF Data Extractor")

# File upload for KMZ and TIFF files
kmz_file = st.file_uploader("Upload KMZ File", type=["kmz"])
tiff_file = st.file_uploader("Upload TIFF File", type=["tif"])

if st.button("Extract Data"):
    if kmz_file and tiff_file:
        try:
            # Extract KML from KMZ in memory
            kml_buffer = extract_kml_from_kmz(kmz_file.getvalue())
            if not kml_buffer:
                st.error("No KML file found in the KMZ.")
                st.stop()

            # Parse coordinates from KML
            coordinates_df = parse_kml(kml_buffer)
            if coordinates_df.empty:
                st.error("No valid coordinates found in the KML.")
                st.stop()

            # Extract data from TIFF
            extracted_data_df = extract_tiff_data(tiff_file.getvalue(), coordinates_df)
            if not extracted_data_df.empty:
                # Display the extracted data
                st.subheader("Extracted Data")
                st.dataframe(extracted_data_df)

                # Generate an Excel file in memory
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    extracted_data_df.to_excel(writer, index=False, sheet_name='Extracted Data')

                # Allow users to download the Excel file
                st.download_button(
                    label="Download Extracted Data as XLSX",
                    data=excel_buffer.getvalue(),
                    file_name="extracted_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("No data extracted from TIFF.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
    else:
        st.error("Please upload both KMZ and TIFF files.")

# To run the Streamlit app, use the command:
# python -m streamlit run 3.py