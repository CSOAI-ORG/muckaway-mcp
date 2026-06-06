"""Test suite for muckaway-mcp server."""

from muckaway_mcp.server import (
    defra_compliance_check,
    grab_lorry_booking,
    skip_hire_quote,
    waste_classification_lookup,
    waste_transfer_note_generator,
    water_quality_monitor,
)


class TestWasteClassificationLookup:
    """Tests for waste_classification_lookup tool."""

    def test_valid_concrete_code(self):
        result = waste_classification_lookup("17 01 01")
        assert result["found"] is True
        assert result["description"] == "Concrete"
        assert result["hazardous"] is False
        assert result["typical_cost_per_tonne_gbp"] == 45.00

    def test_valid_hazardous_code(self):
        result = waste_classification_lookup("17 03 01")
        assert result["found"] is True
        assert result["hazardous"] is True
        assert result["requires_hazardous_consignment_note"] is True

    def test_invalid_code(self):
        result = waste_classification_lookup("99 99 99")
        assert result["found"] is False
        assert "not found" in result["message"].lower()

    def test_normalization(self):
        result = waste_classification_lookup("  17 01 01  ")
        assert result["found"] is True


class TestSkipHireQuote:
    """Tests for skip_hire_quote tool."""

    def test_valid_quote(self):
        result = skip_hire_quote("CM8 1XY", "mixed construction", 8)
        assert result["error"] is False
        assert result["skip_size_yards"] == 8
        assert result["base_price_gbp"] == 290.00
        assert result["total_price_gbp_per_week"] == 320.00  # base + permit

    def test_hazardous_surcharge(self):
        result = skip_hire_quote("CM8 1XY", "asbestos waste", 8)
        assert result["error"] is False
        assert result["hazardous"] is True
        assert result["hazardous_surcharge_gbp"] == 150.00

    def test_invalid_size(self):
        result = skip_hire_quote("CM8 1XY", "soil", 100)
        assert result["error"] is True
        assert "Invalid skip size" in result["message"]

    def test_postcode_uppercase(self):
        result = skip_hire_quote("cm8 1xy", "garden waste", 6)
        assert result["postcode"] == "CM8 1XY"


class TestGrabLorryBooking:
    """Tests for grab_lorry_booking tool."""

    def test_single_load(self):
        result = grab_lorry_booking("CM8 1XY", "soil", 10.0)
        assert result["error"] is False
        assert result["loads_required"] == 1
        assert result["lorry_capacity_m3"] == 16.0
        assert result["estimated_cost_gbp"] > 0

    def test_multiple_loads(self):
        result = grab_lorry_booking("CM8 1XY", "mixed rubble", 50.0)
        assert result["error"] is False
        assert result["loads_required"] == 4
        assert result["estimated_cost_gbp"] > 0

    def test_zero_volume(self):
        result = grab_lorry_booking("CM8 1XY", "soil", 0)
        assert result["error"] is True
        assert "greater than 0" in result["message"]

    def test_availability_within_range(self):
        result = grab_lorry_booking("CM8 1XY", "soil", 30.0)
        assert result["error"] is False
        assert 2 <= result["availability_days"] <= 5


class TestWasteTransferNote:
    """Tests for waste_transfer_note_generator tool."""

    def test_wtn_generation(self):
        result = waste_transfer_note_generator(
            site="123 Construction Site, Chelmsford, CM1 1AA",
            waste_type="Mixed construction waste",
            carrier="WasteCo Ltd",
            destination="Green Recycling Facility, Basildon",
        )
        assert result["error"] is False
        assert "wtn" in result
        assert "WTN-" in result["wtn"]["wtn_id"]
        assert result["wtn"]["document_type"] == "Waste Transfer Note"
        assert "formatted_text" in result

    def test_wtn_id_format(self):
        result = waste_transfer_note_generator(
            site="Site A",
            waste_type="Soil",
            carrier="Carrier X",
            destination="Facility Y",
        )
        wtn_id = result["wtn"]["wtn_id"]
        assert wtn_id.startswith("WTN-")
        assert len(wtn_id) > 10


