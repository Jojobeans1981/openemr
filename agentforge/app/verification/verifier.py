"""Verification system for AgentForge Healthcare AI Agent.

Implements 4 verification types required by PRD:
1. Hallucination Detection - Flag unsupported claims, require source attribution
2. Confidence Scoring - Quantify certainty, surface low-confidence responses
3. Domain Constraints - Enforce business rules (drug dosage limits, emergency escalation)
4. Output Validation - Schema validation, format checking, completeness
"""

import logging
import re

logger = logging.getLogger(__name__)

MEDICAL_DISCLAIMER = (
    "\n\n---\n"
    "**Disclaimer:** This information is for educational purposes only and does not constitute medical advice. "
    "Always consult a qualified healthcare professional for personalized medical guidance."
)

# Keywords indicating high-severity interactions that need escalation
HIGH_SEVERITY_KEYWORDS = [
    "severe",
    "high",
    "contraindicated",
    "life-threatening",
    "fatal",
    "avoid combination",
    "do not use together",
    "black box warning",
    "never combine",
]

# Emergency symptom patterns
EMERGENCY_PATTERNS = [
    r"chest\s+pain",
    r"difficulty\s+breathing",
    r"shortness\s+of\s+breath",
    r"loss\s+of\s+consciousness",
    r"severe\s+bleeding",
    r"stroke",
    r"heart\s+attack",
    r"anaphyla",
    r"suicid",
    r"self.harm",
    r"overdose",
    r"seizure",
    r"can'?t\s+breathe",
    r"unresponsive",
    r"severe\s+allergic",
]

# Hallucination risk patterns - claims that need source backing
UNSUPPORTED_CLAIM_PATTERNS = [
    r"studies\s+show",
    r"research\s+proves",
    r"it\s+is\s+proven",
    r"100%\s+(?:safe|effective)",
    r"guaranteed\s+to",
    r"always\s+(?:cures|works)",
    r"no\s+side\s+effects",
    r"completely\s+harmless",
]

# Forbidden content patterns - things the agent should never say
FORBIDDEN_PATTERNS = [
    r"(?:take|use)\s+\d+\s*(?:mg|ml|tablet|pill|capsule)",  # Specific dosage recommendations
    r"you\s+(?:definitely|certainly)\s+have\s+(?:cancer|diabetes|hiv|aids)",  # Definitive diagnoses
    r"stop\s+taking\s+your\s+(?:medication|medicine|prescription)",  # Advising to stop medication
    r"you\s+don'?t\s+need\s+(?:a\s+)?doctor",  # Discouraging medical consultation
]


class VerificationResult:
    def __init__(self):
        self.has_sources: bool = False
        self.has_disclaimer: bool = False
        self.confidence: float = 0.5
        self.flags: list[str] = []
        self.needs_escalation: bool = False
        self.hallucination_risk: float = 0.0
        self.domain_violations: list[str] = []
        self.output_valid: bool = True
        self.verification_checks: dict[str, bool] = {}

    def to_dict(self) -> dict:
        return {
            "has_sources": self.has_sources,
            "has_disclaimer": self.has_disclaimer,
            "confidence": self.confidence,
            "flags": self.flags,
            "needs_escalation": self.needs_escalation,
            "hallucination_risk": self.hallucination_risk,
            "domain_violations": self.domain_violations,
            "output_valid": self.output_valid,
            "verification_checks": self.verification_checks,
        }


# ===================================================================
# Verification Type 1: Hallucination Detection
# ===================================================================

def _check_hallucination(response: str, tools_used: list[str], result: VerificationResult) -> None:
    """Flag unsupported claims and require source attribution.

    Checks:
    - Response cites sources when tools were used
    - No unsupported absolute claims
    - Medical claims backed by tool data
    """
    response_lower = response.lower()

    # Check for source attribution
    source_patterns = [r"source:", r"according to", r"based on.*data", r"from.*api", r"rxnorm", r"cdc", r"nih", r"fda", r"mayo clinic"]
    for pattern in source_patterns:
        if re.search(pattern, response_lower):
            result.has_sources = True
            break

    if not result.has_sources and tools_used:
        result.flags.append("HALLUCINATION_RISK: Response uses tool data but lacks source attribution")
        result.hallucination_risk += 0.3

    # Check for unsupported absolute claims
    for pattern in UNSUPPORTED_CLAIM_PATTERNS:
        if re.search(pattern, response_lower):
            result.flags.append(f"HALLUCINATION_RISK: Unsupported claim detected (matched: {pattern})")
            result.hallucination_risk += 0.2

    # If no tools were used but response contains specific medical facts, flag it
    if not tools_used and len(response) > 200:
        medical_fact_indicators = [r"\d+\s*mg", r"\d+%\s+(?:risk|chance|probability)", r"fda\s+approved"]
        for pattern in medical_fact_indicators:
            if re.search(pattern, response_lower):
                result.flags.append("HALLUCINATION_RISK: Specific medical claim without tool verification")
                result.hallucination_risk += 0.15

    result.hallucination_risk = min(result.hallucination_risk, 1.0)
    result.verification_checks["hallucination_detection"] = result.hallucination_risk < 0.5


# ===================================================================
# Verification Type 2: Confidence Scoring
# ===================================================================

