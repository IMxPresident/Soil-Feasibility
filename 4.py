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

# Function to classify cohesiveness based on the new criteria
def classify_cohesiveness(row):
    coarse_fragments_percentage = row['Coarse_Fragments_Percentage']
    soil_type = row['Soil_Texture']

    # Check if the soil is gravelly
    if coarse_fragments_percentage > 15:
        return "Gravelly, Non-Cohesive"
    
    # If not gravelly, classify based on soil type
    cohesive_soil_types = [
        "Clay", "Silty Clay", "Sandy Clay", 
        "Silty Clay Loam", "Clay Loam", 
        "Sandy Clay Loam", "Silt", "Silt Loam", "Loam"
    ]
    
    non_cohesive_soil_types = [
        "Sandy Loam", "Loamy Sand", "Sand"
    ]

    if soil_type in cohesive_soil_types:
        return "Non-Gravelly, Cohesive"
    elif soil_type in non_cohesive_soil_types:
        return "Non-Gravelly, Non-Cohesive"
    else:
        return "Unclassified"

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

def assign_pdmin_pdmax(row):
    soil_texture = row['Soil_Texture']
    pd_values = {
        "Sand": (1.30, 1.80),
        "Loamy Sand": (1.25, 1.75),
        "Sandy Loam": (1.20, 1.70),
        "Loam": (1.10, 1.65),
        "Silt Loam": (1.05, 1.60),
        "Silt": (1.00, 1.55),
        "Clay Loam": (0.95, 1.50),
        "Silty Clay Loam": (0.90, 1.45),
        "Sandy Clay Loam": (0.85, 1.40),
        "Clay": (0.80, 1.35),
        "Silty Clay": (0.75, 1.30),
        "Sandy Clay": (0.70, 1.25),
        "Gravelly Soil": (1.40, 2.00)
    }
    return pd_values.get(soil_texture, (None, None))  # Default to (None, None) if not found

# Function to calculate Liquid Limit (LL)
def calculate_liquid_limit (row):
    soil_type = row['Soil_Texture']
    clay_content = row['Clay_Content']
    silt_content = row['Silt']
    sand_content = row['Sand']
    coarse_fragment_content = row['Coarse_Fragments_Percentage']
    soil_organic_carbon = row['Soil_Organic_Carbon']
    moisture_content_33kPa = row['Vol_Water_Content_33kPa']

    # Coefficients for Liquid Limit based on soil type
    ll_coefficients = {
        "Clay": (50, 1.10, 0.50, -0.20, -0.15, 0.50, 0.25),
        "Silty Clay": (48, 1.00, 0.55, -0.18, -0.12, 0.45, 0.22),
        "Sandy Clay": (46, 0.95, 0.45, -0.15, -0.10, 0.40, 0.20),
        "Clay Loam": (42, 0.85, 0.50, -0.22, -0.08, 0.38, 0.18),
        "Silty Clay Loam": (40, 0.75, 0.55, -0.20, -0.07, 0.36, 0.16),
        "Sandy Clay Loam": (38, 0.70, 0.45, -0.18, -0.06, 0.34, 0.15),
        "Loam": (36, 0.55, 0.50, -0.25, -0.05, 0.30, 0.12),
        "Silty Loam": (34, 0.50, 0.55, -0.28, -0.04, 0.28, 0.10),
        "Sandy Loam": (30, 0.40, 0.45, -0.30, -0.03, 0.25, 0.08),
        "Silt": (28, 0.30, 0.65, -0.32, -0.02, 0.22, 0.07),
        "Sand": (26, 0.15, 0.35, -0.35, -0.01, 0.18, 0.08),
        "Loamy Sand": (24, 0.10, 0.30, -0.40, 0.00, 0.15, 0.06),
        "Gravelly Soil": (22, 0.60, 0.40, -0.30, -0.25, 0.30, 0.10)
    }

    if soil_type in ll_coefficients:
        b, ac, as_, asa, acf, asoc, am = ll_coefficients[soil_type]
        LL = (b + (ac * clay_content) + (as_ * silt_content) +
               (asa * sand_content) + (acf * coarse_fragment_content) +
               (asoc * soil_organic_carbon) + (am * moisture_content_33kPa))
        return LL
    else:
        return None  # Return None if soil type is not found

