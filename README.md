# determine-github-owner

Intelligently discover contact information for GitHub repository owners using AI.

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

**Required**: Set your GitHub token for API access:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

**Required**: Set your AI provider API key. For OpenAI (default):

```bash
export OPENAI_API_KEY="your_openai_key_here"
```

Or for Anthropic Claude:

```bash
export ANTHROPIC_API_KEY="your_anthropic_key_here"
```

**Optional**: Set NPM token for authenticated NPM registry requests:

```bash
export NPM_TOKEN="your_npm_token_here"
```

### CLI Command

The tool uses an AI agent to intelligently discover the best way to contact a repository owner:

```bash
determine-github-owner https://github.com/iloveitaly/determine-github-owner
```

By default, it uses OpenAI's GPT-4. You can specify a different model:

```bash
# Use Anthropic Claude
determine-github-owner https://github.com/owner/repo --model anthropic:claude-3-5-sonnet-20241022

# Use OpenAI GPT-4
determine-github-owner https://github.com/owner/repo --model openai:gpt-4o
```

## How It Works

The tool:

1. Fetches repository metadata (description, README, language, etc.)
2. Attempts to find the owner's email from their GitHub profile
3. If not found, searches recent commit history for email addresses
4. Passes all this information to an AI agent
5. The AI agent intelligently uses available tools:
   - Query PyPI for Python package author information
   - Query NPM for JavaScript package maintainer information
6. Returns the best contact information found

The AI agent analyzes the repository context and strategically uses the available tools to discover the most relevant contact information.

## Features

- **AI-Powered Discovery**: Uses LLM to intelligently determine the best approach for finding contact info
- **Multiple Data Sources**: GitHub profiles, commit history, PyPI, NPM
- **Flexible Model Support**: Works with OpenAI GPT-4 or Anthropic Claude
- **Tool-Based Architecture**: AI agent can call package registry APIs as needed

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
