"""
Legacy conversation model aliases.

The official domain is TechnicalCase. This module remains so older imports keep
working while API compatibility is phased out.
"""

from app.models.technical_case import Message, TechnicalCase

Conversation = TechnicalCase

__all__ = ["Conversation", "Message", "TechnicalCase"]
