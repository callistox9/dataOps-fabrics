### pre-commit is a developer friendly feedback loop. Git can run a script automatically just before it records a commit. That script is a git hook, and it lives in .git/hooks/pre-commit. If the script fails, the commit is cancelled and you see the errors.

```
pip install pre-commit
pre-commit install            # Run in the repo terminal. Creates the git hook in this repo.
pre-commit run --all-files    checks pre-comit configs that checks everything already in the repo.
```
### .pre-commit-config.yaml at the repo root
```
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
        exclude: ^pipelines/    
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ["--maxkb=500"]
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  # Your own repo policy checks run as a local hook
  - repo: local
    hooks:
      - id: repo-policy
        name: Repo policy checks
        entry: python scripts/validate.py
        language: system
        pass_filenames: false
```
### To by-pass these check
```
git commit --no-verify
```