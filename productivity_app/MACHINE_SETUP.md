# Machine Setup

## Quick Setup

```bash
# Clone and setup
git clone <repository-url>
cd productivity_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .

# Run
python run.py
```

## Custom AppData Folder (Optional)

```bash
copy productivity_app\app\core\local_config.example.py productivity_app\app\core\local_config.py
# Edit local_config.py with your APPDATA_ROOT_FOLDER
```

## Git Strategy (One-Way Transfer: M1 → M2, Both Developing)

**Machine 1** - Push features to GitHub:
```bash
# Develop feature A
git add .
git commit -m "feature: A description"
git push origin main
```

**Machine 2** - Pull M1's work and merge with local work:
```bash
# Before pulling: commit your M2 work
git add .
git commit -m "feature: B description"

# Pull and merge M1's features
git pull origin main  # Auto-merges if no conflicts

# If conflicts occur:
# 1. Fix conflicts in files
# 2. git add <resolved-files>
# 3. git commit -m "merge: integrated M1 changes"

# Continue working on M2
git add .
git commit -m "feature: C description"
```

**Workflow Summary**:
- M1 works on features → commits → pushes
- M2 works on features → commits locally → pulls from M1 → merges → continues
- M2 accumulates all work (M1 + M2)
- Handle merge conflicts on M2 as they arise
- M2 is the final, complete codebase
