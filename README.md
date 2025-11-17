# determine-github-owner

Find contact information for GitHub repository owners and package maintainers.

## Installation

```bash
uv pip install determine-github-owner
```

Or using pip:

```bash
pip install determine-github-owner
```

## Usage

### Environment Variables

Set your GitHub token for API access:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

Optional: Set NPM token for authenticated NPM registry requests:

```bash
export NPM_TOKEN="your_npm_token_here"
```

### CLI Commands

#### Get Owner Contact Information

Get contact information from a GitHub username or repository URL:

```bash
determine-github-owner owner iloveitaly
determine-github-owner owner https://github.com/iloveitaly/determine-github-owner
```

Include top contributors (those with 5%+ of commits):

```bash
determine-github-owner owner https://github.com/iloveitaly/determine-github-owner --include-contributors
```

#### Get Repository Information

Get detailed repository metadata including README, description, stars, etc:

```bash
determine-github-owner repo https://github.com/iloveitaly/determine-github-owner
```

#### Get PyPI Package Author

Get author contact information from PyPI:

```bash
determine-github-owner pypi requests
```

#### Get NPM Package Maintainers

Get maintainer contact information from NPM:

```bash
determine-github-owner npm express
```

## Features

- Extract owner email from GitHub profile
- Find emails from recent commit history
- Get repository metadata and README content
- Identify top contributors (5%+ contribution threshold)
- Query PyPI package author information
- Query NPM package maintainer contacts
- Support for various GitHub URL formats

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

## License

MIT
