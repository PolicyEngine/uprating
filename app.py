import streamlit as st
import pandas as pd
from policyengine_core.periods import instant
from policyengine_us.system import system
from rounding import round_value, apply_rounding_to_dataframe

# Define the number of months in a year
MONTHS_IN_YEAR = 12

st.set_page_config(page_title="PolicyEngine Uprating Calculator", layout="wide")
st.title("PolicyEngine Uprating Calculator")

# Function to safely access a parameter by path
def get_parameter_by_path(parameters, path):
    parts = path.split('.')
    param = parameters
    for part in parts:
        if hasattr(param, part):
            param = getattr(param, part)
        else:
            # Try accessing as a dictionary-like object
            try:
                param = param[part]
            except (KeyError, TypeError):
                return None
    return param

# Function to find all available values for a year
def get_all_values_for_year(parameter, year):
    """Get all available monthly values for a year"""
    monthly_values = {}
    
    for month in range(1, 13):
        month_instant = instant(f"{year}-{month:02d}-01")
        month_value = parameter(month_instant)
        if month_value is not None:
            monthly_values[month] = month_value
    
    return monthly_values

# Function to get the best representative value for a year
def get_best_value_for_year(parameter, year):
    """
    Get the best representative value for a year:
    - For historical years (up to 2024), look for the last available month
    - For projection years (2025+), look for the first available month
    """
    monthly_values = get_all_values_for_year(parameter, year)
    
    if not monthly_values:
        return None, None
    
    if year <= 2024:
        # For historical years, use the last month available
        last_month = max(monthly_values.keys())
        return monthly_values[last_month], f"{last_month:02d}"
    else:
        # For projection years, use the first month available
        first_month = min(monthly_values.keys())
        return monthly_values[first_month], f"{first_month:02d}"

# Sidebar for inputs
with st.sidebar:
    st.header("Input Parameters")
    
    # Input for the value to be uprated
    value = st.number_input("Enter value to be uprated:", min_value=0.0, value=1000.0, step=100.0)
    
    # Input for the start year
    current_year = 2024
    max_year = 2035  # Maximum year with data
    start_year = st.number_input("Enter start year:", min_value=2015, max_value=max_year, value=current_year, step=1)
    
    # Number of years to project (fixed 1-10 years)
    projection_years = 20
    
    # Get parameters from the system
    parameters = system.parameters
    
    # Define available uprating parameters
    uprating_options = [
        "gov.irs.uprating",         # IRS Uprating Factor
        "gov.bls.cpi.cpi_u",        # CPI-U (Consumer Price Index for All Urban Consumers)
        "gov.bls.cpi.cpi_w",        # CPI-W (Consumer Price Index for Urban Wage Earners and Clerical Workers)
        "gov.bls.cpi.c_cpi_u",      # C-CPI-U (Chained Consumer Price Index for All Urban Consumers)
    ]
    
    # Let the user select the uprating parameter
    selected_uprating = st.selectbox("Select uprating parameter:", uprating_options)
    
    # Add Rounding Options
    st.header("Rounding Options")
    
    # Enable/disable rounding
    
    # Rounding base input - allow user to enter any number
    rounding_base_selection = st.number_input(
        "Round to:",
        min_value=0.01,
        max_value=10000.0,
        value=1.0,
        step=1.0,
        format="%.2f",
    )
    
    # Rounding method selection
    rounding_method = st.radio(
        "Rounding method:",
        options=["nearest", "upwards", "downwards"],
        format_func=lambda x: f"Round {x}",
    )

