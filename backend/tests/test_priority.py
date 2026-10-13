"""
Test Priority Rules & Team Assignment
"""

from app.priority_service import (
    PriorityService,
    evaluate_ticket_priority_and_team,
    PRIORITY_CRITICAL,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
    TEAM_BILLING,
    TEAM_TECHNICAL,
    TEAM_ACCESS,
    TEAM_GENERAL
)


def test_widespread_outage_triggers_critical_priority():
    """Validates that widespread system outage patterns deterministically trigger CRITICAL priority."""
    msg = "Urgent: Widespread outage detected. The entire production system is down for all customers."
    prio, team, meta = evaluate_ticket_priority_and_team(msg, "Technical")
    assert prio == PRIORITY_CRITICAL
    assert meta["is_critical_risk"] is True
    assert team == TEAM_TECHNICAL


def test_suspected_security_incident_triggers_critical_flag():
    """Validates that suspected security breaches trigger CRITICAL priority and security flag."""
    msg = "We suspect a security breach: multiple unauthorized logins from an unknown foreign IP."
    prio, team, meta = evaluate_ticket_priority_and_team(msg, "Access")
    assert prio == PRIORITY_CRITICAL
    assert meta["is_suspected_security"] is True
    assert meta["is_critical_risk"] is True
    assert team == TEAM_ACCESS


def test_business_blocker_triggers_high_priority():
    """Validates that essential business operation blockers trigger HIGH priority."""
    msg = "This bug is blocking our business operations and we cannot process payment before month end."
    prio, team, meta = evaluate_ticket_priority_and_team(msg, "Billing")
    assert prio == PRIORITY_HIGH


def test_routine_question_triggers_low_priority():
    """Validates that informational and pricing questions receive LOW priority."""
    msg = "Could you please send me documentation on your pricing plan and tutorial guides?"
    prio, team, meta = evaluate_ticket_priority_and_team(msg, "General")
    assert prio == PRIORITY_LOW
    assert team == TEAM_GENERAL


def test_standard_operational_issue_defaults_to_medium():
    """Validates that standard technical or billing issues default to MEDIUM priority."""
    msg = "The PDF exporter fails when trying to generate weekly invoices."
    prio, team, meta = evaluate_ticket_priority_and_team(msg, "Technical")
    assert prio == PRIORITY_MEDIUM


def test_team_mapping_correctness():
    """Verifies that all 4 categories map to their designated specialized teams."""
    assert PriorityService.assign_team("Billing") == TEAM_BILLING
    assert PriorityService.assign_team("Technical") == TEAM_TECHNICAL
    assert PriorityService.assign_team("Access") == TEAM_ACCESS
    assert PriorityService.assign_team("General") == TEAM_GENERAL
    # Fallback check
    assert PriorityService.assign_team("NonExistentCategory") == TEAM_GENERAL
