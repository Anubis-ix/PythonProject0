def analyze_safety(data):
    """
    Simulates checking a construction plan for mistakes based on BS8110/EC2 principles.
    """
    errors = []
    
    # Rule 1: Minimum beam depth for span (L/16 rule of thumb for RC - RCC41)
    span = float(data.get('span', 0))
    depth = float(data.get('depth', 0))
    if span > 0 and depth > 0:
        if depth < span / 16:
            errors.append(f"Safety Warning (BS8110/EC2): Beam depth ({depth}m) is likely insufficient for a {span}m span. Recommended: at least {span/16:.2f}m according to RCC41 guidelines.")

    # Rule 2: Material and height check
    material = data.get('material', '').lower()
    floors = int(data.get('floors', 1))
    if material == 'wood' and floors > 5:
        errors.append("Safety Warning: Wooden structures above 5 floors require specialized fire and structural review.")
    
    # Rule 3: Load bearing check (RCC21/RCC41 simulation)
    if span > 15:
        errors.append("Safety Warning: Large spans (>15m) without intermediate columns require advanced structural verification (RCC21 Subframe Analysis).")

    if not errors:
        return {"status": "Safe", "message": "No major structural errors detected based on provided parameters (Sync: RCC Spreadsheets v2.0)."}
    else:
        return {"status": "Warning", "errors": errors}

def analyze_components(data):
    """
    Analyzes specific building components using RCC Spreadsheet logic (Slabs, Columns, Stairs, and Beams).
    """
    results = {}

    # Slab Analysis (RCC31)
    slab = data.get('slab', {})
    thickness = float(slab.get('thickness', 0))
    span = float(slab.get('span', 0))
    if span > 0 and thickness > 0:
        # Simple rule: thickness should be at least L/20 for simple support (BS8110)
        min_thickness = (span * 1000) / 20
        if thickness < min_thickness:
            results['slab'] = f"Warning (RCC31): Slab thickness ({thickness}mm) is less than recommended {min_thickness:.0f}mm for a {span}m span (L/20 rule)."
        else:
            results['slab'] = "Safe: Slab thickness meets standard RCC31/BS8110 requirements."

    # Column Analysis (RCC51)
    column = data.get('column', {})
    height = float(column.get('height', 0))
    width = float(column.get('width', 0))
    if height > 0 and width > 0:
        slenderness = (height * 1000) / width
        if slenderness > 15:
            results['column'] = f"Warning (RCC51): Column is slender (Ratio: {slenderness:.1f}). May require buckling analysis according to EC2. Consider increasing width."
        else:
            results['column'] = "Safe: Column slenderness ratio is within normal limits for short columns (RCC51)."

    # Stair Analysis (RCC72)
    stair = data.get('stair', {})
    riser = float(stair.get('riser', 0))
    tread = float(stair.get('tread', 0))
    if riser > 0 and tread > 0:
        # Rule: 2R + T should be between 600 and 650
        stair_val = 2 * riser + tread
        if 600 <= stair_val <= 650:
            results['stair'] = "Safe: Stair dimensions comply with the 2R+T comfort rule (RCC72)."
        else:
            results['stair'] = f"Warning (RCC72): Stair dimensions may be uncomfortable or unsafe (2R+T = {stair_val:.0f}). Target: 600-650mm."

    # Continuous Beam Analysis (RCC41) - Replaced Roof Analysis
    roof = data.get('roof', {}) # Keep key for compatibility
    bspan = float(roof.get('pitch', 0)) # Using pitch field for span in the form
    btype = roof.get('type', 'pitched')
    if bspan > 8:
        results['roof'] = f"Warning (RCC41): Long span beam ({bspan}m) detected. Deflection control is critical. Refer to RCC41 for rigorous check."
    else:
        results['roof'] = "Safe: Continuous beam configuration appears standard (RCC41)."

    return results

def calculate_energy(data):
    """
    Calculates estimated annual energy needs based on area and insulation.
    """
    area = float(data.get('area', 0))
    insulation_quality = data.get('insulation', 'medium')
    
    # Base energy factor (kWh/m2/year)
    factors = {'high': 50, 'medium': 100, 'low': 200}
    factor = factors.get(insulation_quality, 100)
    
    annual_needs = area * factor
    
    # Sustainability advice
    advice = "Consider solar panels to offset costs."
    if insulation_quality == 'low':
        advice = "Upgrading insulation could reduce energy needs by up to 50%."
    elif insulation_quality == 'high':
        advice = "Excellent insulation. Consider heat recovery ventilation to further improve efficiency."
    
    return {
        "annual_energy_kwh": annual_needs,
        "advice": advice,
        "category": "Sustainable" if (annual_needs / area) < 60 else "Average" if (annual_needs / area) < 150 else "High Consumption"
    }
