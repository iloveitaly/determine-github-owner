"""Test data models."""

from determine_github_owner.models import ContactInfo


def test_contact_info_with_name():
    """Test ContactInfo with name and email."""
    contact = ContactInfo(name="John Doe", email="john@example.com")
    assert contact.name == "John Doe"
    assert contact.email == "john@example.com"


def test_contact_info_email_only():
    """Test ContactInfo with email only."""
    contact = ContactInfo(email="john@example.com")
    assert contact.name is None
    assert contact.email == "john@example.com"
