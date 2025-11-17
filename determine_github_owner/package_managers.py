"""
Package manager contact information retrieval.

Originally extracted from these bash functions:

$ npm_email="$(http GET "https://registry.npmjs.org/-/user/org.couchdb.user:$github_user" | jq -r '.email | select( . != null )')"
$ http https://pypi.org/pypi/$project_name/json | jq -r '.info.author_email'
"""

import re
import os
from pydantic import BaseModel
from structlog_config import configure_logger

from determine_github_owner.models import ContactInfo

log = configure_logger()


def extract_email_from_name_and_email_string(author_info: str) -> tuple[str, str]:
    """
    Extract name and email from email string like:
    Melnor Customer Service <mcustomer@melnor.com>.
    """
    if author_info:
        match = re.match(r"(.*?)\s*<(.+?)>", author_info)
        if match:
            return match.group(1).strip(), match.group(2).strip()

    return "", author_info.strip()


def _make_npm_request(url: str) -> dict:
    """Make authenticated request to NPM registry."""
    import requests

    npm_token = os.environ.get("NPM_TOKEN", "")
    headers = {"Authorization": f"Bearer {npm_token}"} if npm_token else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return {}


def get_npm_package_info(package_name: str) -> dict:
    """
    Get package metadata from NPM registry. Here's an example response.

    {'_id': 'lunch-money',
     'name': 'lunch-money',
     'dist-tags': {'latest': '0.5.0'},
     'versions': {'0.5.0': {'name': 'lunch-money',
       'version': '0.5.0',
       'author': {'name': 'Joe Hoyle'},
       'contributors': [{'name': 'Michael Bianco',
         'email': 'mike@mikebian.co',
         'url': 'https://mikebian.co/about'}],
       'maintainers': [{'name': 'joehoyle', 'email': 'joehoyle@gmail.com'},
        {'name': 'iloveitaly', 'email': 'mike@mikebian.co'}]}},
     'maintainers': [{'email': 'joehoyle@gmail.com', 'name': 'joehoyle'},
      {'email': 'lunchbag@gmail.com', 'name': 'lunchbag'},
      {'email': 'mike@mikebian.co', 'name': 'iloveitaly'}],
     'author': {'name': 'Joe Hoyle'},
     'contributors': [{'name': 'Michael Bianco',
       'email': 'mike@mikebian.co',
       'url': 'https://mikebian.co/about'}]}
    """
    url = f"https://registry.npmjs.org/{package_name}"
    return _make_npm_request(url)


def get_npm_contact_info(github_user: str) -> str:
    """Extract contact email from NPM registry for a given GitHub user."""
    url = f"https://registry.npmjs.org/-/user/org.couchdb.user:{github_user}"
    data = _make_npm_request(url)

    return data.get("email", "")


def get_npm_contact_information_from_npm_package(
    package_name: str,
) -> list[ContactInfo]:
    """
    Extract contact email from NPM registry for a given package.

    Args:
        package_name: Name of the npm package
    """
    log.info("npm package request", package_name=package_name)

    package_info = get_npm_package_info(package_name)

    contributors = package_info.get("contributors", [])
    maintainers = package_info.get("maintainers", [])
    author = package_info.get("author", {})

    contact_list = []

    for contributor in contributors + maintainers:
        if email := contributor.get("email", ""):
            contact_list.append(ContactInfo(email=email))

    if author_email := author.get("email", ""):
        contact_list.append(ContactInfo(email=author_email))

    return contact_list


class PypiPackageResponse(BaseModel):
    """Pypi package contact information."""

    package_name: str
    author_name: str
    author_email: str


def get_pypi_contact_info(project_name: str) -> PypiPackageResponse:
    """
    Extract author email from PyPI registry for a given project.

    Args:
        project_name: Name of the pypi project
    """
    log.info("pypi package request", project_name=project_name)

    import requests

    url = f"https://pypi.org/pypi/{project_name}/json"
    response = requests.get(url)
    response.raise_for_status()

    if response.status_code == 200:
        data = response.json()
        author_info = data.get("info", {}).get("author_email", "")
        name, email = extract_email_from_name_and_email_string(author_info)
        return PypiPackageResponse(
            package_name=project_name,
            author_name=name,
            author_email=email,
        )
    else:
        raise ValueError(f"Failed to fetch package info for {project_name}")


def get_npm_package_contacts(package_name: str) -> list[dict[str, str]]:
    """Get contacts from NPM package maintainers."""
    data = get_npm_package_info(package_name)
    maintainers = data.get("maintainers", [])
    contacts = []
    for maint in maintainers:
        name = maint.get("name", "")
        email = maint.get("email", "")
        if email:
            contacts.append({"email": email, "name": name})
    return contacts
