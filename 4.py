import pandas as pd
import streamlit as st
from io import BytesIO

# Title and Description
st.title("Advanced Soil Data Processor")
st.markdown("""
This application processes soil data based on the given physical and chemical properties. 
It calculates derived properties like cohesion, friction angle, and relative density, 
and provides classifications for soil texture and cohesiveness.
""")

# Function to classify cohesiveness
def classify_cohesiveness(row):
    soil_type = row['Soil_Texture']
    coarse_fragments = row['Coarse_Fragments_Percentage'] 

    # Check if the soil is gravelly
    if coarse_fragments >= 15:
        return "Gravelly, Non-Cohesive"
    
    # If coarse fragments are less than 15%, check for cohesive soil types
    cohesive_soil_types = [
        "Clay", "Silty Clay", "Sandy Clay", 
        "Silty Clay Loam", "Clay Loam", 
        "Sandy Clay Loam", "Silt", "Silt Loam", "Loam"
    ]
    
    if soil_type in cohesive_soil_types:
        return "Non-Gravelly, Cohesive"
    else:
        return "Non-Gravelly, Non-Cohesive"

def assign_porosity(row):
    soil_texture = row['Soil_Texture']
    # Dictionary with porosity values (n_max, n_min) for each soil texture
    porosity_values = {
        "Clay": (0.45, 0.25),
        "Silty Clay": (0.48, 0.28),
        "Sandy Clay": (0.50, 0.30),
        "Silty Clay Loam": (0.50, 0.30),
        "Clay Loam": (0.52, 0.32),
        "Sandy Clay Loam": (0.53, 0.33),
        "Silt": (0.55, 0.35),
        "Silt Loam": (0.53, 0.33),
        "Loam": (0.52, 0.32),
        "Sandy Loam": (0.50, 0.30),
        "Loamy Sand": (0.47, 0.28),
        "Sand": (0.44, 0.26),
        "Gravelly Soil": (0.42, 0.24)
    }
    # Check if the soil texture is in the dictionary and return its values
    n_max, n_min = porosity_values.get(soil_texture, (None, None))  # Default to (None, None) if not found
    
    if n_max is not None and n_min is not None:
        e_max = n_max / (1 - n_max)
        e_min = n_min / (1 - n_min)
        return e_max, e_min
    else:
        return None, None  # Return (None, None) if not found
    

