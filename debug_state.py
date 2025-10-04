#!/usr/bin/env python3
"""
Debug state extraction.
"""
def debug_state_extraction(district_name):
    """Debug the state extraction logic."""
    print(f"Debugging: '{district_name}'")
    
    if not district_name:
        print("  Empty district name -> TX")
        return "TX"
    
    district_upper = district_name.upper()
    print(f"  Uppercase: '{district_upper}'")
    
    # Check for two-letter state codes at the beginning
    if len(district_upper) >= 2 and district_upper[:2].isalpha():
        potential_state = district_upper[:2]
        print(f"  Potential state code: '{potential_state}'")
        # Validate it's a real state code (basic check)
        if potential_state in ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]:
            print(f"  Valid state code found: {potential_state}")
            return potential_state
    
    # Check for state names in the district name (prioritize longer names first)
    state_mappings = [
        ("NEW HAMPSHIRE", "NH"), ("NEW JERSEY", "NJ"), ("NEW MEXICO", "NM"), ("NEW YORK", "NY"),
        ("NORTH CAROLINA", "NC"), ("NORTH DAKOTA", "ND"), ("SOUTH CAROLINA", "SC"), ("SOUTH DAKOTA", "SD"),
        ("WEST VIRGINIA", "WV"), ("RHODE ISLAND", "RI"),
        ("MASSACHUSETTS", "MA"), ("MISSISSIPPI", "MS"), ("PENNSYLVANIA", "PA"),
        ("CALIFORNIA", "CA"), ("COLORADO", "CO"), ("CONNECTICUT", "CT"), ("DELAWARE", "DE"),
        ("FLORIDA", "FL"), ("GEORGIA", "GA"), ("HAWAII", "HI"), ("IDAHO", "ID"),
        ("ILLINOIS", "IL"), ("IOWA", "IA"), ("KANSAS", "KS"),
        ("KENTUCKY", "KY"), ("LOUISIANA", "LA"), ("MAINE", "ME"), ("MARYLAND", "MD"),
        ("MICHIGAN", "MI"), ("MINNESOTA", "MN"), ("MISSOURI", "MO"), ("MONTANA", "MT"),
        ("NEVADA", "NV"), ("OHIO", "OH"), ("OKLAHOMA", "OK"),
        ("OREGON", "OR"), ("TENNESSEE", "TN"), ("TEXAS", "TX"), ("UTAH", "UT"),
        ("VERMONT", "VT"), ("VIRGINIA", "VA"), ("WASHINGTON", "WA"), ("WISCONSIN", "WI"), ("WYOMING", "WY"),
        ("ALABAMA", "AL"), ("ALASKA", "AK"), ("ARIZONA", "AZ"), ("ARKANSAS", "AR"),
        ("INDIANA", "IN"), ("NEBRASKA", "NE")  # Put these last to avoid partial matches
    ]
    
    for state_name, state_code in state_mappings:
        if state_name in district_upper:
            print(f"  Found state name '{state_name}' -> {state_code}")
            return state_code
    
    print("  No state found -> TX")
    return "TX"

# Test the problematic cases
print("=== Testing problematic cases ===")
debug_state_extraction("New York-15")
print()
debug_state_extraction("Invalid District")
print()
debug_state_extraction("NE-01")
