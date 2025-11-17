"""Test GitHub repository functions."""

import pytest
from determine_github_owner.repo import parse_github_url


def test_parse_github_url_with_full_url():
    """Test parsing full GitHub URL."""
    owner, repo = parse_github_url("https://github.com/iloveitaly/determine-github-owner")
    assert owner == "iloveitaly"
    assert repo == "determine-github-owner"


def test_parse_github_url_with_username_only():
    """Test parsing username only."""
    owner, repo = parse_github_url("iloveitaly")
    assert owner == "iloveitaly"
    assert repo is None


def test_parse_github_url_with_github_prefix():
    """Test parsing with github.com prefix."""
    owner, repo = parse_github_url("github.com/iloveitaly/determine-github-owner")
    assert owner == "iloveitaly"
    assert repo == "determine-github-owner"


def test_parse_github_url_with_path():
    """Test parsing URL with additional path."""
    owner, repo = parse_github_url("github.com/iloveitaly/determine-github-owner/issues")
    assert owner == "iloveitaly"
    assert repo == "determine-github-owner"
