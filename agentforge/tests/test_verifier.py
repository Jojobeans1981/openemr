"""Isolated unit tests for AgentForge verification system.

Tests hallucination detection, confidence scoring, domain constraints,
and output validation — all without API keys.
"""

import pytest

from app.verification.verifier import (
    EMERGENCY_PATTERNS,
    FORBIDDEN_PATTERNS,
    HIGH_SEVERITY_KEYWORDS,
    UNSUPPORTED_CLAIM_PATTERNS,
    VerificationResult,
    _check_domain_constraints,
    _check_hallucination,
    _score_confidence,
    _validate_output,
    post_process_response,
    verify_response,
)


# ===================================================================
# Hallucination Detection Tests
# ===================================================================


class TestHallucinationDetection:
    def test_source_attribution_detected(self):
        result = VerificationResult()
        _check_hallucination("Based on data from the CDC, this condition...", ["symptom_lookup"], result)
        assert result.has_sources is True

    def test_no_source_with_tools_flags_risk(self):
        result = VerificationResult()
        _check_hallucination("You should take some medicine for that.", ["drug_interaction_check"], result)
        assert result.has_sources is False
        assert result.hallucination_risk > 0

    def test_unsupported_claims_flagged(self):
        result = VerificationResult()
        _check_hallucination("Studies show this is 100% safe and guaranteed to work.", [], result)
        assert result.hallucination_risk > 0
        assert any("HALLUCINATION_RISK" in f for f in result.flags)

    def test_clean_response_no_flags(self):
        result = VerificationResult()
        _check_hallucination("Source: CDC guidelines recommend rest.", ["symptom_lookup"], result)
        assert result.hallucination_risk == 0

    def test_medical_facts_without_tools_flagged(self):
        result = VerificationResult()
        long_response = "You should take 500mg of this drug. " * 20  # >200 chars
        _check_hallucination(long_response, [], result)
        assert result.hallucination_risk > 0

    def test_risk_capped_at_one(self):
        result = VerificationResult()
        response = "Studies show it is proven to be 100% safe and guaranteed to cure you. No side effects."
        _check_hallucination(response, ["drug_interaction_check"], result)
        assert result.hallucination_risk <= 1.0


# ===================================================================
# Confidence Scoring Tests
# ===================================================================


class TestConfidenceScoring:
    def test_base_confidence(self):
        result = VerificationResult()
        _score_confidence("A basic response.", [], result)
        assert result.confidence == pytest.approx(0.3, abs=0.05)

    def test_tools_boost_confidence(self):
        result = VerificationResult()
        result.has_sources = True  # Set by hallucination check
        _score_confidence("Source: FDA data shows...", ["drug_interaction_check"], result)
        assert result.confidence > 0.5

    def test_multiple_tools_higher_confidence(self):
        result = VerificationResult()
        result.has_sources = True
        _score_confidence(
            "Source: Based on data. This is not medical advice.",
            ["drug_interaction_check", "symptom_lookup"],
            result,
        )
        assert result.confidence > 0.7

    def test_hallucination_reduces_confidence(self):
        result = VerificationResult()
        result.hallucination_risk = 0.5
        _score_confidence("Some response.", ["drug_interaction_check"], result)
        high_risk_confidence = result.confidence

        result2 = VerificationResult()
        result2.hallucination_risk = 0.0
        _score_confidence("Some response.", ["drug_interaction_check"], result2)
        low_risk_confidence = result2.confidence

        assert high_risk_confidence < low_risk_confidence

    def test_domain_violations_reduce_confidence(self):
        result = VerificationResult()
        result.domain_violations = ["VIOLATION: something bad"]
        _score_confidence("Some response.", ["drug_interaction_check"], result)
        assert result.confidence < 0.5

    def test_confidence_bounded(self):
        result = VerificationResult()
        result.hallucination_risk = 1.0
        result.domain_violations = ["v1", "v2"]
        _score_confidence("x", [], result)
        assert result.confidence >= 0.0
        assert result.confidence <= 1.0


# ===================================================================
# Domain Constraints Tests
# ===================================================================


