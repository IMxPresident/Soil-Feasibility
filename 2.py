import streamlit as st
import pandas as pd
import math
import io
import simplekml

# Constants
C12 = 6378137  # Semi-major axis of the ellipsoid (meters)
C13 = 6356752.314  # Semi-minor axis of the ellipsoid (meters)
C17 = 0.006739497  # Eccentricity squared of the ellipsoid
C18 = (C12**2) / C13  # Derived constant for calculations

# Function to convert UTM to Decimal Degrees
def utm_to_decimal_degrees(easting, northing, zone, hemisphere="N"):
    # Calculate N5 (central meridian of the zone)
    N5 = 6 * zone - 183

    if hemisphere == "S":  # Adjust for Southern Hemisphere
        O5 = northing - 10000000
    else:
        O5 = northing

    K5 = O5 / (6366197.724 * 0.9996)  # Calculate K5
    L5 = (C18 / (1 + C17 * (math.cos(K5))**2)**0.5) * 0.9996  # Calculate L5
    P5 = (easting - 500000) / L5  # Calculate P5

    # Latitude (AG5)
    Q5 = math.sin(2 * K5)
    R5 = Q5 * (math.cos(K5))**2
    S5 = K5 + (Q5 / 2)
    T5 = (3 * S5 + R5) / 4
    V5 = (3 / 4) * C17
    W5 = (5 / 3) * (V5**2)
    X5 = (35 / 27) * (V5**3)
    U5 = (5 * T5 + R5 * (math.cos(K5))**2) / 3
    Y5 = 0.9996 * C18 * (K5 - (V5 * S5) + (W5 * T5) - (X5 * U5))
    Z5 = (O5 - Y5) / L5
    AA5 = ((C17 * P5**2) / 2) * (math.cos(K5))**2
    AB5 = P5 * (1 - (AA5 / 3))
    AD5 = (math.exp(AB5) - math.exp(-AB5)) / 2
    AC5 = Z5 * (1 - AA5) + K5
    AE5 = math.atan(AD5 / math.cos(AC5))
    AF5 = math.atan(math.cos(AE5) * math.tan(AC5))
    M5 = K5 + (1 + C17 * (math.cos(K5))**2 - (3 / 2) * C17 * math.sin(K5) * math.cos(K5) * (AF5 - K5)) * (AF5 - K5)
    latitude = (M5 / math.pi) * 180

    # Longitude (AH5)
    longitude = (AE5 / math.pi) * 180 + N5

    return latitude, longitude


# Function to generate a KMZ file
def generate_kmz(data, filename="output.kmz"):
    kml = simplekml.Kml()
    for _, row in data.iterrows():
        latitude = row["Latitude"]
        longitude = row["Longitude"]
        name = row.get("Name", f"Point {_+1}")
        kml.newpoint(name=name, coords=[(longitude, latitude)])
    kmz_data = io.BytesIO()
    kml.savekmz(kmz_data)
    kmz_data.seek(0)
    return kmz_data


# Streamlit Application
def main():
    st.title("UTM to Decimal Degrees Converter with KMZ Generation")
    st.write("Upload an Excel file containing `Northing` and `Easting` columns, and the app will calculate Latitude and Longitude in Decimal Degrees. It will also generate a KMZ file for visualization in Google Earth.")

    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file is not None:
        try:
            # Load Excel file
            data = pd.read_excel(uploaded_file)

            # Check for necessary columns
            if "Northing" not in data.columns or "Easting" not in data.columns:
                st.error("The uploaded file must contain 'Northing' and 'Easting' columns.")
                return

            # Add a sidebar for additional parameters
            st.sidebar.title("Settings")
            zone = st.sidebar.number_input("Enter UTM Zone", min_value=1, max_value=60, value=33)
            hemisphere = st.sidebar.selectbox("Select Hemisphere", ["N", "S"])

            # Process data
            latitude_list = []
            longitude_list = []
            for _, row in data.iterrows():
                northing = row["Northing"]
                easting = row["Easting"]
                latitude, longitude = utm_to_decimal_degrees(easting, northing, zone, hemisphere)
                latitude_list.append(latitude)
                longitude_list.append(longitude)

            # Add results to the DataFrame
            data["Latitude"] = latitude_list
            data["Longitude"] = longitude_list

            # Display the processed data
            st.write("Processed Data:")
            st.dataframe(data)

            # Provide download link for the results as Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                data.to_excel(writer, index=False)
            processed_file = output.getvalue()

            st.download_button(
                label="Download Results as Excel",
                data=processed_file,
                file_name="converted_coordinates.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

            # Generate and download KMZ file
            kmz_file = generate_kmz(data)
            st.download_button(
                label="Download KMZ File",
                data=kmz_file,
                file_name="converted_coordinates.kmz",
                mime="application/vnd.google-earth.kmz",
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
