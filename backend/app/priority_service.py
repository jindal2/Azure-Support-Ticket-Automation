"""
Support Ticket Automation System
Priority & Team Assignment Service

Implements deterministic prototype rules for:
1. Priority Determination (CRITICAL, HIGH, MEDIUM, LOW)
2. Support Team Assignment (Billing, Technical, Identity and Access, Customer Support)
3. Safety & Security Guardrails (Critical-risk override, Security incident flag)

NOTE: These are configurable prototype business rules for the project demo,
not hardcoded corporate policy.
"""

import re
from typing import Dict, Any, Tuple


# Configurable priority levels
PRIORITY_CRITICAL = "CRITICAL"
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"

# Configurable team mappings
TEAM_BILLING = "Billing Support"
TEAM_TECHNICAL = "Technical Support"
TEAM_ACCESS = "Identity and Access Support"
TEAM_GENERAL = "Customer Support"

CATEGORY_TO_TEAM_MAP = {
    "Billing": TEAM_BILLING,
    "Technical": TEAM_TECHNICAL,
    "Access": TEAM_ACCESS,
    "General": TEAM_GENERAL,
}

# Regex keywords for deterministic priority assignment
CRITICAL_OUTAGE_PATTERNS = [
    r"\bwidespread\b",
    r"\boutage\b",
    r"\bsystem(?:s)? down\b",
    r"\bproduction down\b",
    r"\ball (?:users|customers|endpoints)\b",
    r"\bcomplete shutdown\b",
    r"\bcatastrophic failure\b",
]

SECURITY_INCIDENT_PATTERNS = [
    r"\bsecurity breach\b",
    r"\bunauthorized (?:access|login|activity)\b",
    r"\bhacked\b",
    r"\bdata leak(?:age)?\b",
    r"\bcredential leak\b",
    r"\bransomware\b",
    r"\bsuspected breach\b",
    r"\bcompromised account\b",
]

HIGH_PRIORITY_PATTERNS = [
    r"\bblocking (?:our|all|my)? ?business\b",
    r"\bcritical blocker\b",
    r"\bcannot process payment\b",
    r"\burgent\b",
    r"\bescalat(?:e|ion)\b",
    r"\bdeadline today\b",
    r"\bproduction blocked\b",
]

LOW_PRIORITY_PATTERNS = [
    r"\bhow to\b",
    r"\bpricing plan\b",
    r"\bfeature request\b",
    r"\bgeneral enquiry\b",
    r"\bgeneral inquiry\b",
    r"\bwebinar\b",
    r"\bdocumentation\b",
    r"\btutorial\b",
    r"\bfeedback\b",
]


class PriorityService:
    """
    Deterministic priority scoring and support team routing service.
    """

    @staticmethod
    def assign_team(category: str) -> str:
        """
        Maps a category to its designated support team.
        Defaults to Customer Support if unknown.
        """
        return CATEGORY_TO_TEAM_MAP.get(category, TEAM_GENERAL)

    @classmethod
    def evaluate_priority(cls, message: str, predicted_category: str) -> Dict[str, Any]:
        """
        Determines priority, checks critical risk overrides, and flags suspected security incidents.

        Returns:
            dict with:
                - priority: str (CRITICAL, HIGH, MEDIUM, LOW)
                - is_critical_risk: bool
                - is_suspected_security: bool
                - priority_reason: str
        """
        if not message:
            return {
                "priority": PRIORITY_LOW,
                "is_critical_risk": False,
                "is_suspected_security": False,
                "priority_reason": "Default low priority for empty input."
            }

        msg_lower = message.lower()

        # Rule 1: Suspected Security Incidents -> Always CRITICAL and flagged for urgent review
        for pat in SECURITY_INCIDENT_PATTERNS:
            if re.search(pat, msg_lower):
                return {
                    "priority": PRIORITY_CRITICAL,
                    "is_critical_risk": True,
                    "is_suspected_security": True,
                    "priority_reason": "Suspected security incident reported in customer message."
                }

        # Rule 2: Explicit Widespread Service Outages / Major Failures -> Always CRITICAL
        for pat in CRITICAL_OUTAGE_PATTERNS:
            if re.search(pat, msg_lower):
                return {
                    "priority": PRIORITY_CRITICAL,
                    "is_critical_risk": True,
                    "is_suspected_security": False,
                    "priority_reason": "Widespread service outage or major system failure reported."
                }

        # Rule 3: High Priority Business Blockers
        for pat in HIGH_PRIORITY_PATTERNS:
            if re.search(pat, msg_lower):
                return {
                    "priority": PRIORITY_HIGH,
                    "is_critical_risk": False,
                    "is_suspected_security": False,
                    "priority_reason": "Critical business blocker or urgent operational delay."
                }

        # Rule 4: Domain-specific defaults
        if predicted_category == "General":
            return {
                "priority": PRIORITY_LOW,
                "is_critical_risk": False,
                "is_suspected_security": False,
                "priority_reason": "Standard general informational request."
            }

        # Check explicit low priority patterns
        for pat in LOW_PRIORITY_PATTERNS:
            if re.search(pat, msg_lower):
                return {
                    "priority": PRIORITY_LOW,
                    "is_critical_risk": False,
                    "is_suspected_security": False,
                    "priority_reason": "Non-blocking informational query."
                }

        # Default for normal Billing, Technical, Access issues that impede work
        return {
            "priority": PRIORITY_MEDIUM,
            "is_critical_risk": False,
            "is_suspected_security": False,
            "priority_reason": "Standard operational ticket affecting user workflow."
        }


# Helper function
def evaluate_ticket_priority_and_team(message: str, category: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Convenience function returning (priority, assigned_team, metadata).
    """
    priority_meta = PriorityService.evaluate_priority(message, category)
    assigned_team = PriorityService.assign_team(category)
    return priority_meta["priority"], assigned_team, priority_meta