# Function to calculate Plastic Limit (PL)
def calculate_plastic_limit(row):
    soil_type = row['Soil_Texture']
    clay_content = row['Clay_Content']
    silt_content = row['Silt']
    sand_content = row['Sand']
    coarse_fragment_content = row['Coarse_Fragments_Percentage']
    soil_organic_carbon = row['Soil_Organic_Carbon']
    moisture_content_33kPa = row.get('Vol_Water_Content_33kPa', 0)  # Default to 0 if not present

    # Coefficients for Plastic Limit based on soil type
    pl_coefficients = {
        "Clay": (24, 0.70, 0.30, -0.15, -0.10, 0.40, 0.18),
        "Silty Clay": (23, 0.65, 0.35, -0.12, -0.08, 0.35, 0.16),
        "Sandy Clay": (22, 0.60, 0.25, -0.10, -0.07, 0.30, 0.15),
        "Clay Loam": (21, 0.50, 0.35, -0.18, -0.06, 0.28, 0.14),
 "Silty Clay Loam": (20, 0.45, 0.40, -0.16, -0.05, 0.26, 0.13),
        "Sandy Clay Loam": (19, 0.40, 0.30, -0.14, -0.04, 0.24, 0.12),
        "Loam": (18, 0.30, 0.35, -0.20, -0.03, 0.22, 0.10),
        "Silty Loam": (17, 0.25, 0.40, -0.22, -0.02, 0.20, 0.08),
        "Sandy Loam": (16, 0.20, 0.30, -0.25, -0.02, 0.18, 0.06),
        "Silt": (15, 0.10, 0.50, -0.28, -0.01, 0.15, 0.05),
        "Sand": (14, 0.05, 0.25, -0.30, -0.01, 0.12, 0.06),
        "Loamy Sand": (13, 0.02, 0.20, -0.35, 0.00, 0.10, 0.04),
        "Gravelly Soil": (12, 0.40, 0.30, -0.25, -0.20, 0.20, 0.09)
    }

    if soil_type in pl_coefficients:
        b_prime, pc, ps, psa, pcf, psoc, pm = pl_coefficients[soil_type]
        PL = (b_prime + (pc * clay_content) + (ps * silt_content) +
              (psa * sand_content) + (pcf * coarse_fragment_content) +
              (psoc * soil_organic_carbon) + (pm * moisture_content_33kPa))
        return PL
    else:
        return None  # Return None if soil type is not found

# Function to calculate cohesion (c')
def calculate_cohesion_adjusted(row):
    dry_density = row['pd']
    pdmin = row['pdmin']
    pdmax = row['pdmax']
    soil_type = row['Soil_Texture']
    soil_organic_carbon = row['Soil_Organic_Carbon'] * 100  # Convert to percentage

    # Determine delta_c based on SOC
    if 0 <= soil_organic_carbon <= 1:
        delta_c = 1.00
    elif 1 < soil_organic_carbon <= 2:
        delta_c = 0.965
    elif 2 < soil_organic_carbon <= 4:
        delta_c = 0.925
    elif 4 < soil_organic_carbon <= 8:
        delta_c = 0.85
    elif 8 < soil_organic_carbon <= 12:
        delta_c = 0.725
    elif soil_organic_carbon > 12:
        delta_c = 0.575
    else:
        delta_c = 1.00  # Default value if SOC is negative or not defined

    # Cohesion values based on soil type
    cohesion_values = {
        "Clay": (50, 100),
        "Silty Clay": (40, 80),
        "Sandy Clay": (35, 70),
        "Clay Loam": (25, 50),
        "Silty Clay Loam": (30, 60),
        "Sandy Clay Loam": (20, 40),
        "Loam": (10, 25),
        "Silty Loam": (12, 30),
        "Sandy Loam": (5, 15),
        "Silt": (15, 35),
        "Sand": (0, 10),
        "Loamy Sand": (5, 15),
        "Gravelly Soil": (0, 5)
    }

    if soil_type in cohesion_values:
        cmin, cmax = cohesion_values[soil_type]
        if pdmax != pdmin:  # Prevent division by zero
            cohesion_initial = cmin + (((dry_density - pdmin) / (pdmax - pdmin)) * (cmax - cmin)) - (soil_organic_carbon * delta_c)
            return cohesion_initial
        else:
            return None  # Return None if pdmax equals pdmin
    else:
        return None  # Return None if soil type is not found

