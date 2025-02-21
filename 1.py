import streamlit as st
import rasterio
import pandas as pd
import tempfile
import re
from simplekml import Kml

def check_tiff_files(file_paths):
    results = []
    crs_set = set()

    for i, file in enumerate(file_paths, start=1):
        try:
            with rasterio.open(file) as src:
                crs = src.crs
                epsg = crs.to_epsg() if crs else "Unknown"
                resolution = src.res
                results.append({
                    "Sr. No": i,
                    "File Name": file.name,
                    "CRS": str(crs),
                    "EPSG": epsg,
                    "Resolution": resolution
                })
                crs_set.add(str(crs))
        except Exception as e:
            st.error(f"Error processing file {file.name}: {e}")

    df = pd.DataFrame(results)
    return df, crs_set

def create_multiband_raster(file_paths, output_path):
    try:
        sources = [rasterio.open(f) for f in file_paths]

        with rasterio.open(
            output_path, 'w',
            driver='GTiff',
            height=sources[0].height,
            width=sources[0].width,
            count=len(sources),
            crs=sources[0].crs,
            transform=sources[0].transform,
            dtype=sources[0].dtypes[0]
        ) as dst:
            for idx, src in enumerate(sources):
                dst.write(src.read(1), idx + 1)
                band_name = file_paths[idx].name.replace('.tif', '')
                dst.set_band_description(idx + 1, band_name)

        for src in sources:
            src.close()

        return True, None
    except Exception as e:
        return False, str(e)

def dms_to_dd(dms_str):
    """Convert a DMS (Degrees, Minutes, Seconds) string to Decimal Degrees."""
    match = re.match(r"(\d+)°\s*(\d+)’\s*([\d.]+)”", dms_str)
    if not match:
        raise ValueError(f"Invalid DMS format: {dms_str}")
    degrees, minutes, seconds = map(float, match.groups())
    return degrees + (minutes / 60) + (seconds / 3600)

def generate_kmz_from_excel(excel_file, kmz_file):
    try:
        df = pd.read_excel(excel_file)

        # Check required columns
        required_columns = ["sr.no", "Test_location_2", "Northing", "Easting"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"Input file must contain columns: {required_columns}")
            return

        # Create KMZ file
        kml = Kml()
        for _, row in df.iterrows():
            kml.newpoint(
                name=str(row['Test_location_2']),
                coords=[(row['Northing'], row['Easting'])],  # Assuming Easting and Northing are in the correct order
                description=f"Sr.No: {row['sr.no']}"
            )
        kml.savekmz(kmz_file)

        st.success("KMZ file has been successfully created!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Streamlit application
st.title("TIFF File CRS Checker and Multi-band Raster Creator")

# Navigation
page = st.sidebar.selectbox("Select Page", ["Home", "Calculate Design Properties"])

if page == "Home":
    # File uploader for TIFF files
    uploaded_files = st.file_uploader("Select TIFF Files", type=["tif"], accept_multiple_files=True)

    if uploaded_files:
        # Check the TIFF files and get results
        df, crs_set = check_tiff_files(uploaded_files)

        if df is not None and not df.empty:
            st.subheader("TIFF File Metadata")
            st.dataframe(df)

            if len(crs_set) == 1:
                st.success("<<ALL THE FILES CARRY THE SAME CRS VALUES>>")
            else:
                differing_files = [r["File Name"] for r in df.to_dict(orient='records') if r["CRS"] != list(crs_set)[0]]
                st.warning(f"Files with differing CRS values: {', '.join(differing_files)}")

            # Option to create multi-band raster
            output_file = st.text_input("Enter output file name (with .tif extension):", "merged_output.tif")
            if st.button("Create Multi-band Raster"):
                if output_file:
                    # Create a temporary file to save the raster
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as temp_file:
                        temp_output_path = temp_file.name
                    success, error_message = create_multiband_raster(uploaded_files, temp_output_path)
                    if success:
                        # Provide a download link for the user
                        with open(temp_output_path, "rb") as f:
                            st.download_button("Download Multi-band Raster", f, file_name=output_file)
                    else:
                        st.error(f"Error creating multi-band raster: {error_message}")
                else:
                    st.error("Please provide a valid output file name.")

elif page == "Calculate Design Properties":
    st.subheader("Generate KMZ from Excel File")
    excel_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    
    if excel_file:
        kmz_file = st.text_input("Enter output KMZ file name (with .kmz extension):", "output.kmz")
        if st.button("Generate KMZ"):
            if kmz_file:
                generate_kmz_from_excel(excel_file, kmz_file)
            else:
                st.error("Please provide a valid KMZ file name.")

"python -m streamlit run 1.py"