"""Test package manager functions."""

from determine_github_owner.package_managers import (
    extract_email_from_name_and_email_string,
)


def test_extract_email_from_name_and_email_string_with_name():
    """Test extracting name and email from formatted string."""
    name, email = extract_email_from_name_and_email_string(
        "John Doe <john@example.com>"
    )
    assert name == "John Doe"
    assert email == "john@example.com"


def test_extract_email_from_name_and_email_string_email_only():
    """Test extracting email when only email is provided."""
    name, email = extract_email_from_name_and_email_string("john@example.com")
    assert name == ""
    assert email == "john@example.com"


def test_extract_email_from_name_and_email_string_empty():
    """Test extracting from empty string."""
    name, email = extract_email_from_name_and_email_string("")
    assert name == ""
    assert email == ""