# Function to adjust cohesion based on Atterberg limits and coarse fragments
 def adjust_cohesion(row):
    cohesion_initial = row['Cohesion']
    soil_type = row['Soil_Texture']
    plasticity_index = row['Plasticity_Index']
    coarse_fragments_percentage = row['Coarse_Fragments_Percentage']

    # αPI values based on soil type
    alpha_pi_values = {
        "Clay": 0.0075,
        "Silty Clay": 0.006,
        "Sandy Clay": 0.005,
        "Clay Loam": 0.0045,
        "Silty Clay Loam": 0.004,
        "Sandy Clay Loam": 0.0035,
        "Loam": 0.00275,
        "Silty Loam": 0.002,
        "Sandy Loam": 0.00165,
        "Silt": 0.00125,
        "Sand": 0,
        "Loamy Sand": 0,
        "Gravelly Soil": 0
    }

    # βcf values based on coarse fragments percentage
    if 0 <= coarse_fragments_percentage <= 10:
        beta_cf = 1.00
    elif 10 < coarse_fragments_percentage <= 20:
        beta_cf = 0.965
    elif 20 < coarse_fragments_percentage <= 30:
        beta_cf = 0.925
    elif 30 < coarse_fragments_percentage <= 40:
        beta_cf = 0.875
    elif 40 < coarse_fragments_percentage <= 50:
        beta_cf = 0.80
    elif 50 < coarse_fragments_percentage <= 60:
        beta_cf = 0.70
    elif 60 < coarse_fragments_percentage <= 70:
        beta_cf = 0.575
    else:
        beta_cf = 0.40

    if soil_type in alpha_pi_values:
        alpha_pi = alpha_pi_values[soil_type]
        adjusted_cohesion = cohesion_initial * (1 + alpha_pi * plasticity_index) * (1 - beta_cf * coarse_fragments_percentage / 100)
        return adjusted_cohesion
    else:
        return None  # Return None if soil type is not found

