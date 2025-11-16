"""Test determine-github-owner."""

import determine_github_owner


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(determine_github_owner.__name__, str)