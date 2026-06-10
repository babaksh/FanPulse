# GitHub Setup Guide

## Step 1: Initialize Local Git Repository (Done by Bob)

```bash
git init
git add .
git commit -m "Initial commit: FanPulse - AI-powered World Cup analysis system"
```

## Step 2: Create GitHub Repository (Done by You)

1. Go to [GitHub.com](https://github.com)
2. Click the **"+"** button in top right → **"New repository"**
3. Fill in the details:
   - **Repository name**: `FanPulse`
   - **Description**: `AI-powered World Cup analysis system with VAR explanations and tactical insights`
   - **Visibility**: Public (required for IBM Challenge submission)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## Step 3: Connect Local to GitHub (Done by Bob)

After you create the repository, GitHub will show you a URL like:
```
https://github.com/YOUR_USERNAME/FanPulse.git
```

Copy that URL and provide it to Bob, who will run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/FanPulse.git
git branch -M main
git push -u origin main
```

## Step 4: Verify Upload

Go to your GitHub repository and verify all files are uploaded:
- ✓ README.md with project description
- ✓ src/ folder with all code
- ✓ docs/ folder with documentation
- ✓ data/ folder with processed documents
- ✓ scripts/ folder with test scripts
- ✓ requirements.txt and requirements-llm.txt

## Step 5: Add Topics (Optional but Recommended)

On your GitHub repository page:
1. Click the gear icon next to "About"
2. Add topics: `ai`, `machine-learning`, `world-cup`, `ibm-challenge`, `rag`, `llm`, `python`, `fastapi`
3. Save changes

## Step 6: Enable GitHub Pages (Optional)

If you want to host documentation:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /docs
4. Save

## Authentication Options

### Option 1: HTTPS with Personal Access Token (Recommended)
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

### Option 2: SSH Key
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Use SSH URL: `git@github.com:YOUR_USERNAME/FanPulse.git`

### Option 3: GitHub CLI
```bash
gh auth login
gh repo create FanPulse --public --source=. --remote=origin --push
```

## Troubleshooting

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin YOUR_GITHUB_URL
```

### Error: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Large Files Warning
If you get warnings about large files (>50MB):
```bash
# Add to .gitignore
echo "data/match_data/*.csv" >> .gitignore
git rm --cached data/match_data/*.csv
git commit -m "Remove large CSV files from tracking"
```

## Next Steps After Upload

1. Add repository URL to IBM Challenge submission
2. Ensure repository is public
3. Add comprehensive README with setup instructions
4. Tag a release version: `git tag -a v1.0.0 -m "Initial release for IBM Challenge"`
5. Push tags: `git push origin --tags`