def assign_friction_angle_bounds_and_calculate_n(soil_texture, bulk_density, soc):
    # Friction angle bounds based on soil texture
    friction_angle_bounds = {
        "Sand": (30, 35),
        "Loamy Sand": (28, 33),
        "Sandy Loam": (28, 32),
        "Loam": (25, 30),
        "Silt Loam": (22, 27),
        "Silt": (18, 24),
        "Sandy Clay Loam": (27, 32),
        "Clay Loam": (22, 27),
        "Silty Clay Loam": (20, 26),
        "Sandy Clay": (25, 30),
        "Silty Clay": (18, 23),
        "Clay": (15, 20),
        "Gravelly Soil": (32, 38)
    }

    # Particle density bounds based on soil texture
    particle_density_bounds = {
        "Sand": (2.65, 2.75),
        "Loamy Sand": (2.65, 2.70),
        "Sandy Loam": (2.65, 2.70),
        "Loam": (2.65, 2.65),
        "Silt Loam": (2.65, 2.68),
        "Silt": (2.65, 2.68),
        "Clay Loam": (2.65, 2.72),
        "Silty Clay Loam": (2.65, 2.75),
        "Sandy Clay Loam": (2.65, 2.75),
        "Clay": (2.65, 2.78),
        "Silty Clay": (2.65, 2.75),
        "Sandy Clay": (2.65, 2.75),
        "Gravelly Soil": (2.70, 2.80)
    }

    # Friction angle values based on soil texture
    friction_angle_values = {
        "Sand": (30, 35),
        "Loamy Sand": (28, 33),
        "Sandy Loam": (28, 32),
        "Loam": (25, 30),
        "Silt Loam": (22, 27),
        "Silt": (18, 24),
        "Sandy Clay Loam": (27, 32),
        "Clay Loam": (22, 27),
        "Silty Clay Loam": (20, 26),
        "SandyClay": (25, 30),
        "Silty Clay": (18, 23),
        "Clay": (15, 20),
        "Gravelly Soil": (32, 38)
    }

    # Delta phi values based on soil texture and SOC
    delta_phi_values = {
        "Sand": (0, 0.1, 0.2, 0.3),
        "Loamy Sand": (0, 0.2, 0.4, 0.6),
        "Sandy Loam": (0, 0.3, 0.6, 0.9),
        "Loam": (0, 0.4, 0.8, 1.2),
        "Silt Loam": (0, 0.5, 1.0, 1.5),
        "Silt": (0, 0.5, 1.0, 1.5),
        "Sandy Clay Loam": (0, 0.4, 0.8, 1.2),
        "Clay Loam": (0, 0.5, 1.0, 1.5),
        "Silty Clay Loam": (0, 0.5, 1.0, 1.5),
        "Sandy Clay": (0, 0.3, 0.6, 0.9),
        "Silty Clay": (0, 0.5, 1.0, 1.5),
        "Clay": (0, 0.6, 1.2, 1.8),
        "Gravelly Soil": (0, 0.2, 0.4, 0.6)
    }

    # Get friction angle bounds
    friction_bounds = friction_angle_bounds.get(soil_texture, (None, None))
    # Get particle density bounds
    particle_density = particle_density_bounds.get(soil_texture, (None, None))

    if particle_density[0] is not None and particle_density[1] is not None:
        pp_min, pp_max = particle_density
        # Calculate n_min and n_max
        n_min = (1 - bulk_density / pp_min) * 100
        n_max = (1 - bulk_density / pp_max) * 100
    else:
        pp_min, pp_max, n_min, n_max = None, None, None, None

    # Assign phi_min and phi_max based on soil class
    phi_min, phi_max = friction_angle_values.get(soil_texture, (None, None))

    # Assign Δϕ based on SOC
    delta_phi = None
    if soil_texture in delta_phi_values:
        if soc < 1:
            delta_phi = delta_phi_values[soil_texture][0]
        elif 1 <= soc <= 5:
            delta_phi = delta_phi_values[soil_texture][1]
        elif 5 < soc <= 10:
            delta_phi = delta_phi_values[soil_texture][2]
        else:  # SOC > 10
            delta_phi = delta_phi_values[soil_texture][3]

    # Calculate ρb_min and ρb_max
    if n_min is not None and n_max is not None and pp_min is not None and pp_max is not None:
        rho_b_min = (1 - n_max / 100) * pp_max
        rho_b_max = (1 - n_min / 100) * pp_min
    else:
        rho_b_min, rho_b_max = None, None

    # Calculate the angle of friction φ
    phi = None
    if rho_b_min is not None and rho_b_max is not None:
        phi = phi_min + (((bulk_density - rho_b_min) / (rho_b_max - rho_b_min)) * (phi_max - phi_min)) - (soc * delta_phi)

    return (friction_bounds, pp_min, pp_max, n_min, n_max, phi_min, phi_max, delta_phi, rho_b_min, rho_b_max, phi)

