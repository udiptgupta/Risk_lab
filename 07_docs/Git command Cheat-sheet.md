# Git Command Cheat Sheet

## ✅ Initial Setup (Run Once per Project)
```bash
# Navigate to project root
cd /d/05_Projects/07_Risk_Lab

# Initialize Git repo (only first time)
git init

# Rename branch to main
git branch -m main

# Add remote origin (only once)
git remote add origin https://github.com/udiptgupta/Risk_lab.git

# Pull README + existing files from GitHub (if repo already has content)
git pull origin main --allow-unrelated-histories

✅ Daily Workflow (Add → Commit → Push)

# 1. Check status
git status

# 2. Pull latest changes (important before committing)
git pull origin main --ff-only

# 3. Stage all changes
git add .

# 4. Commit with a message
git commit -m "Your message here"

# 5. Push to GitHub
git push origin main

✅ Common Fixes

If history diverged (safe rebase)

git pull origin main --rebase
# Resolve conflicts if any, then:
git rebase --continue
git push origin main

If you accidentally committed a folder (e.g., envs/)

git rm -r --cached envs/
git commit -m "Removed envs from tracking"
git push origin main

✅ .gitignore Best Practice
Create a file named .gitignore in the project root with:

# Ignore virtual environments
envs/
venv/
*.env

# Ignore Jupyter checkpoints
.ipynb_checkpoints/

# Ignore raw and large datasets
01_data_raw/*.csv
01_data_raw/*.xlsx
!01_data_raw/sample_*.csv  # keep small samples

# Ignore Excel outputs and temp files
*.xlsx
*.xls
~$*.xls

# Ignore logs, cache
*.log
__pycache__/
.DS_Store

✅ Quick Summary

git add .
git commit -m "Update message"
git push origin main

Tip: Always run these from Git Bash inside the project root:
/d/05_Projects/07_Risk_Lab