class TestDefraComplianceCheck:
    """Tests for defra_compliance_check tool."""

    def test_hazardous_landfill_compliance(self):
        result = defra_compliance_check("hazardous waste", "landfill")
        assert result["compliant"] is False
        assert result["waste_category"] == "hazardous_waste"

    def test_non_hazardous_recycling_compliant(self):
        result = defra_compliance_check("mixed construction", "recycling")
        assert result["compliant"] is True
        assert result["waste_category"] == "non_hazardous_waste"

    def test_inert_waste_landfill(self):
        result = defra_compliance_check("concrete rubble", "landfill")
        assert result["compliant"] is True
        assert result["waste_category"] == "inert_waste"

    def test_hazardous_recycling(self):
        result = defra_compliance_check("hazardous chemicals", "recycling")
        assert result["compliant"] is True
        assert result["requires_carrier_license"] is True

    def test_recommendations_present(self):
        result = defra_compliance_check("soil", "landfill")
        assert len(result["recommendations"]) > 0
        assert "waste hierarchy" in str(result["recommendations"]).lower()


class TestWaterQualityMonitor:
    """Tests for water_quality_monitor tool."""

    def test_optimal_water(self):
        result = water_quality_monitor(ph=7.2, ammonia=0.0, nitrite=0.0, temperature=18.0)
        assert result["error"] is False
        assert result["overall_status"] == "OPTIMAL"
        assert result["fish_health_risk"] == "NO RISK"

    def test_critical_water(self):
        result = water_quality_monitor(ph=9.5, ammonia=0.5, nitrite=0.5, temperature=35.0)
        assert result["error"] is False
        assert result["overall_status"] == "CRITICAL"
        assert "HIGH RISK" in result["fish_health_risk"]

    def test_warning_water(self):
        result = water_quality_monitor(ph=7.8, ammonia=0.015, nitrite=0.05, temperature=20.0)
        assert result["error"] is False
        assert result["overall_status"] == "WARNING"

    def test_parameter_structure(self):
        result = water_quality_monitor(ph=7.0, ammonia=0.01, nitrite=0.05, temperature=15.0)
        params = result["parameters"]
        assert "ph" in params
        assert "ammonia" in params
        assert "nitrite" in params
        assert "temperature" in params
        for param in params.values():
            assert "value" in param
            assert "status" in param
            assert "recommendation" in param

    def test_recommendations_for_critical(self):
        result = water_quality_monitor(ph=9.0, ammonia=0.1, nitrite=0.0, temperature=18.0)
        assert len(result["recommendations"]) > 0
        assert any("pH" in r for r in result["recommendations"])
        assert any("ammonia" in r for r in result["recommendations"])


class TestIntegration:
    """Integration tests combining multiple tools."""

    def test_full_waste_workflow(self):
        """Test a complete waste management workflow."""
        # 1. Classify waste
        classification = waste_classification_lookup("17 01 01")
        assert classification["found"] is True
        assert classification["hazardous"] is False

        # 2. Get skip quote
        quote = skip_hire_quote("CM8 1XY", classification["description"], 8)
        assert quote["error"] is False

        # 3. Check DEFRA compliance
        compliance = defra_compliance_check(classification["description"], "recycling")
        assert compliance["compliant"] is True

        # 4. Generate WTN
        wtn = waste_transfer_note_generator(
            site="Test Site, CM8 1XY",
            waste_type=classification["description"],
            carrier="Test Carrier",
            destination="Test Facility",
        )
        assert wtn["error"] is False

    def test_aquaculture_workflow(self):
        """Test aquaculture monitoring workflow."""
        # Monitor water quality
        result = water_quality_monitor(ph=7.0, ammonia=0.01, nitrite=0.05, temperature=15.0)
        assert result["overall_status"] in ["OPTIMAL", "WARNING"]
        assert len(result["recommendations"]) > 0