class TestDomainConstraints:
    def test_emergency_detection_chest_pain(self):
        result = VerificationResult()
        _check_domain_constraints("", "I have chest pain and difficulty breathing", [], result)
        assert result.needs_escalation is True

    def test_emergency_detection_overdose(self):
        result = VerificationResult()
        _check_domain_constraints("", "I took 20 pills of aspirin", [], result)
        assert result.needs_escalation is True

    def test_emergency_detection_suicidal(self):
        result = VerificationResult()
        _check_domain_constraints("", "I'm having suicidal thoughts", [], result)
        assert result.needs_escalation is True

    def test_no_emergency_normal_query(self):
        result = VerificationResult()
        _check_domain_constraints("", "What is ibuprofen used for?", [], result)
        assert result.needs_escalation is False

    def test_high_severity_drug_interaction_escalation(self):
        result = VerificationResult()
        _check_domain_constraints(
            "Severity: Contraindicated. This is a life-threatening combination.",
            "check interaction",
            ["drug_interaction_check"],
            result,
        )
        assert result.needs_escalation is True

    def test_forbidden_dosage_recommendation(self):
        result = VerificationResult()
        _check_domain_constraints("You should take 500 mg of aspirin daily.", "", [], result)
        assert len(result.domain_violations) > 0

    def test_forbidden_definitive_diagnosis(self):
        result = VerificationResult()
        _check_domain_constraints("You definitely have cancer.", "", [], result)
        assert len(result.domain_violations) > 0

    def test_forbidden_stop_medication(self):
        result = VerificationResult()
        _check_domain_constraints("Stop taking your medication immediately.", "", [], result)
        assert len(result.domain_violations) > 0

    def test_emergency_patterns_are_valid_regex(self):
        import re
        for pattern in EMERGENCY_PATTERNS:
            re.compile(pattern)  # Should not raise

    def test_forbidden_patterns_are_valid_regex(self):
        import re
        for pattern in FORBIDDEN_PATTERNS:
            re.compile(pattern)


# ===================================================================
# Output Validation Tests
# ===================================================================


class TestOutputValidation:
    def test_empty_response_invalid(self):
        result = VerificationResult()
        _validate_output("", [], result)
        assert result.output_valid is False

    def test_short_response_with_tools_invalid(self):
        result = VerificationResult()
        _validate_output("OK", ["drug_interaction_check"], result)
        assert result.output_valid is False

    def test_valid_response(self):
        result = VerificationResult()
        _validate_output("This is a comprehensive response with useful medical information.", [], result)
        assert result.output_valid is True

    def test_error_pattern_flagged(self):
        result = VerificationResult()
        _validate_output("There was an error processing your request. Exception occurred.", [], result)
        assert any("OUTPUT_WARNING" in f for f in result.flags)


# ===================================================================
# Full Verification Pipeline Tests
# ===================================================================


class TestVerifyResponse:
    def test_full_pipeline_good_response(self):
        response = (
            "Based on FDA Drug Safety Database data, warfarin and aspirin have a High severity interaction. "
            "Source: FDA, NIH DailyMed. "
            "Disclaimer: This is not medical advice. Consult a healthcare professional."
        )
        result = verify_response(response, ["drug_interaction_check"], "check warfarin and aspirin interaction")
        assert result.confidence > 0.5
        assert result.has_sources is True
        assert result.output_valid is True

    def test_full_pipeline_emergency_query(self):
        result = verify_response(
            "Please seek immediate medical attention.",
            [],
            "I have severe chest pain and difficulty breathing",
        )
        assert result.needs_escalation is True

    def test_post_process_adds_disclaimer(self):
        result = VerificationResult()
        result.has_disclaimer = False
        processed = post_process_response("Some response without disclaimer.", result)
        assert "Disclaimer" in processed

    def test_post_process_adds_escalation(self):
        result = VerificationResult()
        result.needs_escalation = True
        result.has_disclaimer = True
        processed = post_process_response("Some response about symptoms.", result)
        assert "IMPORTANT" in processed
        assert "911" in processed