def calculate_n_value(soil_texture, bulk_density):
    # Initialize n_value
    n_value = None

    # N-value formulas based on soil texture
    if soil_texture == "Sand":
        n_value = 12.5 * (bulk_density / 10000000000)
    elif soil_texture == "Loamy Sand":
        n_value = 10.8 * (bulk_density / 100000000)
    elif soil_texture == "Sandy Loam":
        n_value = 9.6 * (bulk_density / 1000000)
    elif soil_texture == "Loam":
        n_value = 8.5 * (bulk_density / 100000)
    elif soil_texture == "Silt Loam":
        n_value = 7.2 * (bulk_density / 10000)
    elif soil_texture == "Silt":
        n_value = 6.8 * (bulk_density / 1000)
    elif soil_texture == "Clay Loam":
        n_value = 5.5 * (bulk_density / 100)
    elif soil_texture == "Silty Clay Loam":
        n_value = 4.8 * (bulk_density / 10)
    elif soil_texture == "Sandy Clay Loam":
        n_value = 4.0 * (bulk_density / 10)
    elif soil_texture == "Clay":
        n_value = 3.5 * (bulk_density / 10)
    elif soil_texture == "Silty Clay":
        n_value = 3.2 * (bulk_density / 10)
    elif soil_texture == "Sandy Clay":
        n_value = 2.8 * (bulk_density / 10)
    elif soil_texture == "Gravelly Soil":
        n_value = 15 * (bulk_density / 1000000000000)

    return n_value  # Return the calculated N-value or None if not found

