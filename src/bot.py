import os
import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

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

def review_with_claude(diff):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": f"Review this code diff and give feedback on bugs, security issues, and improvements:\n\n{diff}"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()["content"][0]["text"]

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
    review = review_with_claude(diff)
    post_comment(repo, pr_number, review)