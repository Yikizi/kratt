# Git Workflow & Repository Strategy

**Updated**: 2025-02-05

## Overview

Projekt "Kratt" koosneb kahest faasist:
1. **iaib-proto** - seminari töö (30h, uurimisetapp) ✅ valmis
2. **kratt monorepo** - bakalaureuse töö (täismahus implementation)

---

## Repository Structure

```
GitHub Private (PRIMARY)
├── github.com/mattiaslinholm/kratt (private)
│   ├── wake-word/              # Phase 1: Wake word model
│   ├── hardware/               # ESP32, Raspberry Pi
│   ├── docs/                   # Documentation
│   ├── home-assistant/         # HA integration
│   └── external-repos/
│       └── iaib-proto/         # Reference to old work
│           └── → GitLab link (not submodule, just reference)

GitLab TalTech (ARCHIVE)
├── gitlab.cs.taltech.ee/malinh/iaib
│   ├── experiments/            # Early prototypes (Whisper, etc)
│   ├── docs/                   # 30h research documentation
│   └── scripts/                # Time tracking scripts
│   └── → Read-only archive of seminari work

GitHub Public (FUTURE)
└── github.com/mattiaslinholm/kratt (public)
    ├── models/                 # Final trained models
    ├── hardware/               # Implementation guides
    ├── home-assistant/         # Add-on
    └── docs/                   # User documentation
    └── → Filtered, safe, presentable version
```

---

## Workflow

### Current Development (kratt monorepo):

```bash
# Work in kratt monorepo
cd ~/kratt
git add .
git commit -m "feat(wake-word): add Phase 1 dataset generation"
git push origin main
```

**Primary remote**: GitHub Private (`github.com/mattiaslinholm/kratt`)

### Referencing iaib-proto:

**Option 1: Keep as external reference (RECOMMENDED)**
```bash
# iaib-proto stays in external-repos/ as historical reference
# Update it occasionally from GitLab
cd ~/kratt/external-repos/iaib-proto
git pull origin main
cd ~/kratt
git add external-repos/iaib-proto  # track as regular directory
git commit -m "docs: sync iaib-proto reference"
```

**Option 2: Git submodule (if frequent updates needed)**
```bash
# Convert to submodule (only if you update iaib actively)
cd ~/kratt
rm -rf external-repos/iaib-proto
git submodule add https://gitlab.cs.taltech.ee/malinh/iaib.git external-repos/iaib-proto
git commit -m "docs: add iaib-proto as submodule"
```

**Recommendation**: Keep as regular directory (Option 1) since iaib-proto is mostly finished and won't change much.

---

## Setup Instructions

### 1. Initialize kratt GitHub Private

```bash
cd ~/kratt

# Check current status
git status
git remote -v

# Add GitHub private remote
git remote add origin git@github.com:mattiaslinholm/kratt.git

# Push existing commits
git push -u origin main

# Push tags
git tag -a v0.1.0-phase1 -m "Phase 1: Neurokõne dataset complete (1800 samples)"
git push origin --tags
```

### 2. Keep iaib-proto as reference

```bash
cd ~/kratt/external-repos/iaib-proto

# Verify GitLab connection
git remote -v
# Should show: gitlab.cs.taltech.ee/malinh/iaib.git

# Pull latest (if needed)
git pull origin main

# Document in main repo
cd ~/kratt
echo "See external-repos/iaib-proto/README.md for early research phase" >> README.md
git add README.md external-repos/iaib-proto
git commit -m "docs: add reference to iaib-proto seminari work"
git push origin main
```

### 3. Future: GitHub Public Release

```bash
# When thesis is complete and ready for public release

# Create filtered branch
cd ~/kratt
git checkout -b public-release

# Remove sensitive files
rm -rf data/raw/           # Personal voice recordings
rm -rf docs/thesis/drafts/  # Thesis drafts
rm -rf external-repos/iaib-proto/  # Private seminari work
# ... filter other sensitive content

# Update README for public audience
# Add LICENSE (MIT or Apache 2.0)
# Add CITATION.cff

git add .
git commit -m "prepare: public release (filtered)"

# Create new public repo on GitHub
git remote add public git@github.com:mattiaslinholm/kratt.git
git push public public-release:main
```

---

## .gitignore Strategy

```gitignore
# Data (never commit raw audio)
data/raw/
data/processed/*.wav
!data/processed/README.md

# Models (large files - use Git LFS if needed)
models/checkpoints/
*.ckpt
*.pth
!models/production/*.onnx  # Production models OK (if <100MB)

# Virtual environments
.venv/
venv/
__pycache__/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Sensitive
*.env
secrets.yaml
**/secrets.yaml
credentials/

# Thesis drafts (commit only finals)
docs/thesis/drafts/
```

---

## Commit Message Convention

```
type(scope): description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Testing
- chore: Maintenance

Scopes:
- wake-word: Wake word detection
- hardware: Hardware implementations
- ha: Home Assistant
- thesis: Thesis writing
- docs: Documentation

Examples:
feat(wake-word): add Neurokõne dataset generation
fix(hardware): correct ESP32 I2S pin mapping
docs(thesis): add methodology chapter draft
test(wake-word): add model accuracy tests
```

---

## Branching Strategy

### Main Branch (default):
```bash
# Direct commits for thesis development
git checkout main
# ... work ...
git commit -m "feat: description"
git push origin main
```

### Feature Branches (optional, for experiments):
```bash
# For risky experiments
git checkout -b experiment/multi-wake-word
# ... experiment ...
git commit -m "experiment: test multiple wake words"

# If successful, merge
git checkout main
git merge experiment/multi-wake-word
git push origin main

# If failed, just delete
git branch -D experiment/multi-wake-word
```

### No complicated branching needed for thesis work!

---

## Milestones & Tags

### Tag Convention:
```
v0.1.0-phase1    # Phase 1 complete (data)
v0.2.0-phase2    # Phase 2 complete (training)
v0.3.0-phase3    # Phase 3 complete (deployment)
v1.0.0-thesis    # Thesis defense version
v1.1.0-release   # Public release
```

### GitHub Milestones:
- Phase 1: Data Collection ✅
- Phase 2: Model Training
- Phase 3: Hardware Deployment
- Phase 4: HA Integration
- Phase 5: User Testing
- Phase 6: Thesis Writing

---

## Thesis Advisor Collaboration

**Tanel Alumäe** võib vaadata:
- GitLab iaib repo (seal on Issues koos time tracking'uga)
- GitHub kratt repo (kui ta tahab näha koodi)

**Sharing:**
```bash
# Give Tanel read access to GitHub private repo
# Settings → Collaborators → Add: tanel.alumae@taltech.ee
```

Või:
```bash
# Keep using GitLab iaib for advisor communication
# Push thesis updates there occasionally
cd ~/kratt/external-repos/iaib-proto
# ... add thesis progress docs ...
git add .
git commit -m "docs: thesis progress update"
git push origin main
```

---

## Summary

**Simple Strategy:**
1. ✅ **kratt (GitHub Private)** = primary development (PUSH HERE)
2. 📚 **iaib-proto (GitLab)** = historical reference (READ-ONLY archive)
3. 🌍 **kratt-public (GitHub)** = future open source (AFTER THESIS)

**No complex submodules needed!** Just reference iaib-proto as external-repos/ directory.

---

**Next Action:**
```bash
cd ~/kratt
git remote add origin git@github.com:mattiaslinholm/kratt.git
git push -u origin main
```
