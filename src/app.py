from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

DEMO_REVIEW = """## 🔍 Code Review Summary

### ✅ What looks good
- Clean and readable code structure
- Good use of functions and separation of concerns
- Consistent naming conventions followed throughout

### 🐛 Bugs & Issues
- Missing error handling for edge cases in the main function
- Potential null reference on line 23 if API returns empty response
- Loop condition may cause off-by-one error

### 🔒 Security Concerns
- API key is hardcoded — should be moved to environment variables
- No input validation on user-provided parameters
- Consider adding rate limiting to prevent abuse

### 💡 Improvements
- Add unit tests for core functions
- Consider using async/await for better performance
- Add logging for easier debugging in production
- Break down large functions into smaller, testable units

### 📊 Overall Rating
**7/10** — The code is functional and readable, but needs better error handling, 
security improvements, and test coverage before production deployment."""

def get_pr_diff(repo, pr_number, github_token=None):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, f"GitHub API error: {response.status_code}"
    
    files = response.json()
    diff_text = ""
    for file in files:
        diff_text += f"\nFile: {file['filename']}\n"
        diff_text += file.get("patch", "No changes")
    return diff_text, None

def review_with_claude(diff, api_key):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": f"""You are an expert code reviewer. Review this PR diff and provide feedback in this format:

## 🔍 Code Review Summary

### ✅ What looks good
- List positive aspects

### 🐛 Bugs & Issues
- List any bugs or potential issues

### 🔒 Security Concerns
- List any security issues

### 💡 Improvements
- List suggestions for improvement

### 📊 Overall Rating
Rate the code quality from 1-10 and explain why.

Here is the diff to review:

{diff}"""
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        return None, f"Claude API error: {response.status_code}"
    return response.json()["content"][0]["text"], None

@app.route("/review", methods=["POST"])
def review():
    data = request.json
    repo = data.get("repo")
    pr_number = data.get("pr_number")
    api_key = data.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
    github_token = data.get("github_token") or os.environ.get("GITHUB_TOKEN")

    if not repo or not pr_number:
        return jsonify({"error": "repo and pr_number are required"}), 400

    # Demo mode - no API key needed
    if not api_key:
        return jsonify({
            "review": DEMO_REVIEW,
            "repo": repo,
            "pr_number": pr_number,
            "mode": "demo"
        })

    diff, error = get_pr_diff(repo, pr_number, github_token)
    if error:
        return jsonify({"error": error}), 400

    review, error = review_with_claude(diff, api_key)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"review": review, "repo": repo, "pr_number": pr_number})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "AI PR Reviewer is running!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)