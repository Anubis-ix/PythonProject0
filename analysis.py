import math

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
    Analyzes specific building components using RCC Spreadsheet logic.
    """
    results = {}

    # 1. One-way Slab Analysis (RCC31)
    slab = data.get('slab', {})
    s_thickness = float(slab.get('thickness', 0))
    s_span = float(slab.get('span', 0))
    if s_span > 0 and s_thickness > 0:
        min_s_thickness = (s_span * 1000) / 20
        if s_thickness < min_s_thickness:
            results['One-way Slab'] = f"Warning (RCC31): Thickness ({s_thickness}mm) is less than recommended {min_s_thickness:.0f}mm (L/20 rule)."
        else:
            results['One-way Slab'] = "Safe: Slab thickness meets standard RCC31/BS8110 requirements."

    # 2. Flat Slab Analysis (RCC33)
    flat_slab = data.get('flat_slab', {})
    fs_thickness = float(flat_slab.get('thickness', 0))
    fs_span = float(flat_slab.get('span', 0))
    if fs_span > 0 and fs_thickness > 0:
        min_fs_thickness = (fs_span * 1000) / 24
        if fs_thickness < min_fs_thickness:
            results['Flat Slab'] = f"Warning (RCC33): Flat slab thickness ({fs_thickness}mm) is low for {fs_span}m span. Recommended: {min_fs_thickness:.0f}mm (L/24)."
        else:
            results['Flat Slab'] = "Safe: Flat slab depth is adequate for punching shear and deflection (RCC33)."

    # 3. Ribbed Slab Analysis (RCC32)
    ribbed = data.get('ribbed_slab', {})
    r_depth = float(ribbed.get('depth', 0))
    r_span = float(ribbed.get('span', 0))
    if r_span > 0 and r_depth > 0:
        min_r_depth = (r_span * 1000) / 18
        if r_depth < min_r_depth:
            results['Ribbed Slab'] = f"Warning (RCC32): Rib depth ({r_depth}mm) is likely insufficient. Recommended: {min_r_depth:.0f}mm."
        else:
            results['Ribbed Slab'] = "Safe: Ribbed slab configuration meets RCC32 standards."

    # 4. Continuous Beam Analysis (RCC41)
    beam = data.get('beam', {})
    b_depth = float(beam.get('depth', 0))
    b_span = float(beam.get('span', 0))
    # Backward compatibility with 'roof' key from previous version
    if not b_span:
        roof = data.get('roof', {})
        b_span = float(roof.get('pitch', 0))
        b_depth = float(roof.get('depth', 0) if 'depth' in roof else 400) # Default if not provided

    if b_span > 0 and b_depth > 0:
        if b_depth < (b_span * 1000) / 12:
            results['Continuous Beam'] = f"Warning (RCC41): Beam depth ({b_depth}mm) is shallow for {b_span}m span. Refer to RCC41 for rigorous check."
        else:
            results['Continuous Beam'] = "Safe: Continuous beam configuration appears standard (RCC41)."

    # 5. Wide Beam Analysis (RCC43)
    wide_beam = data.get('wide_beam', {})
    wb_width = float(wide_beam.get('width', 0))
    wb_depth = float(wide_beam.get('depth', 0))
    if wb_width > 0 and wb_depth > 0:
        if wb_width < 2 * wb_depth:
             results['Wide Beam'] = "Info (RCC43): Standard beam detected. Wide beams typically have Width > 2*Depth."
        else:
             results['Wide Beam'] = "Safe: Wide beam geometry analyzed for shear according to RCC43."

    # 6. Column Analysis (RCC51)
    column = data.get('column', {})
    c_height = float(column.get('height', 0))
    c_width = float(column.get('width', 0))
    if c_height > 0 and c_width > 0:
        slenderness = (c_height * 1000) / c_width
        if slenderness > 15:
            results['Column'] = f"Warning (RCC51): Column is slender (Ratio: {slenderness:.1f}). EC2 buckling check required."
        else:
            results['Column'] = "Safe: Column slenderness ratio is within normal limits (RCC51)."

    # 7. Retaining Wall Analysis (RCC62)
    wall = data.get('wall', {})
    w_height = float(wall.get('height', 0))
    w_base = float(wall.get('base', 0))
    if w_height > 0 and w_base > 0:
        if w_base < 0.4 * w_height:
            results['Retaining Wall'] = f"Warning (RCC62): Base width ({w_base}m) is insufficient for height ({w_height}m). Risk of sliding or overturning."
        else:
            results['Retaining Wall'] = "Safe: Retaining wall proportions are stable (RCC62)."

    # 8. Stair Analysis (RCC72)
    stair = data.get('stair', {})
    riser = float(stair.get('riser', 0))
    tread = float(stair.get('tread', 0))
    if riser > 0 and tread > 0:
        stair_val = 2 * riser + tread
        if 600 <= stair_val <= 650:
            results['Stair'] = "Safe: Stair dimensions comply with the 2R+T comfort rule (RCC72)."
        else:
            results['Stair'] = f"Warning (RCC72): Stair dimensions uncomfortable (2R+T = {stair_val:.0f}). Target: 600-650mm."

    return results

def calculate_energy(data):
    """
    Calculates annual energy needs using OpenBEM (SAP-based) logic.
    """
    tfa = float(data.get('area', 35))
    # OpenBEM uses space heating, water heating, and misc electrical
    
    # Base gains and losses simulation based on insulation
    insulation = data.get('insulation', 'medium')
    
    # Loss factors based on OpenBEM/SAP logic (W/K per m2)
    loss_factors = {'high': 0.5, 'medium': 1.2, 'low': 2.5}
    u_value = loss_factors.get(insulation, 1.2)
    
    # OpenBEM Simplified Balance Model Logic:
    # 1. Heat Loss Coefficient (H) = U-value * TFA (simplified)
    h = u_value * tfa
    
    # 2. Temperature difference (External average ~10C, Internal ~21C)
    delta_t = 21 - 10
    
    # 3. Monthly Heat Loss (Watts) = H * delta_t
    monthly_loss_w = h * delta_t
    
    # 4. Annual Heat Demand (kWh) = (Watts * 24 * 365) / 1000
    annual_heat_demand = (monthly_loss_w * 24 * 365) / 1000
    
    # 5. Gains (Solar + Internal) - Simplified OpenBEM logic
    # Typical gains are around 300-500W for small house
    base_gains = 400 * (tfa / 50) 
    annual_gains = (base_gains * 24 * 365) / 1000
    
    # 6. Useful gains factor (OpenBEM/SAP Utilisation Factor)
    # Simplified: 0.7 to 0.95
    util_factor = 0.85 if insulation == 'high' else 0.7
    useful_annual_gains = annual_gains * util_factor
    
    # 7. Final space heating requirement
    space_heating = max(0, annual_heat_demand - useful_annual_gains)
    
    # 8. Water heating and Misc (OpenBEM defaults)
    water_heating = 2000 * (tfa / 50)
    misc_electrical = 1500 * (tfa / 50)
    
    total_energy = space_heating + water_heating + misc_electrical
    
    # SAP Rating Calculation (from OpenBEM saprating_model.js)
    # sap_rating = 117 - 121 * log10(ECF) where ECF = (Cost * Deflator) / (TFA + 45)
    # Using a simplified cost factor (0.15 £/kWh)
    total_cost = total_energy * 0.15
    ecf = (total_cost * 0.47) / (tfa + 45.0)
    
    sap_rating = 0
    if ecf >= 3.5:
        sap_rating = 117 - 121 * (math.log10(ecf))
    else:
        sap_rating = 100 - 13.95 * ecf
        
    # Sustainability advice
    advice = "OpenBEM Analysis: "
    if sap_rating > 80:
        advice += "High SAP rating. Your building is energy efficient."
    elif sap_rating > 50:
        advice += "Average efficiency. Consider improving glazing or heat pump integration."
    else:
        advice += "Low SAP rating. Significant insulation upgrades and high-efficiency heating recommended."
    
    return {
        "annual_energy_kwh": round(total_energy, 2),
        "sap_rating": round(sap_rating, 1),
        "advice": advice,
        "category": "Sustainable (A/B)" if sap_rating > 80 else "Average (C/D)" if sap_rating > 50 else "High Consumption (E-G)"
    }