def process_soil_data(input_path, output_path):
    df = pd.read_excel(input_path)
    df['Bulk_Density'] = df['bulk_density'] / 100
    df['Cation_Exchange_Capacity'] = df['cation_exchange_capacity'] / 10
    df["Clay_Content"] = df["clay_content"] / 10
    df['Coarse_Fragments_Percentage'] = df['coarse_fragments'] / 10
    df['Nitrogen'] = df["nitrogen"]
    df['Organic_Carbon_Density'] = df['organic_carbon_density'] / 10000
    df["pH_Water"] = df['pH_water'] / 10
    df["Sand"] = df["sand"] / 10
    df["Silt"] = df["silt"] / 10
    df['Organic_Carbon_Stock'] = df['organic_carbon_stock']
    df['Soil_Organic_Carbon'] = df['soil_organic_carbon'] / 100
    df['Vol_Water_Content_10kPa'] = df['vol_water_content_10kPa']/10
    df['Vol_Water_Content_33kPa'] = df['vol_water_content_33kPa']/10
    df['Vol_Water_Content_1500kPa'] = df['vol_water_content_1500kPa']/10
    
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
        elif 23 <= Sand <= 52 and 28 <= Silt <= 50 and 7 <= Clay_Content <= 28:
            return "Loam"
        elif 0 <= Sand <= 50 and 50 <= Silt <= 86 and 0 <= Clay_Content <= 28:
            return "Silt Loam"
        elif 0 <= Sand <= 20 and 80 <= Silt <= 100 and 0 <= Clay_Content <= 12:
            return "Silt"
        elif 45 <= Sand <= 80 and 0 <= Silt <= 28 and 20 <= Clay_Content <= 35:
            return "Sandy Clay Loam"
        elif 20 <= Sand <= 45 and 15 <= Silt <= 52 and 28 <= Clay_Content <= 40:
            return "Clay Loam"
        elif 0 <= Sand <= 20 and 40 <= Silt <= 72 and 28 <= Clay_Content <= 40:
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
    df['%_of_Clay'] = ((df['Mass_of_Clay'] / df["Total_Mass_Of_Soil"]) * 100) if df["Total_Mass_Of_Soil"] != 0 else 0
    df['%_of_Sand'] = ((df['Mass_of_Sand'] / df["Total_Mass_Of_Soil"]) * 100) if df["Total_Mass_Of_Soil"] != 0 else 0
    df['%_of_Silt'] = ((df['Mass_of_Silt'] / df["Total_Mass_Of_Soil"]) * 100) if df["Total_Mass_Of_Soil"] != 0 else 0
    df['%_of_Coarse_Fragments'] = ((df['Mass_of_Coarse_Fragments'] / df["Total_Mass_Of_Soil"]) * 100) if df["Total_Mass_Of_Soil"] != 0 else 0
    
    # VOLUME FRACTION FOR EACH COMPONENT
    # Check for zero before division
    df['Volume_Fraction_Clay'] = df['Mass_of_Clay'] / Gs_clay if Gs_clay != 0 else 0
    df['Volume_Fraction_Sand'] = df['Mass_of_Sand'] / Gs_Sand if Gs_Sand != 0 else 0
    df['Volume_Fraction_Silt'] = df['Mass_of_Silt'] / Gs_silt if Gs_silt != 0 else 0

    # FINE FRACTION PERCENTAGE
    df['Fine_Fraction_Volume(%)'] = 100 - df['Coarse_Fragments_Percentage']
    df['Sum_of_Fine_Fraction_Volume(%)'] = df['Volume_Fraction_Clay'] + df['Volume_Fraction_Sand'] + df['Volume_Fraction_Silt']

    # ADJUSTED FINE FRACTION %
    df['Adjusted_Clay_Content'] = (df['Fine_Fraction_Volume(%)'] * df['Volume_Fraction_Clay']) / df['Sum_of_Fine_Fraction_Volume(%)'] if df['Sum_of_Fine_Fraction_Volume(%)'] != 0 else 0
    df['Adjusted_Sand'] = (df['Fine_Fraction_Volume(%)'] * df['Volume_Fraction_Sand']) / df['Sum_of_Fine_Fraction_Volume(%)'] if df['Sum_of_Fine_Fraction_Volume(%)'] != 0 else 0
    df['Adjusted_Silt'] = (df['Fine_Fraction_Volume(%)'] * df['Volume_Fraction_Silt']) / df['Sum_of_Fine_Fraction_Volume(%)'] if df['Sum_of_Fine_Fraction_Volume(%)'] != 0 else 0
    
    # TOTAL VOLUME OF SOLIDS
    df['Volume_of_Solids'] = df['Sum_of_Fine_Fraction_Volume(%)'] + df['Coarse_Fragments_Percentage']
    
    # TOTAL VOLUME OF VOIDS 
    df['Volume_of_Voids'] = total_volume_of_soil - df['Volume_of_Solids']
    
    # VOID RATIO
    df['Void_Ratio'] = df['Volume_of_Voids'] / df['Volume_of_Solids'] if df['Volume_of_Solids'] != 0 else 0
    
    # Apply porosity values to the dataframe
    df[['e_max', 'e_min']] = df.apply(lambda row: pd.Series(assign_porosity(row)), axis=1)

    # Calculate pdmin and pdmax
    df['pdmin'], df['pdmax'] = zip(*df.apply(assign_pdmin_pdmax, axis=1))

    # Calculate dry density (pd)
    df['pd'] = df['Bulk_Density'] / (1 + df['Vol_Water_Content_33kPa']/100)

    # Calculate Relative Density (Dr)
    df['Relative_Density'] = ((df['pd'] - df['pdmin']) / (df['pdmax'] - df['pdmin'])) * 100 if (df['pdmax'] - df['pdmin']) != 0 else 0

    # Calculate Liquid Limit (LL)
    df['Liquid_Limit'] = df.apply(calculate_liquid_limit, axis=1)

    # Calculate Plastic Limit (PL)
    df['Plastic_Limit'] = df.apply(calculate_plastic_limit, axis=1)

    # ATTERBERG LIMITS
    df['Plasticity_Index'] = df['Liquid_Limit'] - df['Plastic_Limit']
    
    # Calculate initial cohesion (c')
    df['Cohesion'] = df.apply(calculate_cohesion_adjusted, axis=1)

    # Adjust cohesion based on Atterberg limits and coarse fragments
    df['Adjusted_Cohesion'] = df.apply(adjust_cohesion, axis=1)

    # Angle of Friction and N-value calculation
    df[['Friction_Bounds', 'pp_min', 'pp_max', 'n_min', 'n_max', 'phi_min', 'phi_max', 'delta_phi', 'rho_b_min', 'rho_b_max', 'phi']] = df.apply(
        lambda row: pd.Series(assign_friction_angle_bounds_and_calculate_n(row['Soil_Texture'], row['Bulk_Density'], row['Soil_Organic_Carbon'] * 100)), axis=1)

    df['SPT_N_Values'] = df.apply(lambda row: calculate_n_value(row['Soil_Texture'], row['Bulk_Density']), axis=1)

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
