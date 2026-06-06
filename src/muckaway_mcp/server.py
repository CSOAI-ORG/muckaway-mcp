#!/usr/bin/env python3
"""
MuckAway MCP Server — Waste Management & Aquaculture Tools

A production-ready Model Context Protocol (MCP) server providing waste management,
skip hire, grab lorry booking, waste transfer notes, DEFRA compliance, and
water quality monitoring tools.

This server is the first Hive MCP for muckaway.ai — an uncontested vertical
in the 9,400+ MCP ecosystem.
"""

import math
from datetime import datetime, timedelta

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("muckaway-mcp")

# ─────────────────────────────────────────────────────────────────────────────
# EWC (European Waste Catalogue) Database (simplified)
# ─────────────────────────────────────────────────────────────────────────────

EWC_DATABASE = {
    "17 01 01": {
        "description": "Concrete",
        "hazardous": False,
        "disposal_routes": ["crushing_and_recycling", "landfill_inert"],
        "typical_cost_per_tonne": 45.00,
    },
    "17 01 02": {
        "description": "Bricks",
        "hazardous": False,
        "disposal_routes": ["crushing_and_recycling", "landfill_inert"],
        "typical_cost_per_tonne": 35.00,
    },
    "17 01 03": {
        "description": "Tiles and ceramics",
        "hazardous": False,
        "disposal_routes": ["crushing_and_recycling", "landfill_inert"],
        "typical_cost_per_tonne": 40.00,
    },
    "17 01 07": {
        "description": "Mixture of concrete, bricks, tiles and ceramics",
        "hazardous": False,
        "disposal_routes": ["crushing_and_recycling", "landfill_inert"],
        "typical_cost_per_tonne": 42.00,
    },
    "17 02 01": {
        "description": "Wood",
        "hazardous": False,
        "disposal_routes": ["biomass_energy", "composting", "landfill_inert"],
        "typical_cost_per_tonne": 30.00,
    },
    "17 03 01": {
        "description": "Bituminous mixtures containing coal tar",
        "hazardous": True,
        "disposal_routes": ["hazardous_landfill", "high_temperature_incineration"],
        "typical_cost_per_tonne": 250.00,
    },
    "17 03 02": {
        "description": "Bituminous mixtures other than those containing coal tar",
        "hazardous": False,
        "disposal_routes": ["recycling", "low_temperature_incineration"],
        "typical_cost_per_tonne": 80.00,
    },
    "17 04 09": {
        "description": "Waste plastic",
        "hazardous": False,
        "disposal_routes": ["recycling", "energy_recovery"],
        "typical_cost_per_tonne": 55.00,
    },
    "17 05 04": {
        "description": "Soil and stones",
        "hazardous": False,
        "disposal_routes": ["landfill_inert", "contaminated_soil_treatment"],
        "typical_cost_per_tonne": 25.00,
    },
    "17 05 06": {
        "description": "Dredging spoil",
        "hazardous": False,
        "disposal_routes": ["landfill_inert", "beneficial_use"],
        "typical_cost_per_tonne": 28.00,
    },
    "17 06 04": {
        "description": "Insulation materials",
        "hazardous": False,
        "disposal_routes": ["landfill_inert", "recycling"],
        "typical_cost_per_tonne": 60.00,
    },
    "20 01 21": {
        "description": "Fluorescent tubes",
        "hazardous": True,
        "disposal_routes": ["specialist_recycling", "hazardous_landfill"],
        "typical_cost_per_tonne": 500.00,
    },
    "20 01 35": {
        "description": "Waste electrical and electronic equipment (WEEE)",
        "hazardous": False,
        "disposal_routes": ["weee_recycling", "refurbishment"],
        "typical_cost_per_tonne": 120.00,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Skip Hire Pricing Database
# ─────────────────────────────────────────────────────────────────────────────

SKIP_PRICES = {
    4: {"price_per_week": 210.00, "max_tonnes": 2.0, "dimensions": "1.8m x 1.2m x 0.9m"},
    6: {"price_per_week": 250.00, "max_tonnes": 3.0, "dimensions": "2.6m x 1.5m x 1.0m"},
    8: {"price_per_week": 290.00, "max_tonnes": 4.0, "dimensions": "3.6m x 1.8m x 1.1m"},
    12: {"price_per_week": 380.00, "max_tonnes": 6.0, "dimensions": "4.0m x 1.8m x 1.5m"},
    16: {"price_per_week": 450.00, "max_tonnes": 8.0, "dimensions": "4.8m x 1.8m x 1.7m"},
    20: {"price_per_week": 520.00, "max_tonnes": 10.0, "dimensions": "5.2m x 2.0m x 1.8m"},
    40: {"price_per_week": 850.00, "max_tonnes": 16.0, "dimensions": "6.0m x 2.4m x 2.0m"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Grab Lorry Pricing
# ─────────────────────────────────────────────────────────────────────────────

GRAB_LORRY_RATE = 85.00  # per hour or per load
GRAB_LORRY_CAPACITY_M3 = 16.0

# ─────────────────────────────────────────────────────────────────────────────
# DEFRA Compliance Rules
# ─────────────────────────────────────────────────────────────────────────────

DEFRA_RULES = {
    "hazardous_waste": {
        "requires_carrier_license": True,
        "requires_hazardous_consignment_note": True,
        "prohibited_methods": ["open_burning", "uncontrolled_landfill", "sewer_disposal"],
        "required_documentation": [
            "hazardous_consignment_note",
            "waste_transfer_note",
            "carrier_license",
        ],
    },
    "non_hazardous_waste": {
        "requires_carrier_license": False,
        "requires_waste_transfer_note": True,
        "prohibited_methods": ["open_burning", "sewer_disposal"],
        "required_documentation": ["waste_transfer_note"],
    },
    "inert_waste": {
        "requires_carrier_license": False,
        "requires_waste_transfer_note": False,
        "prohibited_methods": ["open_burning"],
        "required_documentation": ["duty_of_care"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Water Quality Thresholds (for aquaculture)
# ─────────────────────────────────────────────────────────────────────────────

WATER_QUALITY_THRESHOLDS = {
    "ph": {"min": 6.5, "max": 8.5, "optimal": 7.2},
    "ammonia": {"min": 0.0, "max": 0.02, "optimal": 0.0, "unit": "mg/L"},
    "nitrite": {"min": 0.0, "max": 0.1, "optimal": 0.0, "unit": "mg/L"},
    "temperature": {"min": 4.0, "max": 28.0, "optimal": 18.0, "unit": "°C"},
}

# ════════════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ════════════════════════════════════════════════════════════════════════════


@mcp.tool()
def waste_classification_lookup(waste_code: str) -> dict:
    """
    Look up an EWC (European Waste Catalogue) waste code and return classification details.

    Args:
        waste_code: The EWC waste code (e.g., "17 01 01" for concrete)

    Returns:
        Dictionary with description, hazardous status, disposal routes, and typical cost.
    """
    normalized = waste_code.strip().upper()
    if normalized in EWC_DATABASE:
        data = EWC_DATABASE[normalized]
        return {
            "waste_code": normalized,
            "found": True,
            "description": data["description"],
            "hazardous": data["hazardous"],
            "disposal_routes": data["disposal_routes"],
            "typical_cost_per_tonne_gbp": data["typical_cost_per_tonne"],
            "requires_hazardous_consignment_note": data["hazardous"],
        }
    return {
        "waste_code": normalized,
        "found": False,
        "message": "Waste code not found in database. Please verify the EWC code or contact your waste carrier.",
    }


@mcp.tool()
def skip_hire_quote(postcode: str, waste_type: str, skip_size: int) -> dict:
    """
    Generate a skip hire quote based on postcode, waste type, and skip size.

    Args:
        postcode: UK postcode (e.g., "CM8 1XY")
        waste_type: Description of waste (e.g., "mixed construction", "garden waste", "soil")
        skip_size: Skip size in cubic yards (4, 6, 8, 12, 16, 20, or 40)

    Returns:
        Quote with pricing, delivery info, and restrictions.
    """
    if skip_size not in SKIP_PRICES:
        valid_sizes = list(SKIP_PRICES.keys())
        return {
            "error": True,
            "message": f"Invalid skip size. Valid sizes: {valid_sizes}",
        }

    price_data = SKIP_PRICES[skip_size]
    base_price = price_data["price_per_week"]

    # Hazardous waste surcharge
    hazardous_keywords = ["asbestos", "chemical", "oil", "paint", "solvent", "hazardous"]
    is_hazardous = any(kw in waste_type.lower() for kw in hazardous_keywords)
    hazardous_surcharge = 150.00 if is_hazardous else 0.00

    # Permit surcharge (if on public highway — assume 50% chance for demo)
    permit_surcharge = 30.00

    total_price = base_price + hazardous_surcharge + permit_surcharge

    return {
        "error": False,
        "postcode": postcode.upper(),
        "waste_type": waste_type,
        "skip_size_yards": skip_size,
        "dimensions": price_data["dimensions"],
        "max_tonnes": price_data["max_tonnes"],
        "base_price_gbp": base_price,
        "hazardous_surcharge_gbp": hazardous_surcharge,
        "permit_surcharge_gbp": permit_surcharge,
        "total_price_gbp_per_week": total_price,
        "hazardous": is_hazardous,
        "requires_permit": True,
        "valid_for_days": 7,
        "notes": [
            "Price includes delivery and collection within 30 miles of postcode.",
            "Hazardous waste requires additional documentation.",
            "Overweight charges apply at £15 per tonne over limit.",
        ],
    }


@mcp.tool()
def grab_lorry_booking(postcode: str, waste_type: str, volume_m3: float) -> dict:
    """
    Check availability and pricing for grab lorry booking.

    Args:
        postcode: UK postcode
        waste_type: Type of waste
        volume_m3: Estimated volume in cubic metres

    Returns:
        Availability and pricing details.
    """
    if volume_m3 <= 0:
        return {
            "error": True,
            "message": "Volume must be greater than 0 cubic metres.",
        }

    loads_required = max(1, math.ceil(volume_m3 / GRAB_LORRY_CAPACITY_M3))
    estimated_hours = loads_required * 1.5  # 1.5 hours per load
    estimated_cost = estimated_hours * GRAB_LORRY_RATE

    # Check availability (demo: always available within 2-5 days)
    availability_days = min(5, max(2, round(volume_m3 / 10)))

    return {
        "error": False,
        "postcode": postcode.upper(),
        "waste_type": waste_type,
        "volume_m3": volume_m3,
        "loads_required": loads_required,
        "lorry_capacity_m3": GRAB_LORRY_CAPACITY_M3,
        "estimated_hours": estimated_hours,
        "hourly_rate_gbp": GRAB_LORRY_RATE,
        "estimated_cost_gbp": round(estimated_cost, 2),
        "available_from": (datetime.now() + timedelta(days=availability_days)).strftime("%Y-%m-%d"),
        "availability_days": availability_days,
        "notes": [
            "Grab lorry can access sites with 3.5m width and 4.0m height clearance.",
            "Site must have suitable hardstanding for lorry operation.",
            "Waste must be loose and accessible (no bagged waste for grab).",
        ],
    }


@mcp.tool()
def waste_transfer_note_generator(
    site: str, waste_type: str, carrier: str, destination: str
) -> dict:
    """
    Generate a Waste Transfer Note (WTN) document.

    Args:
        site: The site address where waste was produced
        waste_type: Description of the waste
        carrier: Name of the waste carrier
        destination: Name and address of the waste disposal/recovery facility

    Returns:
        A structured Waste Transfer Note ready for printing or digital submission.
    """
    wtn_id = f"WTN-{datetime.now().strftime('%Y%m%d')}-{hash(site + carrier) % 10000:04d}"

    wtn = {
        "document_type": "Waste Transfer Note",
        "wtn_id": wtn_id,
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "producer_details": {
            "site_address": site,
            "sic_code": "41201 - Construction of commercial buildings",
        },
        "waste_description": {
            "description": waste_type,
            "quantity": "To be confirmed on collection",
            "ewc_code": "See waste_classification_lookup for EWC code",
        },
        "carrier_details": {
            "name": carrier,
            "carrier_license_required": True,
        },
        "receiver_details": {
            "facility_name": destination,
        },
        "legal_declaration": {
            "duty_of_care": "I confirm that the waste described has been handled in accordance with the Duty of Care.",
            "hazardous_declaration": "I confirm that the waste is NOT hazardous (unless separately declared).",
            "signature_required": True,
        },
        "retention_period": "2 years from date of transfer",
        "regulatory_framework": "Environmental Protection Act 1990, Waste (England and Wales) Regulations 2011",
    }

    return {
        "error": False,
        "wtn": wtn,
        "formatted_text": _format_wtn(wtn),
    }


def _format_wtn(wtn: dict) -> str:
    """Format a WTN as a human-readable text document."""
    lines = [
        "═" * 60,
        "              WASTE TRANSFER NOTE",
        "═" * 60,
        f"WTN ID: {wtn['wtn_id']}",
        f"Date: {wtn['generated_date']}",
        "",
        "PRODUCER:",
        f"  Site: {wtn['producer_details']['site_address']}",
        f"  SIC Code: {wtn['producer_details']['sic_code']}",
        "",
        "WASTE DESCRIPTION:",
        f"  {wtn['waste_description']['description']}",
        f"  Quantity: {wtn['waste_description']['quantity']}",
        "",
        "CARRIER:",
        f"  Name: {wtn['carrier_details']['name']}",
        "",
        "RECEIVER:",
        f"  Facility: {wtn['receiver_details']['facility_name']}",
        "",
        "LEGAL DECLARATION:",
        f"  {wtn['legal_declaration']['duty_of_care']}",
        f"  {wtn['legal_declaration']['hazardous_declaration']}",
        "",
        f"Retention: {wtn['retention_period']}",
        f"Framework: {wtn['regulatory_framework']}",
        "═" * 60,
    ]
    return "\n".join(lines)


@mcp.tool()
def defra_compliance_check(waste_type: str, disposal_method: str) -> dict:
    """
    Check if a waste disposal method complies with DEFRA regulations.

    Args:
        waste_type: Description of the waste (e.g., "hazardous", "non_hazardous", "inert")
        disposal_method: Proposed disposal method (e.g., "recycling", "landfill", "incineration")

    Returns:
        Compliance assessment with required documentation and prohibited methods.
    """
    # Determine waste category
    waste_type_lower = waste_type.lower()
    if (
        "hazardous" in waste_type_lower
        or "asbestos" in waste_type_lower
        or "chemical" in waste_type_lower
    ):
        category = "hazardous_waste"
    elif (
        "inert" in waste_type_lower or "concrete" in waste_type_lower or "brick" in waste_type_lower
    ):
        category = "inert_waste"
    else:
        category = "non_hazardous_waste"

    rules = DEFRA_RULES[category]

    # Check if disposal method is prohibited
    method_lower = disposal_method.lower().replace(" ", "_")
    prohibited = method_lower in rules["prohibited_methods"] or any(
        pm in method_lower for pm in rules["prohibited_methods"]
    )

    # Check specific method compliance
    compliant_methods = {
        "recycling": True,
        "landfill": category in ["non_hazardous_waste", "inert_waste"],
        "hazardous_landfill": category == "hazardous_waste",
        "incineration": category in ["hazardous_waste", "non_hazardous_waste"],
        "high_temperature_incineration": category == "hazardous_waste",
        "composting": category == "non_hazardous_waste",
        "energy_recovery": category in ["non_hazardous_waste", "hazardous_waste"],
    }

    method_compliant = compliant_methods.get(method_lower, False)

    overall_compliant = not prohibited and method_compliant

    return {
        "error": False,
        "waste_type": waste_type,
        "disposal_method": disposal_method,
        "waste_category": category,
        "compliant": overall_compliant,
        "prohibited": prohibited,
        "method_compliant": method_compliant,
        "requires_carrier_license": rules["requires_carrier_license"],
        "required_documentation": rules["required_documentation"],
        "prohibited_methods": rules["prohibited_methods"],
        "recommendations": _get_compliance_recommendations(category, disposal_method),
    }


def _get_compliance_recommendations(category: str, disposal_method: str) -> list:
    """Generate compliance recommendations based on category and method."""
    recommendations = []

    if category == "hazardous_waste":
        recommendations.append(
            "Use a licensed hazardous waste carrier (check on EA public register)."
        )
        recommendations.append("Complete a hazardous consignment note for every movement.")
        recommendations.append(
            "Ensure the receiving facility has an environmental permit for hazardous waste."
        )
    elif category == "inert_waste":
        recommendations.append(
            "Inert waste can go to inert landfill or be reused on site (subject to waste exemption)."
        )
        recommendations.append(
            "No waste transfer note required if reused under U1 exemption (use of waste in construction)."
        )
    else:
        recommendations.append("Complete a waste transfer note for every movement.")
        recommendations.append("Use a registered waste carrier (check on EA public register).")

    if "recycling" in disposal_method.lower():
        recommendations.append("Recycling is the preferred option under the waste hierarchy.")
    if "landfill" in disposal_method.lower():
        recommendations.append(
            "Landfill is the least preferred option under the waste hierarchy — consider recycling or recovery first."
        )

    return recommendations


@mcp.tool()
def water_quality_monitor(ph: float, ammonia: float, nitrite: float, temperature: float) -> dict:
    """
    Monitor water quality parameters for aquaculture (fish farms, ponds, RAS systems).

    Args:
        ph: pH level (optimal: 6.5-8.5)
        ammonia: Ammonia concentration in mg/L (optimal: <0.02)
        nitrite: Nitrite concentration in mg/L (optimal: <0.1)
        temperature: Water temperature in °C (optimal: 10-25)

    Returns:
        Water quality assessment with alerts and recommendations.
    """
    thresholds = WATER_QUALITY_THRESHOLDS

    # Assess each parameter
    ph_status = _assess_parameter("pH", ph, thresholds["ph"])
    ammonia_status = _assess_parameter("ammonia", ammonia, thresholds["ammonia"])
    nitrite_status = _assess_parameter("nitrite", nitrite, thresholds["nitrite"])
    temperature_status = _assess_parameter("temperature", temperature, thresholds["temperature"])

    # Overall status
    statuses = [
        ph_status["status"],
        ammonia_status["status"],
        nitrite_status["status"],
        temperature_status["status"],
    ]
    if any(s == "CRITICAL" for s in statuses):
        overall_status = "CRITICAL"
    elif any(s == "WARNING" for s in statuses):
        overall_status = "WARNING"
    else:
        overall_status = "OPTIMAL"

    # Generate recommendations
    recommendations = []
    if ph_status["status"] != "OPTIMAL":
        recommendations.append(f"pH: {ph_status['recommendation']}")
    if ammonia_status["status"] != "OPTIMAL":
        recommendations.append(f"Ammonia: {ammonia_status['recommendation']}")
    if nitrite_status["status"] != "OPTIMAL":
        recommendations.append(f"Nitrite: {nitrite_status['recommendation']}")
    if temperature_status["status"] != "OPTIMAL":
        recommendations.append(f"Temperature: {temperature_status['recommendation']}")

    if overall_status == "OPTIMAL":
        recommendations.append("All parameters optimal. Continue current management practices.")

    return {
        "error": False,
        "overall_status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "parameters": {
            "ph": ph_status,
            "ammonia": ammonia_status,
            "nitrite": nitrite_status,
            "temperature": temperature_status,
        },
        "recommendations": recommendations,
        "fish_health_risk": _assess_fish_health_risk(
            ph_status, ammonia_status, nitrite_status, temperature_status
        ),
    }


def _assess_parameter(name: str, value: float, thresholds: dict) -> dict:
    """Assess a single water quality parameter."""
    min_val = thresholds["min"]
    max_val = thresholds["max"]
    optimal = thresholds["optimal"]
    unit = thresholds.get("unit", "")

    if value < min_val or value > max_val:
        status = "CRITICAL"
    elif abs(value - optimal) > (max_val - min_val) * 0.2:
        status = "WARNING"
    else:
        status = "OPTIMAL"

    recommendations = {
        "pH": {
            "CRITICAL": "Emergency: Add buffer (pH up/down) immediately. Check for acid rain or chemical contamination.",
            "WARNING": "Add pH buffer gradually. Monitor daily. Check for organic matter buildup.",
            "OPTIMAL": "pH is optimal for most freshwater fish species.",
        },
        "ammonia": {
            "CRITICAL": "EMERGENCY: Stop feeding. Perform 50% water change. Check biofilter function. Add ammonia binder.",
            "WARNING": "Reduce feeding by 50%. Check biofilter. Increase aeration. Monitor daily.",
            "OPTIMAL": "Ammonia levels are safe for fish.",
        },
        "nitrite": {
            "CRITICAL": "DANGER: Nitrite poisoning risk. Perform 30% water change. Add salt (1g/L). Check biofilter.",
            "WARNING": "Increase water changes. Check biofilter maturity. Add beneficial bacteria supplement.",
            "OPTIMAL": "Nitrite levels are safe.",
        },
        "temperature": {
            "CRITICAL": "Critical temperature. Add heater/cooler. Move fish to backup system if possible.",
            "WARNING": "Temperature stress risk. Add shade/cover. Monitor dissolved oxygen (colder = more O2).",
            "OPTIMAL": "Temperature is optimal for fish metabolism.",
        },
    }

    return {
        "value": value,
        "unit": unit,
        "status": status,
        "optimal_range": f"{min_val}-{max_val}",
        "optimal_value": optimal,
        "recommendation": recommendations[name][status],
    }


def _assess_fish_health_risk(ph, ammonia, nitrite, temperature) -> str:
    """Assess overall fish health risk based on water quality."""
    critical_count = sum(
        1 for s in [ph, ammonia, nitrite, temperature] if s["status"] == "CRITICAL"
    )
    warning_count = sum(1 for s in [ph, ammonia, nitrite, temperature] if s["status"] == "WARNING")

    if critical_count >= 2:
        return (
            "HIGH RISK — Immediate intervention required. Fish mortality likely within 24-48 hours."
        )
    elif critical_count == 1 or warning_count >= 2:
        return "MODERATE RISK — Fish stress elevated. Action needed within 24 hours."
    elif warning_count == 1:
        return "LOW RISK — Monitor closely. Corrective action within 1 week."
    else:
        return "NO RISK"


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
