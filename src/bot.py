import os
import requests
import google.generativeai as genai

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_pr_diff(repo, pr_number):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    files = response.json()
    
    diff_text = ""
    for file in files:
        diff_text += f"\nFile: {file['filename']}\n"
        diff_text += file.get("patch", "No changes")
    return diff_text

def review_with_gemini(diff):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.0-pro")
    prompt = f"""You are an expert code reviewer. Review this PR diff and provide feedback in this format:

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

    response =model.generate_content(prompt)
    return response.text

def post_comment(repo, pr_number, comment):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    body = {"body": comment}
    requests.post(url, headers=headers, json=body)
    print("✅ Review posted successfully!")

if __name__ == "__main__":
    repo = os.environ.get("REPO_NAME")
    pr_number = os.environ.get("PR_NUMBER")
    
    print(f"🔍 Reviewing PR #{pr_number} in {repo}...")
    diff = get_pr_diff(repo, pr_number)
    review = review_with_gemini(diff)
    post_comment(repo, pr_number, review)