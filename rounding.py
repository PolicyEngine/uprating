"""
Rounding functions for PolicyEngine Uprating Calculator.
"""
import numpy as np

def round_value(value, rounding_base=1, rounding_method="nearest"):
    """
    Round a value according to specified method and base.
    
    Parameters:
    -----------
    value : float
        The value to be rounded
    rounding_base : float
        The base to round to (e.g., 1 for nearest dollar, 10 for nearest ten, 0.01 for nearest cent)
    rounding_method : str
        The rounding method to use: "nearest", "up", or "down"
        
    Returns:
    --------
    float
        The rounded value
    """
    if rounding_base == 0:
        return value
    
    if rounding_method == "nearest":
        # Round to the nearest multiple of rounding_base
        return round(value / rounding_base) * rounding_base
    elif rounding_method == "upwards":
        # Round up to the next multiple of rounding_base
        return np.ceil(value / rounding_base) * rounding_base
    elif rounding_method == "downwards":
        # Round down to the previous multiple of rounding_base
        return np.floor(value / rounding_base) * rounding_base
    else:
        # If an invalid method is provided, return the original value
        return value


def apply_rounding_to_dataframe(df, column_name, rounding_base, rounding_method):
    """
    Apply rounding to a specific column in a DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the values to round
    column_name : str
        The name of the column to apply rounding to
    rounding_base : float
        The base to round to
    rounding_method : str
        The rounding method to use: "nearest", "up", or "down"
        
    Returns:
    --------
    pandas.DataFrame
        A copy of the DataFrame with the rounded values
    """
    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()
    
    # Apply rounding to the specified column
    df_copy[column_name] = df_copy[column_name].apply(
        lambda x: round_value(x, rounding_base, rounding_method)
    )
    
    return df_copy