def _score_confidence(response: str, tools_used: list[str], result: VerificationResult) -> None:
    """Quantify certainty and surface low-confidence responses.

    Score components:
    - Base: 0.3 (raw LLM response)
    - Tool usage: +0.25
    - Source citation: +0.15
    - Disclaimer present: +0.05
    - Multiple tools: +0.1
    - Hallucination risk: -0.2
    - No domain violations: +0.15
    """
    response_lower = response.lower()

    confidence = 0.3  # Base confidence for LLM response

    # Tool usage boosts confidence
    if tools_used:
        confidence += 0.25

    # Source citation
    if result.has_sources:
        confidence += 0.15

    # Disclaimer
    disclaimer_patterns = [r"disclaimer", r"not.*medical\s+advice", r"consult.*healthcare", r"educational\s+purposes"]
    for pattern in disclaimer_patterns:
        if re.search(pattern, response_lower):
            result.has_disclaimer = True
            confidence += 0.05
            break

    # Multiple tools = more thorough
    if len(tools_used) > 1:
        confidence += 0.1

    # Hallucination risk reduces confidence
    confidence -= result.hallucination_risk * 0.2

    # Domain violations reduce confidence
    if result.domain_violations:
        confidence -= 0.15

    result.confidence = max(0.0, min(confidence, 1.0))
    result.verification_checks["confidence_scoring"] = True


# ===================================================================
# Verification Type 3: Domain Constraints
# ===================================================================

def _check_domain_constraints(response: str, query: str, tools_used: list[str], result: VerificationResult) -> None:
    """Enforce healthcare domain business rules.

    Rules:
    - Emergency symptoms must trigger escalation
    - High-severity drug interactions must be flagged
    - No specific dosage recommendations
    - No definitive diagnoses
    - Cannot advise stopping prescribed medication
    """
    response_lower = response.lower()
    query_lower = query.lower()

    # Emergency detection in query
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, query_lower):
            result.needs_escalation = True
            result.flags.append("ESCALATION: Emergency symptoms detected in query")
            break

    # High-severity drug interaction flagging
    if "drug_interaction_check" in tools_used:
        for keyword in HIGH_SEVERITY_KEYWORDS:
            if keyword in response_lower:
                result.needs_escalation = True
                result.flags.append(f"ESCALATION: High-severity drug interaction detected ({keyword})")
                break

    # Check for forbidden content
    for pattern in FORBIDDEN_PATTERNS:
        match = re.search(pattern, response_lower)
        if match:
            violation = f"DOMAIN_VIOLATION: Forbidden content detected: '{match.group()}'"
            result.domain_violations.append(violation)
            result.flags.append(violation)

    # Overdose detection in query
    overdose_patterns = [r"took\s+\d+\s+pills", r"overdose", r"too\s+many\s+pills"]
    for pattern in overdose_patterns:
        if re.search(pattern, query_lower):
            result.needs_escalation = True
            result.flags.append("ESCALATION: Possible overdose detected - immediate escalation required")
            break

    result.verification_checks["domain_constraints"] = len(result.domain_violations) == 0


# ===================================================================
# Verification Type 4: Output Validation
# ===================================================================

def _validate_output(response: str, tools_used: list[str], result: VerificationResult) -> None:
    """Validate response format, completeness, and structure.

    Checks:
    - Response is not empty
    - Response is not excessively long
    - Response contains actionable information
    - Tool responses are included when tools were used
    """
    # Non-empty response
    if not response or len(response.strip()) < 10:
        result.output_valid = False
        result.flags.append("OUTPUT_INVALID: Response is empty or too short")

    # Not excessively long (>10K chars suggests something went wrong)
    if len(response) > 10000:
        result.flags.append("OUTPUT_WARNING: Response exceeds 10K characters")

    # If tools were used, response should reference tool output
    if tools_used and len(response) < 50:
        result.output_valid = False
        result.flags.append("OUTPUT_INVALID: Tools were used but response is too short to include results")

    # Check for common error patterns that indicate tool failure
    error_patterns = [r"error processing", r"tool.*failed", r"exception", r"traceback"]
    for pattern in error_patterns:
        if re.search(pattern, response.lower()):
            result.flags.append("OUTPUT_WARNING: Response may contain error information")

    result.verification_checks["output_validation"] = result.output_valid


# ===================================================================
# Main verification entry point
# ===================================================================

def verify_response(response: str, tools_used: list[str], original_query: str) -> VerificationResult:
    """Run all verification checks on an agent response.

    Implements 4 verification types:
    1. Hallucination Detection - Source attribution, unsupported claim detection
    2. Confidence Scoring - Multi-factor confidence calculation
    3. Domain Constraints - Emergency escalation, forbidden content, dosage limits
    4. Output Validation - Format, completeness, structure checks
    """
    result = VerificationResult()

    # Run all 4 verification types
    _check_hallucination(response, tools_used, result)
    _check_domain_constraints(response, original_query, tools_used, result)
    _validate_output(response, tools_used, result)
    _score_confidence(response, tools_used, result)  # Run last since it uses other results

    return result


def post_process_response(response: str, verification: VerificationResult) -> str:
    """Post-process the agent response based on verification results."""
    processed = response

    # Add escalation notice if needed
    if verification.needs_escalation and "emergency" not in response.lower()[:200]:
        escalation_notice = (
            "\n\n**IMPORTANT:** Based on the information provided, this situation may require "
            "immediate medical attention. Please consult a healthcare professional or call 911 "
            "if you are experiencing a medical emergency."
        )
        processed = escalation_notice + "\n\n" + processed

    # Add low confidence warning
    if verification.confidence < 0.5 and "error" not in response.lower():
        processed += (
            "\n\n**Note:** This response has lower confidence. "
            "Please verify this information with a healthcare professional."
        )

    # Ensure disclaimer is present
    if not verification.has_disclaimer:
        processed += MEDICAL_DISCLAIMER

    return processed