def process_soil_data(input_path, output_path):
    df = pd.read_excel(input_path)
    df['Bulk_Density'] = df['bulk_density'] / 100
    df["Clay_Content"] = df["clay_content"] / 10
    df["Sand"] = df["sand"] / 10
    df["Silt"] = df["silt"] / 10
    df['Coarse_Fragments_Percentage'] = df['coarse_fragments'] / 10
    df['Cation_Exchange_Capacity'] = df['cation_exchange_capacity'] / 10
    df["pH_Water"] = df['pH_water'] / 10
    df['Soil_Organic_Carbon'] = df['soil_organic_carbon'] / 100
    df['Organic_Carbon_Density'] = df['organic_carbon_density'] / 10000
    df['Organic_Carbon_Stock'] = df['organic_carbon_stock']
    total_volume_of_soil = 1000
    Gs_clay = 2.75
    Gs_Sand = 2.675
    Gs_silt = 2.70
    Gs_coarse_fragments = 2.70

    # Move the classify_soil_texture function here
    def classify_soil_texture(Sand, Silt, Clay_Content):
        if 85 <= Sand <= 100 and 0 <= Silt <= 15 and 0 <= Clay_Content <= 10:
            return "Sand"
        elif 70 <= Sand <= 90 and 0 <= Silt <= 30 and 0 <= Clay_Content <= 15:
            return "Loamy Sand"
        elif 43 <= Sand <= 85 and 0 <= Silt <= 50 and 0 <= Clay_Content <= 20:
            return "Sandy Loam"
        elif 23 <= Sand <= 52 and 28 <= Silt <= 50 and 7 <= Clay_Content <= 27:
            return "Loam"
        elif 0 <= Sand <= 50 and 50 <= Silt <= 88 and 0 <= Clay_Content <= 27:
            return "Silt Loam"
        elif 0 <= Sand <= 20 and 80 <= Silt <= 100 and 0 <= Clay_Content <= 12:
            return "Silt"
        elif 45 <= Sand <= 80 and 0 <= Silt <= 28 and 20 <= Clay_Content <= 35:
            return "Sandy Clay Loam"
        elif 20 <= Sand <= 45 and 15 <= Silt <= 53 and 27 <= Clay_Content <= 40:
            return "Clay Loam"
        elif 0 <= Sand <= 20 and 40 <= Silt <= 73 and 27 <= Clay_Content <= 40:
            return "Silty Clay Loam"
        elif 45 <= Sand <= 65 and 0 <= Silt <= 20 and 35 <= Clay_Content <= 55:
            return "Sandy Clay"
        elif 0 <= Sand <= 20 and 40 <= Silt <= 60 and 40 <= Clay_Content <= 60:
            return "Silty Clay"
        elif 0 <= Sand <= 45 and 0 <= Silt <= 40 and 40 <= Clay_Content <= 100:
            return "Clay"
        else:
            return "Unclassified"

    # Soil Texture Classification
    df['Soil_Texture'] = df.apply(lambda row: classify_soil_texture(row['Sand'], row['Silt'], row['Clay_Content']), axis=1)

    # MASS OF EACH COMPONENTS
    df['Total_Mass_Of_Soil'] = total_volume_of_soil * df["Bulk_Density"]
    df['Mass_of_Coarse_Fragments'] = df['coarse_fragments'] * Gs_coarse_fragments
    df['Mass_of_Fine_Fragments'] = df['Total_Mass_Of_Soil'] - df['Mass_of_Coarse_Fragments']
    
    # MASS OF EACH FINE FRAGMENTS
    df["Mass_of_Clay"] = (df['Mass_of_Fine_Fragments'] * df['Clay_Content'] / 100)
    df["Mass_of_Sand"] = (df['Mass_of_Fine_Fragments'] * df['Sand'] / 100)
    df["Mass_of_Silt"] = (df['Mass_of_Fine_Fragments'] * df['Silt'] / 100) 

    # PERCENTAGE MASS OF EACH COMPONENT IN SOIL
    df['%_of_Clay'] = ((df['Mass_of_Clay'] / df["Total_Mass_Of_Soil"]) * 100)
    df['%_of_Sand'] = ((df['Mass_of_Sand'] / df["Total_Mass_Of_Soil"]) * 100)
    df['%_of_Silt'] = ((df['Mass_of_Silt'] / df["Total_Mass_Of_Soil"]) * 100)
    df['%_of _Coarse_Fragments'] = ((df['Mass_of_Coarse_Fragments'] / df["Total_Mass_Of_Soil"]) * 100)
    
    # VOLUME FRACTION FOR EACH COMPONENT
    df['Volume_Fraction_Clay'] = df['Mass_of_Clay'] / Gs_clay
    df['Volume_Fraction_Sand'] = df['Mass_of_Sand'] / Gs_Sand
    df['Volume_Fraction_Silt'] = df['Mass_of_Silt'] / Gs_silt
    
    # FINE FRACTION PERCENTAGE
    df['Fine_Fraction_Volume(%)'] = 100 - df['Coarse_Fragments_Percentage']
    df['Sum_of_Fine_Fraction_Volume(%)'] = df['Volume_Fraction_Clay'] + df['Volume_Fraction_Sand'] + df['Volume_Fraction_Silt']
    
    # ADJUSTED FINE FRACTION %
    df['Adjusted_Clay_Content'] = (df['Fine_Fraction_Volume(%)'] * df['Volume_Fraction_Clay']) / df['Sum_of_Fine_Fraction_Volume(%)']
    df['Adjusted_Sand'] = (df['Fine_Fraction_Volume(%)'] * df['Volume_Fraction_Sand']) / df['Sum_of_Fine_Fraction_Volume(%)']
    df['Adjusted_Silt'] = (df['Fine_Fraction_Volume(%)'] * df['Volume_Fraction_Silt']) / df['Sum_of_Fine_Fraction_Volume(%)']
    
    # TOTAL VOLUME OF SOLIDS
    df['Volume_of_Solids'] = df['Sum_of_Fine_Fraction_Volume(%)'] + df['coarse_fragments']
    
    # TOTAL VOLUME OF VOIDS 
    df['Volume_of_Voids'] = total_volume_of_soil - df['Volume_of_Solids']
    
    # VOID RATIO
    df['Void_Ratio'] = df['Volume_of_Voids'] / df['Volume_of_Solids']
    
    # Apply porosity values to the dataframe
    df[['e_max', 'e_min']] = df.apply(lambda row: pd.Series(assign_porosity(row)), axis=1)


    # Calculate Relative Density
    df['Relative_Density'] = ((df['e_max'] - df['Void_Ratio']) / (df['e_max'] - df['e_min'])) * 100
   
    # ATTERBERG LIMITS
    df['Liquid_Limit'] = 0.5 * df['Clay_Content'] + 20
    df['Plastic_Limit'] = 0.25 * df['Clay_Content'] + 10
    df['Plasticity_Index'] = df['Liquid_Limit'] - df['Plastic_Limit']
    
    # USCS SOIL CLASSIFICATION
    def classify_uscs(row):
        fine_content = row["Clay_Content"] + row["Silt"]
        coarse_content = row["Sand"]
        LL = row["Liquid_Limit"]
        PI = row["Plasticity_Index"]
        
        # Ensure that 'Gravel' and 'Uniformity_Coefficient' are defined in your DataFrame
        gravel_content = row.get("Gravel", 0)  # Default to 0 if not present
        uniformity_coefficient = row.get("Uniformity_Coefficient", 0)  # Default to 0 if not present

        if fine_content > 50:
            if LL < 50:
                return "ML (Silt)" if PI < 4 else "CL (Lean Clay)"
            else:
                return "MH (Elastic Silt)" if PI < 4 else "CH (Fat Clay)"
        elif coarse_content > 50:
            if gravel_content > 50:
                return "GW (Well-Graded Gravel)" if uniformity_coefficient > 4 else "GP (Poorly-Graded Gravel)"
            else:
                return "SW (Well-Graded Sand)" if uniformity_coefficient > 4 else "SP (Poorly-Graded Sand)"
        elif fine_content > 12:
            return "SM (Silty Sand)" if row["Sand"] > 50 else "SC (Clayey Sand)"
        else:
            return "Coarse-Grained (Unclassified)"

    # Apply the USCS classification to the DataFrame
    df['USCS_classification'] = df.apply(classify_uscs, axis=1)

    # HYDRAULIC CONDUCTIVITY
    def calculate_hydraulic_conductivity(soil_type):
        hydraulic_values = {
            "Gravel": 1.5015e-1,
            "Coarse Sand": 3.0045e-4,
            "Medium Sand": 2.5045e-4,
            "Fine Sand": 5.01e-5,
            "Sandy Loam": 2.75e-3,
            "Loam": 1.95e-4,
            "Sandy Clay Loam": 2.05e-4,
            "Silty Clay": 5.3e-5,
            "Clay": 2.5008e-6,
            "Sand": 4.0e-4,  # Add any other soil types you expect
            "Silty Clay Loam": 1.0e-5,  # Example value
            "Clay Loam": 1.0e-5  # Example value
        }
        return hydraulic_values.get(soil_type, "Invalid soil type")

    df['Hydraulic_Conductivity'] = df['Soil_Texture'].apply(calculate_hydraulic_conductivity)

    # COHESION
    def calculate_cohesion(row):
        soil_type = row["Soil_Texture"]
        LL = row["Liquid_Limit"]
        PI = row["Plasticity_Index"]
        
        if soil_type in ["Clay", "Silty Clay", "Sandy Clay", "Silty Clay Loam", "Clay Loam", "Silt", "Silt Loam"]:
            # Cohesive Soils
            return (20 * PI) + (0.25 * LL)
        elif soil_type in ["Sand", "Loamy Sand"]:
            # Non-Cohesive Soils
            return 0.1 * LL
        elif soil_type in ["Sandy Clay Loam", "Loam"]:
            # Partially Cohesive Soils
            return (0.2 * PI) + (0.15 * LL)
        elif soil_type == "Sandy Loam":
            # Special Case
            return (0.2 * LL) + (15 * PI)
        else:
            return 0  # Return 0 for unclassified or unknown soil type

    df['Cohesion'] = df.apply(calculate_cohesion, axis=1)

    # ANGLE OF FRICTION
    def calculate_angle_of_friction(row):
        soil_type = row["Soil_Texture"]
        LL = row["Liquid_Limit"]
        PI = row["Plasticity_Index"]
        DR = row.get("Relative_Density", 0)  # Use 0 if Relative Density is not available

        if soil_type in ["Clay", "Silty Clay", "Sandy Clay", "Silty Clay Loam", "Clay Loam", "Silt", "Silt Loam"]:
            # Cohesive Soils
            return 15 + (0.1 * (LL - PI))
        elif soil_type in ["Sand", "Loamy Sand"]:
            # Non-Cohesive Soils
            return 30 + (0.2 * DR)
        elif soil_type in ["Sandy Clay Loam", "Loam"]:
            # Partially Cohesive Soils
            return 20 + (0.15 * (LL - PI))
        elif soil_type == "Sandy Loam":
            # Special Case
            return 25 + (0.1 * (LL - 2 * PI))
        else:
            return None  # Return None for unclassified or unknown soil types

    df['Angle_of_Friction'] = df.apply(calculate_angle_of_friction, axis=1)
    
    # N-VALUES (SPT VALUES)
    def calculate_n_values(row):
        soil_type = row["Soil_Texture"]
        LL = row["Liquid_Limit"]
        PI = row["Plasticity_Index"]
        Coh = row["Cohesion"]
        RD = row["Relative_Density"]
        
        if soil_type in ["Clay", "Silty Clay", "Sandy Clay", "Silty Clay Loam", "Clay Loam", "Silt", "Silt Loam"]:
            # Cohesive Soils
            return (2.5 * (Coh / 10))
        elif soil_type in ["Sand", "Loamy Sand"]:
            # Non-Cohesive Soils
            return (5 + (RD / 10))
        elif soil_type in ["Sandy Clay Loam", "Loam"]:
            # Partially Cohesive Soils
            return (3 + (Coh / 10) + (RD / 15))
        elif soil_type == "Sandy Loam":
            # Special Case
            return (4 + (Coh / 12) + (RD / 20))
        else:
            return 0  # Return 0 for unclassified or unknown soil type

    df['SPT_VALUES'] = df.apply(calculate_n_values, axis=1)

    # Classify cohesiveness based on updated logic
    df['Cohesiveness'] = df.apply(classify_cohesiveness, axis=1)

    # Save the processed data to an Excel file
    df.to_excel(output_path, index=False)  # Ensure the output is saved in .xlsx format
    return df

# File upload
uploaded_file = st.file_uploader("Upload an Excel file with soil data", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # Process the uploaded file
        processed_data = process_soil_data(uploaded_file, "processed_soil_data.xlsx")
        
        # Display the processed data
        st.write("Processed Data:")
        st.dataframe(processed_data)
        
        # Download button for processed data
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            processed_data.to_excel(writer, index=False, sheet_name="Processed Data")
            output.seek(0)
        
        st.download_button(
            label="Download Processed Data",
            data=output,
            file_name="processed_soil_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("Please upload an Excel file to begin.")

"python -m streamlit run 4.py"