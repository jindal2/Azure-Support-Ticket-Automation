"""
Support Ticket Automation System
Summary & Draft Response Generator

Provides lightweight, hallucination-free extractive summarization and
professional category-specific response templates.

SAFETY & COMPLIANCE RULES:
- Never fabricate refunds, credits, or account modifications.
- Never promise specific SLA or resolution timelines.
- Never claim an issue is already resolved before human intervention.
- Never expose internal system infrastructure or stack traces.
- Flag draft as pending review until explicitly approved by an authorized agent.
"""

import re
from typing import Optional


def generate_summary(message: str) -> str:
    """
    Extracts a concise, truthful summary from the customer message.
    Uses clean sentence-level extraction to prevent hallucinating facts.
    """
    if not message or not message.strip():
        return "No message content provided."

    clean = message.strip()

    # Split into sentences based on punctuation or newlines
    sentences = re.split(r"(?<=[.!?])\s+|\n+", clean)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return clean[:120] + ("..." if len(clean) > 120 else "")

    first_sentence = sentences[0]

    # If first sentence is too long, truncate cleanly at word boundary
    if len(first_sentence) > 140:
        words = first_sentence[:137].rsplit(" ", 1)
        return words[0] + "..."

    return first_sentence


def generate_draft_response(
    category: str,
    priority: str,
    message: str,
    is_uncertain: bool = False,
    is_critical: bool = False,
    is_security: bool = False,
    ticket_id: Optional[str] = None
) -> str:
    """
    Generates a polite, compliant draft response tailored to ticket parameters.
    """
    ref_str = f" regarding ticket {ticket_id}" if ticket_id else ""

    # 1. Critical Security Incident Draft
    if is_security:
        return (
            f"Hello,\n\n"
            f"Thank you for contacting Support{ref_str}.\n\n"
            f"We take reported security and access concerns very seriously. Your report has been "
            f"escalated immediately to our Information Security and Identity Support team for a "
            f"thorough investigation.\n\n"
            f"In the meantime, if you suspect your credentials may be compromised, we recommend "
            f"updating your password and reviewing your active login sessions where possible.\n\n"
            f"A support specialist will follow up with you as soon as our security review is complete.\n\n"
            f"Best regards,\n"
            f"Security & Identity Support Team\n"
            f"(Draft pending human approval)"
        )

    # 2. Critical Service Outage Draft
    if is_critical:
        return (
            f"Hello,\n\n"
            f"Thank you for reaching out to Support{ref_str}.\n\n"
            f"We have noted your report concerning service disruption. Our Technical Support and "
            f"Operations teams have been alerted and are investigating the status of the platform.\n\n"
            f"A team member will provide updates directly on this ticket as technical verification proceeds.\n\n"
            f"Thank you for your patience,\n"
            f"Operations & Technical Support\n"
            f"(Draft pending human approval)"
        )

    # 3. Uncertain / Ambiguous Draft
    if is_uncertain:
        return (
            f"Hello,\n\n"
            f"Thank you for reaching out to Support{ref_str}.\n\n"
            f"We have received your request and routed it to our specialized triage team. "
            f"Because your request involves multiple topics, a customer support specialist is currently "
            f"reviewing your ticket details to ensure it is directed to the most appropriate team.\n\n"
            f"We will follow up with you shortly with next steps.\n\n"
            f"Best regards,\n"
            f"Customer Support Team\n"
            f"(Draft pending human approval)"
        )

    # 4. Standard Category Drafts
    if category == "Billing":
        return (
            f"Hello,\n\n"
            f"Thank you for contacting Billing Support{ref_str}.\n\n"
            f"We have received your billing enquiry. Our Billing Operations team is currently reviewing "
            f"your account and recent invoice history. To help us process this promptly, please ensure you "
            f"have provided any relevant invoice numbers or transaction references.\n\n"
            f"A representative will review the account details and reply to you directly.\n\n"
            f"Kind regards,\n"
            f"Billing Support Team\n"
            f"(Draft pending human approval)"
        )

    elif category == "Technical":
        return (
            f"Hello,\n\n"
            f"Thank you for contacting Technical Support{ref_str}.\n\n"
            f"We have logged your technical enquiry. Our engineering support team is investigating the "
            f"behavior described. If you have any additional error messages, screenshots, or browser/system "
            f"details, please reply to this message.\n\n"
            f"A technical support engineer will investigate and respond to assist you.\n\n"
            f"Kind regards,\n"
            f"Technical Support Team\n"
            f"(Draft pending human approval)"
        )

    elif category == "Access":
        return (
            f"Hello,\n\n"
            f"Thank you for contacting Identity and Access Support{ref_str}.\n\n"
            f"We understand you are experiencing an authentication or access issue. Our team is verifying "
            f"your account status to guide you through secure access restoration.\n\n"
            f"Please ensure you have access to your registered primary email address for verification.\n\n"
            f"Kind regards,\n"
            f"Identity & Access Support Team\n"
            f"(Draft pending human approval)"
        )

    else:  # General
        return (
            f"Hello,\n\n"
            f"Thank you for contacting Customer Support{ref_str}.\n\n"
            f"We have received your enquiry. A member of our customer care team is reviewing your question "
            f"and will provide you with the requested information shortly.\n\n"
            f"In the meantime, feel free to visit our online documentation center for product guides and FAQs.\n\n"
            f"Kind regards,\n"
            f"Customer Care Team\n"
            f"(Draft pending human approval)"
        )
