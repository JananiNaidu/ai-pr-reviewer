# 🤖 AI-Powered PR Reviewer

An automated GitHub bot that reviews Pull Requests using Claude AI (Anthropic).
It analyzes code diffs and posts feedback directly as PR comments.

## 🚀 Features
- Automatically triggers on every Pull Request
- Detects bugs, security issues, and code smells
- Posts detailed review comments on the PR
- Powered by Claude AI (claude-sonnet-4-6)

## 🛠️ Tech Stack
- Python
- GitHub Actions
- Anthropic Claude API
- GitHub REST API

## ⚙️ Setup

### 1. Fork or clone this repo
```bash
git clone https://github.com/your-username/ai-pr-reviewer.git
```

### 2. Add GitHub Secrets
Go to your repo → Settings → Secrets → Actions and add:
- `ANTHROPIC_API_KEY` → your Anthropic API key

### 3. Push to GitHub
The bot will automatically run on every new Pull Request!

## 📸 How It Works
1. Developer opens a Pull Request
2. GitHub Action triggers automatically
3. Bot fetches the code diff
4. Claude AI reviews the code
5. Review is posted as a PR comment

## 📄 License
MIT