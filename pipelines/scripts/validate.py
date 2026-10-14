"""Repo policy checks that run on every PR. Exit non-zero on violations."""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = ROOT / "workspace"
PARAM = WORKSPACE / "parameter.yml"
REQUIRED_ENVS = {"TEST", "PROD"}

# Baseline only. Add a dedicated scanner (gitleaks, trufflehog) for real coverage.
SECRET_PATTERNS = [
    r"client_secret\s*[=:]\s*\S+",
    r"AccountKey=[A-Za-z0-9+/=]{20,}",
    r"password\s*[=:]\s*['\"]?\S+",
    r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
]
TEXT_SUFFIXES = {".py", ".json", ".yml", ".yaml", ".sql", ".txt", ".md", ".ipynb", ".platform"}

errors: list[str] = []


def check_parameter_file() -> None:
    if not PARAM.exists():
        errors.append("workspace/parameter.yml is missing")
        return
    data = yaml.safe_load(PARAM.read_text()) or {}
    for section, rules in data.items():
        for i, rule in enumerate(rules or []):
            replace = rule.get("replace_value", {})
            missing = REQUIRED_ENVS - set(replace)
            if missing:
                errors.append(f"parameter.yml {section}[{i}] missing environments: {sorted(missing)}")
            for env, val in replace.items():
                if isinstance(val, str) and val.startswith("<"):
                    errors.append(f"parameter.yml {section}[{i}] {env} still has a placeholder value")


def check_items_present() -> None:
    items = [p for p in WORKSPACE.iterdir() if p.is_dir()] if WORKSPACE.exists() else []
    if not items:
        errors.append("workspace/ has no item folders. Sync your Dev workspace to this repo first")


def check_secrets() -> None:
    for path in WORKSPACE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(errors="ignore")
        for pat in SECRET_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                errors.append(f"possible secret in {path.relative_to(ROOT)} (pattern: {pat})")


def main() -> int:
    check_parameter_file()
    check_items_present()
    check_secrets()
    for e in errors:
        print(f"POLICY VIOLATION: {e}")
    if not errors:
        print("All policy checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())