import requests

token = "YOUR_GITHUB_TOKEN_HERE"
repo = "JananiNaidu/ai-pr-reviewer"
pr_number = 1

comment = """## 🤖 AI Code Review

### ✅ What looks good
- Clean and readable code structure
- Good use of functions and separation of concerns
- Consistent naming conventions followed throughout

### 🐛 Bugs & Issues
- Missing error handling for edge cases
- Potential null reference if API returns empty response

### 🔒 Security Concerns
- API key should be moved to environment variables
- Add input validation on user-provided parameters

### 💡 Improvements
- Add unit tests for core functions
- Consider using async/await for better performance
- Add logging for easier debugging

### 📊 Overall Rating
**8/10** - Clean and well structured code! Ready for production with minor improvements."""

url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
response = requests.post(url, headers=headers, json={"body": comment})
print("Done!", response.status_code)