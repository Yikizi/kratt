# Git Repository Strategy

> **Historical / superseded:** use `docs/GIT_WORKFLOW.md` for current git/process guidance. This file preserves the early repository-strategy plan.

**Updated**: 2025-02-05

## Repository Architecture

### 1. GitLab TalTech (Primary - Development)

**URL**: `git.taltech.ee/[username]/kratt`
**Status**: Active development
**Access**: Private
**Purpose**:
- Primary development repository
- Issue tracking and project management
- Milestones for thesis timeline
- Full history and all data (including sensitive/draft content)
- Collaboration with thesis advisor (Tanel Alumäe)

**Features:**
- ✅ Issues for task tracking
- ✅ Milestones for phases (Phase 1, 2, 3)
- ✅ Wiki for research notes
- ✅ CI/CD for automated testing (optional)
- ✅ Full commit history

### 2. GitHub Private (Backup - Personal Archive)

**URL**: `github.com/[username]/kratt-backup`
**Status**: Mirror of GitLab
**Access**: Private
**Purpose**:
- Long-term personal backup
- Survives after TalTech account expiration
- Alternative access if GitLab unavailable
- Personal reference post-graduation

**Sync Strategy:**
- Manual push after major milestones
- Or automated mirror via CI/CD
- Keep in sync with GitLab main branch

### 3. GitHub Public (Showcase - Future)

**URL**: `github.com/[username]/kratt`
**Status**: Post-thesis release
**Access**: Public (MIT/Apache 2.0)
**Purpose**:
- Open source release
- Community contributions
- Portfolio showcase
- Academic publication reference

**Content (Filtered):**
- ✅ Final wake word models (ONNX, TFLite)
- ✅ Training scripts and methodology
- ✅ Home Assistant add-on
- ✅ Hardware implementation guides
- ✅ Documentation and user guides
- ❌ Raw personal data
- ❌ Thesis drafts
- ❌ Private notes/experiments

---

## Milestone Structure (GitLab)

### Milestone 1: Data Collection (Weeks 1-4)
- [ ] Phase 1 MVP dataset (Neurokõne + author)
- [ ] Data augmentation pipeline
- [ ] Test set preparation
- [ ] Quality validation

### Milestone 2: Model Training (Weeks 5-8)
- [ ] openWakeWord training pipeline
- [ ] microWakeWord conversion
- [ ] Model evaluation (>95% accuracy)
- [ ] Hyperparameter tuning

### Milestone 3: Hardware Deployment (Weeks 9-12)
- [ ] Raspberry Pi implementation
- [ ] ESP32C3 implementation
- [ ] Wyoming protocol integration
- [ ] Local testing

### Milestone 4: Home Assistant Integration (Weeks 13-16)
- [ ] Add-on development
- [ ] Voice pipeline configuration
- [ ] Documentation
- [ ] User testing preparation

### Milestone 5: User Testing (Weeks 17-18)
- [ ] Recruit 20-30 testers
- [ ] Deploy to test users
- [ ] Collect feedback
- [ ] Performance metrics

### Milestone 6: Thesis Writing (Weeks 19-22)
- [ ] Introduction and background
- [ ] Methodology chapter
- [ ] Results and evaluation
- [ ] Conclusions
- [ ] Defense preparation

---

## Issue Labels

**Type:**
- `type:feature` - New functionality
- `type:bug` - Bug fix
- `type:docs` - Documentation
- `type:research` - Research task
- `type:experiment` - Experimental feature

**Priority:**
- `priority:critical` - Blocking thesis progress
- `priority:high` - Important for thesis
- `priority:medium` - Nice to have
- `priority:low` - Future improvement

**Status:**
- `status:todo` - Not started
- `status:in-progress` - Currently working
- `status:blocked` - Waiting on external dependency
- `status:review` - Needs review

**Component:**
- `component:data` - Data collection/processing
- `component:model` - Model training/evaluation
- `component:hardware` - Hardware implementation
- `component:ha` - Home Assistant integration
- `component:thesis` - Thesis writing

---

## Current Git Status

```bash
# Repository: ~/kratt
# Branch: main
# Commits: 5

# Recent commits:
c8236d2 docs: Add comprehensive iterative data collection strategy
e60825c feat: Add Neurokõne API test and access options
8539baf docs: Add formal thesis proposal (Ülesandepüstitus)
efc0226 feat: Migrate wake word scripts to monorepo
efabbd2 docs: Add strategic CLAUDE.md files throughout monorepo
```

---

## Next Steps

### Immediate:
1. ✅ Create GitLab repo at git.taltech.ee
2. ✅ Add remote: `git remote add origin git@git.taltech.ee:[username]/kratt.git`
3. ✅ Push initial commits: `git push -u origin main`
4. ✅ Create initial milestones
5. ✅ Create first issues for Phase 1

### This Week:
1. ✅ Setup GitHub private backup
2. ✅ Add GitHub remote: `git remote add backup git@github.com:[username]/kratt-backup.git`
3. ✅ Push to backup: `git push backup main`
4. ✅ Document workflow in README

### Future (Post-Thesis):
1. ⏳ Prepare public release branch
2. ⏳ Filter sensitive content
3. ⏳ Create public GitHub repo
4. ⏳ Write public README
5. ⏳ Announce release

---

## Workflow

### Daily Development:
```bash
# Make changes
git add .
git commit -m "type(component): description"
git push origin main
```

### Weekly Backup:
```bash
# Sync to GitHub backup
git push backup main
```

### Milestone Completion:
```bash
# Tag milestone
git tag -a v0.1.0-phase1 -m "Phase 1 MVP dataset complete"
git push origin --tags
git push backup --tags
```

---

## Commit Message Convention

Format: `type(component): description`

**Examples:**
- `feat(data): Add Neurokõne sample generation script`
- `fix(model): Fix ONNX export dimension mismatch`
- `docs(thesis): Add methodology chapter draft`
- `test(hardware): Add ESP32 integration tests`
- `chore(deps): Update TensorFlow to 2.15.0`

---

## File Management

### Always Commit:
- Source code (Python, YAML, etc.)
- Documentation (Markdown, LaTeX)
- Configuration files
- Scripts and tools

### Never Commit:
- `data/raw/` - Raw audio files (use .gitignore)
- `models/checkpoints/` - Large model files (use Git LFS or external storage)
- `.venv/` - Virtual environments
- `__pycache__/` - Python cache
- Personal credentials/tokens

### Use Git LFS for:
- Final production models (<100MB)
- Demo audio samples
- Thesis figures (high-res)

---

**Philosophy**: "Version control for code, not data. Document decisions, not just changes."
