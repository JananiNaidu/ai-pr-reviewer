from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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
    return diff_text[:3000], None

def review_with_groq(diff, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.1-8b-instant",
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
        return None, f"Groq API error: {response.status_code} - {response.text}"
    return response.json()["choices"][0]["message"]["content"], None

@app.route("/review", methods=["POST"])
def review():
    data = request.json
    repo = data.get("repo")
    pr_number = data.get("pr_number")
    api_key = data.get("api_key") or GROQ_API_KEY
    github_token = data.get("github_token")

    if not repo or not pr_number:
        return jsonify({"error": "repo and pr_number are required"}), 400

    if not api_key:
        return jsonify({
            "review": "## 🤖 Demo Review\n\n### ✅ What looks good\n- Clean code structure\n\n### 📊 Overall Rating\n**Demo mode** - Add a Groq API key for real reviews!",
            "repo": repo,
            "pr_number": pr_number,
            "mode": "demo"
        })

    diff, error = get_pr_diff(repo, pr_number, github_token)
    if error:
        return jsonify({"error": error}), 400

    review, error = review_with_groq(diff, api_key)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"review": review, "repo": repo, "pr_number": pr_number})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)