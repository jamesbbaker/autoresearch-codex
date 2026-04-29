# Autoresearch Privacy Policy

Autoresearch is an MCP app for running KPI-focused improvement loops.

## Data processed

Autoresearch processes the KPI profile, KPI snapshot values, guardrails, iteration notes, experiment hypotheses, experiment outcomes, feedback, shortcomings, and next-bet notes that a user provides while using the app.

## Data storage

The current reference implementation stores app state in local JSON files under `data/` on the deployed server. If deployed publicly, the deployer is responsible for securing the server, limiting access as needed, and replacing local JSON storage with appropriate durable storage before multi-user production use.

## Data sharing

Autoresearch does not intentionally sell data or share data with third parties. Data may be processed by the hosting provider used to run the deployed MCP server and by OpenAI when the app is used through ChatGPT or Codex.

## Sensitive data

Do not enter passwords, API keys, payment details, protected health information, or other secrets into Autoresearch KPI fields or experiment notes.

## Contact

For questions, contact the repository maintainer through:

```text
https://github.com/jamesbbaker/autoresearch-codex
```