# Main calculations
if st.button("Calculate Uprated Values"):
    try:
        # Getting the uprating parameter
        uprating_parameter = get_parameter_by_path(parameters, selected_uprating)
        
        if uprating_parameter is None:
            st.error(f"Could not find parameter: {selected_uprating}")
            st.stop()
        
        # Create a list of years for which to calculate the uprated values
        years = list(range(start_year, start_year + projection_years + 1))
        
        # Calculate uprated values for each year
        uprated_values = []
        uprating_factors = []
        used_months = []
        
        # Store the last available uprating factor for years beyond 2035
        last_available_uprating_factor = None
        
        # Get values for all years in the range
        year_values = {}
        month_used = {}
        
        for year in range(start_year - 1, start_year + projection_years + 1):
            if year > 2035:
                continue  # Skip years beyond available data
                
            value_for_year, month = get_best_value_for_year(uprating_parameter, year)
            if value_for_year is not None:
                year_values[year] = value_for_year
                month_used[year] = month
        
        # First year is never uprated (original value)
        uprated_values.append(value)
        uprating_factors.append(0.0)
        used_months.append(month_used.get(start_year, "N/A"))
        
        # Calculate for remaining years
        current_value = value
        for i, year in enumerate(years[1:], 1):
            prev_year = years[i-1]
            
            # Handle years beyond 2035 using the last available uprating factor
            if year > 2035:
                if last_available_uprating_factor is not None:
                    current_value *= (1 + last_available_uprating_factor)
                    uprated_values.append(current_value)
                    uprating_factors.append(last_available_uprating_factor)
                    used_months.append("Projected")
                else:
                    # If we don't have a factor for projection, use the last value
                    uprated_values.append(current_value)
                    uprating_factors.append(0.0)
                    used_months.append("No projection data")
                continue
            
            # Calculate uprating factor if we have values for both years
            if year in year_values and prev_year in year_values:
                uprating_factor = (year_values[year] / year_values[prev_year]) - 1
                
                # If uprating factor is suspiciously close to zero, warn the user
                if abs(uprating_factor) < 0.0001 and year >= 2025:                    
                    # Try to get February value for the current year
                    feb_instant = instant(f"{year}-02-01")
                    feb_value = uprating_parameter(feb_instant)
                    
                    if feb_value is not None and feb_value != year_values[year]:
                        # Recalculate with February value
                        uprating_factor = (feb_value / year_values[prev_year]) - 1
                        year_values[year] = feb_value
                        month_used[year] = "02"
                
                current_value *= (1 + uprating_factor)
                uprated_values.append(current_value)
                uprating_factors.append(uprating_factor)
                used_months.append(month_used.get(year, "N/A"))
                
                # Store for projections beyond 2035
                if year == 2035:
                    last_available_uprating_factor = uprating_factor
            else:
                # Handle missing data 
                if year not in year_values:
                    st.warning(f"No data available for {year}")
                if prev_year not in year_values:
                    st.warning(f"No data available for {prev_year}")
                    
                # Use last value without uprating
                uprated_values.append(current_value)
                uprating_factors.append(0.0)
                used_months.append("Missing data")
        
        # Create a DataFrame for displaying the results
        data = {
            "Year": years,
            "Uprating Factor": [f"{factor*100:.2f}%" if factor is not None else "N/A" for factor in uprating_factors],
            "Uprated Value": uprated_values,
        }
        
        df = pd.DataFrame(data)
        
        # Create a copy of the original values for display
        df["Original Value"] = df["Uprated Value"].copy()
        
        # Apply rounding to the uprated values
        df = apply_rounding_to_dataframe(df, "Uprated Value", rounding_base_selection, rounding_method)
        
        # Display both original and rounded values
        df_display = df[["Year", "Uprating Factor", "Original Value", "Uprated Value"]]
        
        # Format the values to 2 decimal places
        df_display["Original Value"] = df_display["Original Value"].round(2)
        df_display["Uprated Value"] = df_display["Uprated Value"].round(2)
        
        # Rename columns to show rounding details
        df_display = df_display.rename(columns={
            "Original Value": "Pre-Rounded Value",
            "Uprated Value": f"Rounded Value ({rounding_method} to {rounding_base_selection})"
        })
        
        st.subheader("Uprated Values (with Rounding)")
        st.dataframe(
            df_display.style.format({
                "Pre-Rounded Value": "${:,.2f}",
                f"Rounded Value ({rounding_method} to {rounding_base_selection})": "${:,.2f}"
            }),
            hide_index=True,
            use_container_width=True
        )

            
    except Exception as e:
        st.error(f"Error in calculation: {e}")
        st.info("Please try a different uprating parameter or check your inputs.")