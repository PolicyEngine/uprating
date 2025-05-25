from flask import Flask, request, jsonify
from flask_cors import CORS
from policyengine_core.periods import instant
from policyengine_us.system import system
import numpy as np

app = Flask(__name__)
CORS(app)

# Define the number of months in a year
MONTHS_IN_YEAR = 12

def get_parameter_by_path(parameters, path):
    parts = path.split('.')
    param = parameters
    for part in parts:
        if hasattr(param, part):
            param = getattr(param, part)
        else:
            try:
                param = param[part]
            except (KeyError, TypeError):
                return None
    return param

def get_all_values_for_year(parameter, year):
    """Get all available monthly values for a year"""
    monthly_values = {}
    
    for month in range(1, 13):
        month_instant = instant(f"{year}-{month:02d}-01")
        month_value = parameter(month_instant)
        if month_value is not None:
            monthly_values[month] = month_value
    
    return monthly_values

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
        last_month = max(monthly_values.keys())
        return monthly_values[last_month], f"{last_month:02d}"
    else:
        first_month = min(monthly_values.keys())
        return monthly_values[first_month], f"{first_month:02d}"

def round_value(value, rounding_base=1, rounding_method="nearest"):
    """Round a value according to specified method and base."""
    if rounding_base == 0:
        return value
    
    if rounding_method == "nearest":
        return round(value / rounding_base) * rounding_base
    elif rounding_method == "upwards":
        return np.ceil(value / rounding_base) * rounding_base
    elif rounding_method == "downwards":
        return np.floor(value / rounding_base) * rounding_base
    else:
        return value

@app.route('/api/uprating-options', methods=['GET'])
def get_uprating_options():
    """Get available uprating parameters"""
    uprating_options = [
        {"value": "gov.irs.uprating", "label": "IRS Uprating Factor"},
        {"value": "gov.bls.cpi.cpi_u", "label": "CPI-U (Consumer Price Index for All Urban Consumers)"},
        {"value": "gov.bls.cpi.cpi_w", "label": "CPI-W (Consumer Price Index for Urban Wage Earners and Clerical Workers)"},
        {"value": "gov.bls.cpi.c_cpi_u", "label": "C-CPI-U (Chained Consumer Price Index for All Urban Consumers)"},
    ]
    return jsonify(uprating_options)

@app.route('/api/calculate', methods=['POST'])
def calculate_uprating():
    """Calculate uprated values"""
    try:
        data = request.json
        value = float(data['value'])
        start_year = int(data['startYear'])
        projection_years = int(data['projectionYears'])
        selected_uprating = data['selectedUprating']
        rounding_base = float(data['roundingBase'])
        rounding_method = data['roundingMethod']
        
        # Get parameters from the system
        parameters = system.parameters
        uprating_parameter = get_parameter_by_path(parameters, selected_uprating)
        
        if uprating_parameter is None:
            return jsonify({"error": f"Could not find parameter: {selected_uprating}"}), 400
        
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
                continue
                
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
        warnings = []
        
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
                    warnings.append(f"No data available for {year}")
                if prev_year not in year_values:
                    warnings.append(f"No data available for {prev_year}")
                    
                # Use last value without uprating
                uprated_values.append(current_value)
                uprating_factors.append(0.0)
                used_months.append("Missing data")
        
        # Apply rounding to the uprated values
        rounded_values = [round_value(val, rounding_base, rounding_method) for val in uprated_values]
        
        # Prepare the response data
        results = []
        for i, year in enumerate(years):
            results.append({
                "year": year,
                "upratingFactor": uprating_factors[i],
                "originalValue": uprated_values[i],
                "roundedValue": rounded_values[i],
                "month": used_months[i]
            })
        
        return jsonify({
            "results": results,
            "warnings": warnings
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)