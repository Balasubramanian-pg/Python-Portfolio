#!/usr/bin/env python3
"""
Sprint Generator

A production-hardened automation script that:
- Reads README.md files from top-level project folders in a GitHub repo
- Uses Gemini to generate a sprint plan
- Validates and repairs JSON output
- Writes a project README, sprint folders, mini-sprint markdown files, and metadata
- Uses GitHub Git Data API for batch commits
- Creates a branch per project and optionally opens a pull request
- Supports retries, rate-limit handling, concurrency, and dry-run mode
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import requests

APP_NAME = "sprint-generator"
APP_VERSION = "2.0.0"

DEFAULT_GITHUB_API = "https://api.github.com"
DEFAULT_GEMINI_API = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
DEFAULT_SKIP_FOLDERS = {".github", "assets", "images", "docs", ".git", ".sprint-generator"}

LOGGER = logging.getLogger(APP_NAME)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_dotenv_file(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return
    for raw_line in p.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def slugify(value: str, fallback: str = "untitled") -> str:
    value = value.strip().replace("_", "-")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def escape_md_cell(value: str) -> str:
    return str(value).replace("|", r"\|")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def extract_json_object(text: str) -> Optional[str]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start:end + 1]
    return None


def read_text_safely(text: str, limit: int) -> str:
    return text[:limit] if len(text) > limit else text


def is_retryable_status(status_code: int) -> bool:
    return status_code in {408, 425, 429, 500, 502, 503, 504}


def parse_retry_after(headers: Dict[str, str]) -> Optional[float]:
    retry_after = headers.get("Retry-After")
    if not retry_after:
        return None
    try:
        return float(retry_after)
    except Exception:
        return None


def sleep_backoff(attempt: int, base_delay: float, max_delay: float) -> None:
    delay = min(max_delay, base_delay * (2 ** max(0, attempt - 1)))
    time.sleep(delay)


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    *,
    retry: "RetryConfig",
    logger: logging.Logger,
    **kwargs: Any,
) -> requests.Response:
    last_exc: Optional[Exception] = None
    timeout = kwargs.pop("timeout", retry.timeout_seconds)
    for attempt in range(1, retry.attempts + 1):
        try:
            resp = session.request(method, url, timeout=timeout, **kwargs)
            if 200 <= resp.status_code < 300:
                return resp
            if is_retryable_status(resp.status_code):
                ra = parse_retry_after(resp.headers)
                if ra is not None:
                    logger.warning("Retryable HTTP %s for %s %s, waiting %.1fs", resp.status_code, method, url, ra)
                    time.sleep(ra)
                else:
                    logger.warning("Retryable HTTP %s for %s %s, attempt %s/%s", resp.status_code, method, url, attempt, retry.attempts)
                    sleep_backoff(attempt, retry.base_delay_seconds, retry.max_delay_seconds)
                continue
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            logger.warning("Request error for %s %s on attempt %s/%s: %s", method, url, attempt, retry.attempts, exc)
            if attempt < retry.attempts:
                sleep_backoff(attempt, retry.base_delay_seconds, retry.max_delay_seconds)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"Request failed for {method} {url}")


def parse_readme_headings(readme_text: str) -> List[str]:
    headings: List[str] = []
    for line in readme_text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            heading = re.sub(r"^#+\s*", "", line).strip()
            if heading:
                headings.append(heading)
    return headings


# -----------------------------------------------------------------------------
# Data models
# -----------------------------------------------------------------------------

@dataclass
class MiniSprint:
    mini_sprint_id: str
    mini_sprint_name: str
    description: str
    deliverable: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MiniSprint":
        return MiniSprint(
            mini_sprint_id=str(data.get("mini_sprint_id", "")).strip(),
            mini_sprint_name=str(data.get("mini_sprint_name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            deliverable=str(data.get("deliverable", "")).strip(),
        )

    def is_valid(self) -> bool:
        return bool(self.mini_sprint_id and self.mini_sprint_name and self.description and self.deliverable)


@dataclass
class Sprint:
    sprint_number: int
    sprint_name: str
    sprint_objective: str
    mini_sprints: List[MiniSprint]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Sprint":
        mini_sprints = [
            MiniSprint.from_dict(ms)
            for ms in data.get("mini_sprints", [])
            if isinstance(ms, dict)
        ]
        return Sprint(
            sprint_number=safe_int(data.get("sprint_number", 0)),
            sprint_name=str(data.get("sprint_name", "")).strip(),
            sprint_objective=str(data.get("sprint_objective", "")).strip(),
            mini_sprints=mini_sprints,
        )


@dataclass
class SprintPlan:
    project_title: str
    project_summary: str
    sprints: List[Sprint]
    source_readme_sha256: str = ""
    generated_at: str = ""
    model: str = ""
    generator_version: str = APP_VERSION

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SprintPlan":
        sprints = [
            Sprint.from_dict(s)
            for s in data.get("sprints", [])
            if isinstance(s, dict)
        ]
        return SprintPlan(
            project_title=str(data.get("project_title", "")).strip(),
            project_summary=str(data.get("project_summary", "")).strip(),
            sprints=sprints,
            source_readme_sha256=str(data.get("source_readme_sha256", "")).strip(),
            generated_at=str(data.get("generated_at", "")).strip(),
            model=str(data.get("model", "")).strip(),
            generator_version=str(data.get("generator_version", APP_VERSION)).strip() or APP_VERSION,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_title": self.project_title,
            "project_summary": self.project_summary,
            "source_readme_sha256": self.source_readme_sha256,
            "generated_at": self.generated_at,
            "model": self.model,
            "generator_version": self.generator_version,
            "sprints": [
                {
                    "sprint_number": sprint.sprint_number,
                    "sprint_name": sprint.sprint_name,
                    "sprint_objective": sprint.sprint_objective,
                    "mini_sprints": [dataclasses.asdict(ms) for ms in sprint.mini_sprints],
                }
                for sprint in self.sprints
            ],
        }

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.project_title:
            errors.append("project_title missing")
        if not self.project_summary:
            errors.append("project_summary missing")
        if not self.sprints:
            errors.append("sprints missing")
            return errors
        if not (5 <= len(self.sprints) <= 12):
            errors.append(f"sprints count out of range: {len(self.sprints)}")
        sprint_numbers = set()
        for sprint in self.sprints:
            if sprint.sprint_number in sprint_numbers:
                errors.append(f"duplicate sprint_number: {sprint.sprint_number}")
            sprint_numbers.add(sprint.sprint_number)
            if not sprint.sprint_name:
                errors.append(f"sprint {sprint.sprint_number} missing name")
            if not sprint.sprint_objective:
                errors.append(f"sprint {sprint.sprint_number} missing objective")
            if not (2 <= len(sprint.mini_sprints) <= 5):
                errors.append(f"sprint {sprint.sprint_number} mini_sprints count out of range: {len(sprint.mini_sprints)}")
            for ms in sprint.mini_sprints:
                if not ms.is_valid():
                    errors.append(f"sprint {sprint.sprint_number} has invalid mini sprint")
        return errors

    def normalized(self) -> "SprintPlan":
        cleaned_sprints: List[Sprint] = []
        for sprint in sorted(self.sprints, key=lambda s: s.sprint_number):
            sprint_name = slugify(sprint.sprint_name)
            mini_sprints: List[MiniSprint] = []
            for idx, ms in enumerate(sprint.mini_sprints[:5], start=1):
                mini_sprints.append(
                    MiniSprint(
                        mini_sprint_id=ms.mini_sprint_id.strip() or f"{sprint.sprint_number}.{idx}",
                        mini_sprint_name=slugify(ms.mini_sprint_name),
                        description=ms.description.strip(),
                        deliverable=ms.deliverable.strip(),
                    )
                )
            while len(mini_sprints) < 2:
                idx = len(mini_sprints) + 1
                mini_sprints.append(
                    MiniSprint(
                        mini_sprint_id=f"{sprint.sprint_number}.{idx}",
                        mini_sprint_name=slugify(f"workstream-{idx}"),
                        description="Define and complete the workstream details.",
                        deliverable="Documented implementation notes and task checklist.",
                    )
                )
            cleaned_sprints.append(
                Sprint(
                    sprint_number=max(0, sprint.sprint_number),
                    sprint_name=sprint_name or f"Sprint-{sprint.sprint_number}",
                    sprint_objective=sprint.sprint_objective.strip() or "Advance the project in a structured way.",
                    mini_sprints=mini_sprints,
                )
            )
        if len(cleaned_sprints) < 5:
            cleaned_sprints = self._expand_to_minimum_five(cleaned_sprints)
        if len(cleaned_sprints) > 12:
            cleaned_sprints = cleaned_sprints[:12]
        return SprintPlan(
            project_title=self.project_title.strip() or "Untitled Project",
            project_summary=self.project_summary.strip() or "No summary provided.",
            sprints=cleaned_sprints,
            source_readme_sha256=self.source_readme_sha256,
            generated_at=self.generated_at or utc_now_iso(),
            model=self.model,
            generator_version=self.generator_version,
        )

    @staticmethod
    def _expand_to_minimum_five(sprints: List[Sprint]) -> List[Sprint]:
        templates = [
            ("foundation", "Establish the project baseline and environment."),
            ("architecture", "Define the data and solution architecture."),
            ("implementation", "Build the core capabilities and integrations."),
            ("validation", "Test, QA, and harden the solution."),
            ("release", "Package documentation and prepare for rollout."),
        ]
        existing = {s.sprint_number for s in sprints}
        next_number = 0
        while len(sprints) < 5:
            while next_number in existing:
                next_number += 1
            name, objective = templates[len(sprints)]
            sprints.append(
                Sprint(
                    sprint_number=next_number,
                    sprint_name=slugify(name),
                    sprint_objective=objective,
                    mini_sprints=[
                        MiniSprint(
                            mini_sprint_id=f"{next_number}.1",
                            mini_sprint_name=slugify("planning"),
                            description="Clarify scope and capture execution steps.",
                            deliverable="Agreed sprint plan.",
                        ),
                        MiniSprint(
                            mini_sprint_id=f"{next_number}.2",
                            mini_sprint_name=slugify("delivery"),
                            description="Implement the work, validate outputs, and document decisions.",
                            deliverable="Completed work package.",
                        ),
                    ],
                )
            )
            existing.add(next_number)
            next_number += 1
        return sorted(sprints, key=lambda s: s.sprint_number)


@dataclass
class RetryConfig:
    attempts: int = 4
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 20.0
    timeout_seconds: float = 45.0


@dataclass
class Config:
    github_token: str
    github_owner: str
    github_repo: str
    github_branch: str
    gemini_api_key: str
    github_api: str = DEFAULT_GITHUB_API
    gemini_api: str = DEFAULT_GEMINI_API
    gemini_model: str = DEFAULT_GEMINI_MODEL
    skip_folders: Tuple[str, ...] = tuple(sorted(DEFAULT_SKIP_FOLDERS))
    write_delay_seconds: float = 0.0
    max_workers: int = 4
    branch_prefix: str = "sprint-gen"
    create_pr: bool = True
    dry_run: bool = False
    readme_char_limit: int = 12000
    model_temperature: float = 0.2
    model_max_output_tokens: int = 4096
    retry_attempts: int = 4
    retry_base_delay_seconds: float = 1.0
    retry_max_delay_seconds: float = 20.0
    timeout_seconds: float = 45.0

    @staticmethod
    def from_args(args: argparse.Namespace) -> "Config":
        github_token = args.github_token or os.getenv("GITHUB_TOKEN", "")
        github_owner = args.github_owner or os.getenv("GITHUB_OWNER", "")
        github_repo = args.github_repo or os.getenv("GITHUB_REPO", "")
        github_branch = args.github_branch or os.getenv("GITHUB_BRANCH", "main")
        gemini_api_key = args.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        if not github_token:
            raise ValueError("Missing GitHub token. Set GITHUB_TOKEN or pass --github-token.")
        if not github_owner:
            raise ValueError("Missing GitHub owner. Set GITHUB_OWNER or pass --github-owner.")
        if not github_repo:
            raise ValueError("Missing GitHub repo. Set GITHUB_REPO or pass --github-repo.")
        if not gemini_api_key:
            raise ValueError("Missing Gemini API key. Set GEMINI_API_KEY or pass --gemini-api-key.")
        skip_flags = getattr(args, "skip_folder", []) or []
        skip_folders = tuple(sorted(set(DEFAULT_SKIP_FOLDERS).union(set(skip_flags))))
        return Config(
            github_token=github_token,
            github_owner=github_owner,
            github_repo=github_repo,
            github_branch=github_branch,
            gemini_api_key=gemini_api_key,
            github_api=os.getenv("GITHUB_API_URL", DEFAULT_GITHUB_API),
            gemini_api=os.getenv("GEMINI_API_URL", DEFAULT_GEMINI_API),
            gemini_model=args.gemini_model or os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
            skip_folders=skip_folders,
            write_delay_seconds=args.write_delay,
            max_workers=args.workers,
            branch_prefix=args.branch_prefix,
            create_pr=not args.no_pr,
            dry_run=args.dry_run,
            readme_char_limit=args.readme_char_limit,
            model_temperature=args.temperature,
            model_max_output_tokens=args.max_output_tokens,
            retry_attempts=args.retry_attempts,
            retry_base_delay_seconds=args.retry_base_delay,
            retry_max_delay_seconds=args.retry_max_delay,
            timeout_seconds=args.timeout,
        )

    def retry_config(self) -> RetryConfig:
        return RetryConfig(
            attempts=self.retry_attempts,
            base_delay_seconds=self.retry_base_delay_seconds,
            max_delay_seconds=self.retry_max_delay_seconds,
            timeout_seconds=self.timeout_seconds,
        )


class GitHubClient:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": f"{APP_NAME}/{APP_VERSION}",
        })
        self.retry = config.retry_config()

    @property
    def api(self) -> str:
        return self.config.github_api.rstrip("/")

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.api}{path}"
        return request_with_retry(self.session, method, url, retry=self.retry, logger=LOGGER, **kwargs)

    def list_repo_folders(self) -> List[str]:
        resp = self._request("GET", f"/repos/{self.config.github_owner}/{self.config.github_repo}/contents/", params={"ref": self.config.github_branch})
        resp.raise_for_status()
        return [
            item.get("name", "")
            for item in resp.json()
            if item.get("type") == "dir" and item.get("name", "") not in self.config.skip_folders
        ]

    def fetch_readme(self, folder: str) -> Optional[str]:
        for name in ["README.md", "Readme.md", "readme.md"]:
            resp = self._request("GET", f"/repos/{self.config.github_owner}/{self.config.github_repo}/contents/{folder}/{name}", params={"ref": self.config.github_branch})
            if resp.status_code == 200:
                payload = resp.json()
                if payload.get("encoding") != "base64":
                    raise ValueError(f"Unexpected encoding for {folder}/{name}: {payload.get('encoding')}")
                return base64.b64decode(payload.get("content", "")).decode("utf-8", errors="replace")
            if resp.status_code not in (404, 200):
                resp.raise_for_status()
        return None

    def get_file_text(self, path: str, ref: Optional[str] = None) -> Optional[str]:
        resp = self._request("GET", f"/repos/{self.config.github_owner}/{self.config.github_repo}/contents/{path}", params={"ref": ref or self.config.github_branch})
        if resp.status_code == 200:
            payload = resp.json()
            if payload.get("encoding") == "base64":
                return base64.b64decode(payload.get("content", "")).decode("utf-8", errors="replace")
            return None
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return None

    def get_branch_sha(self, branch: str) -> str:
        resp = self._request("GET", f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/ref/heads/{branch}")
        resp.raise_for_status()
        return resp.json()["object"]["sha"]

    def create_branch(self, new_branch: str, base_branch: str) -> None:
        base_sha = self.get_branch_sha(base_branch)
        resp = self._request(
            "POST",
            f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/refs",
            json={"ref": f"refs/heads/{new_branch}", "sha": base_sha},
        )
        if resp.status_code in (201, 422):
            return
        resp.raise_for_status()

    def create_blob(self, content: str) -> str:
        resp = self._request(
            "POST",
            f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/blobs",
            json={"content": content, "encoding": "utf-8"},
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    def get_commit_tree_sha(self, commit_sha: str) -> str:
        resp = self._request("GET", f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/commits/{commit_sha}")
        resp.raise_for_status()
        return resp.json()["tree"]["sha"]

    def create_tree(self, base_tree_sha: str, entries: List[Dict[str, Any]]) -> str:
        resp = self._request(
            "POST",
            f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/trees",
            json={"base_tree": base_tree_sha, "tree": entries},
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        resp = self._request(
            "POST",
            f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/commits",
            json={"message": message, "tree": tree_sha, "parents": [parent_sha]},
        )
        resp.raise_for_status()
        return resp.json()["sha"]

    def update_ref(self, branch: str, commit_sha: str) -> None:
        resp = self._request(
            "PATCH",
            f"/repos/{self.config.github_owner}/{self.config.github_repo}/git/refs/heads/{branch}",
            json={"sha": commit_sha, "force": False},
        )
        resp.raise_for_status()

    def create_pull_request(self, head_branch: str, base_branch: str, title: str, body: str) -> Optional[Dict[str, Any]]:
        resp = self._request(
            "POST",
            f"/repos/{self.config.github_owner}/{self.config.github_repo}/pulls",
            json={
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch,
                "maintainer_can_modify": True,
            },
        )
        if resp.status_code in (200, 201):
            return resp.json()
        if resp.status_code == 422:
            return None
        resp.raise_for_status()
        return None


SYSTEM_PROMPT = """
You are a senior software project manager who specialises in data engineering and project execution.

Given a project README.md, extract or generate a sprint-based breakdown.

Rules:
1. Produce between 5 and 12 sprints, numbered from 0 upward.
2. Each sprint must have 2 to 5 mini sprints.
3. Output ONLY valid JSON.
4. Follow this exact schema:

{
  "project_title": "<string>",
  "project_summary": "<one-paragraph summary>",
  "sprints": [
    {
      "sprint_number": 0,
      "sprint_name": "Platform-Foundation",
      "sprint_objective": "<one sentence>",
      "mini_sprints": [
        {
          "mini_sprint_id": "0.1",
          "mini_sprint_name": "Environment-Setup",
          "description": "<2-3 sentence description>",
          "deliverable": "<concrete output>"
        }
      ]
    }
  ]
}

Use kebab-case for sprint_name and mini_sprint_name.
Keep descriptions concise but actionable.
""".strip()


class GeminiClient:
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.retry = config.retry_config()

    @property
    def api(self) -> str:
        return self.config.gemini_api.rstrip("/")

    def _url(self) -> str:
        return f"{self.api}/models/{self.config.gemini_model}:generateContent?key={self.config.gemini_api_key}"

    def _request(self, payload: Dict[str, Any]) -> requests.Response:
        return request_with_retry(self.session, "POST", self._url(), json=payload, retry=self.retry, logger=LOGGER)

    def _payload(self, prompt_text: str, temperature: float) -> Dict[str, Any]:
        return {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": self.config.model_max_output_tokens,
            },
        }

    def generate(self, readme_text: str) -> Optional[Dict[str, Any]]:
        prompt = "Generate the sprint breakdown JSON for this README:\n\n" + read_text_safely(readme_text, self.config.readme_char_limit)
        resp = self._request(self._payload(prompt, self.config.model_temperature))
        if resp.status_code != 200:
            LOGGER.error("Gemini returned HTTP %s: %s", resp.status_code, resp.text[:300])
            return None
        try:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            LOGGER.error("Gemini response missing expected text payload")
            return None
        candidate = extract_json_object(text)
        if candidate is None:
            LOGGER.error("Could not extract JSON from Gemini response")
            return None
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            LOGGER.error("Gemini returned invalid JSON")
            return None

    def repair(self, readme_text: str, bad_payload: str, validation_errors: List[str]) -> Optional[Dict[str, Any]]:
        repair_prompt = f"""
The previous response was invalid.

Validation errors:
{json.dumps(validation_errors, indent=2)}

README:
{read_text_safely(readme_text, self.config.readme_char_limit)}

Invalid model output:
{read_text_safely(bad_payload, 8000)}

Return corrected JSON only, matching the schema exactly.
""".strip()
        resp = self._request(self._payload(repair_prompt, 0.0))
        if resp.status_code != 200:
            LOGGER.error("Gemini repair call returned HTTP %s", resp.status_code)
            return None
        try:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return None
        candidate = extract_json_object(text)
        if candidate is None:
            return None
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None


def fallback_plan(folder: str, readme_text: str, readme_hash: str, model: str) -> SprintPlan:
    headings = parse_readme_headings(readme_text)
    title = headings[0] if headings else folder.replace("-", " ")
    summary_bits = headings[1:4]
    summary = "This project appears to cover " + (", ".join(summary_bits) if summary_bits else "a structured implementation effort") + "."
    phases = [
        ("foundation", "Establish the project baseline and environment."),
        ("architecture", "Define the data and solution architecture."),
        ("implementation", "Build the core capabilities and integrations."),
        ("validation", "Test, QA, and harden the solution."),
        ("release", "Package documentation and prepare for rollout."),
    ]
    sprints: List[Sprint] = []
    for idx, (name, objective) in enumerate(phases):
        sprints.append(
            Sprint(
                sprint_number=idx,
                sprint_name=slugify(name),
                sprint_objective=objective,
                mini_sprints=[
                    MiniSprint(
                        mini_sprint_id=f"{idx}.1",
                        mini_sprint_name=slugify("planning"),
                        description="Clarify scope and capture execution steps.",
                        deliverable="Agreed sprint plan.",
                    ),
                    MiniSprint(
                        mini_sprint_id=f"{idx}.2",
                        mini_sprint_name=slugify("delivery"),
                        description="Implement the work, validate outputs, and document decisions.",
                        deliverable="Completed work package.",
                    ),
                ],
            )
        )
    return SprintPlan(
        project_title=title,
        project_summary=summary,
        sprints=sprints,
        source_readme_sha256=readme_hash,
        generated_at=utc_now_iso(),
        model=model,
    ).normalized()


def generate_project_readme(plan: SprintPlan) -> str:
    sprint_rows = "\n".join(
        f"| Sprint {s.sprint_number} | [{escape_md_cell(s.sprint_name.replace('-', ' '))}](Sprint-{s.sprint_number}-{s.sprint_name}/README.md) | {escape_md_cell(s.sprint_objective)} |"
        for s in plan.sprints
    )
    return f"""# {plan.project_title}

## Project Summary
{plan.project_summary}

## Sprint Overview

| # | Sprint | Objective |
|---|--------|-----------|
{sprint_rows}

---
Auto-generated by {APP_NAME}. The sprint metadata is stored in `.sprint-generator/plan.json`.
"""


def generate_sprint_readme(plan: SprintPlan, sprint: Sprint) -> str:
    mini_sprint_list = "\n".join(
        f"- [{ms.mini_sprint_id} — {ms.mini_sprint_name.replace('-', ' ')}](MiniSprint-{ms.mini_sprint_id}-{ms.mini_sprint_name}.md)"
        for ms in sprint.mini_sprints
    )
    return f"""# Sprint {sprint.sprint_number}: {sprint.sprint_name.replace('-', ' ')}

## Objective
{sprint.sprint_objective}

## Mini Sprints
{mini_sprint_list}

---
Auto-generated by {APP_NAME}. Update this file with implementation details as work progresses.
"""


def generate_mini_sprint_file(plan: SprintPlan, sprint: Sprint, ms: MiniSprint) -> str:
    return f"""# MiniSprint {ms.mini_sprint_id} - {ms.mini_sprint_name.replace('-', ' ')}

**Sprint:** Sprint {sprint.sprint_number} - {sprint.sprint_name.replace('-', ' ')}

## Overview
{ms.description}

## Deliverable
{ms.deliverable}

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Notes
> Add implementation notes here.

---
Auto-generated by {APP_NAME}. Replace placeholders with actual execution details.
"""


def generate_plan_metadata(plan: SprintPlan) -> str:
    return json.dumps(plan.to_dict(), indent=2, ensure_ascii=False) + "\n"


@dataclass
class ProjectResult:
    folder: str
    status: str
    message: str
    branch: Optional[str] = None
    pull_request_url: Optional[str] = None
    files_written: int = 0


class SprintGeneratorService:
    def __init__(self, config: Config):
        self.config = config

    def github_client(self) -> GitHubClient:
        return GitHubClient(self.config)

    def gemini_client(self) -> GeminiClient:
        return GeminiClient(self.config)

    def should_skip_project(self, github: GitHubClient, folder: str, readme_hash: str) -> bool:
        marker_path = f"{folder}/.sprint-generator/plan.json"
        existing = github.get_file_text(marker_path, ref=self.config.github_branch)
        if not existing:
            return False
        try:
            payload = json.loads(existing)
            return payload.get("source_readme_sha256") == readme_hash
        except Exception:
            return False

    def process_project(self, folder: str) -> ProjectResult:
        github = self.github_client()
        gemini = self.gemini_client()
        LOGGER.info("Project started: %s", folder)

        readme = github.fetch_readme(folder)
        if not readme:
            return ProjectResult(folder=folder, status="skipped", message="README.md not found")

        readme_hash = sha256_text(readme)
        if self.should_skip_project(github, folder, readme_hash):
            return ProjectResult(folder=folder, status="skipped", message="No README changes detected")

        raw_plan = gemini.generate(readme)
        if raw_plan is None:
            LOGGER.warning("Gemini generation failed for %s, using fallback", folder)
            plan = fallback_plan(folder, readme, readme_hash, self.config.gemini_model)
        else:
            plan = SprintPlan.from_dict(raw_plan)
            plan.source_readme_sha256 = readme_hash
            plan.generated_at = utc_now_iso()
            plan.model = self.config.gemini_model
            validation_errors = plan.validate()
            if validation_errors:
                LOGGER.warning("Validation errors for %s: %s", folder, validation_errors)
                repaired = gemini.repair(readme, json.dumps(raw_plan, indent=2), validation_errors)
                if repaired:
                    candidate = SprintPlan.from_dict(repaired)
                    candidate.source_readme_sha256 = readme_hash
                    candidate.generated_at = utc_now_iso()
                    candidate.model = self.config.gemini_model
                    plan = candidate.normalized()
                else:
                    plan = plan.normalized()
            else:
                plan = plan.normalized()

        return self._write_project(github, folder, plan)

    def _write_project(self, github: GitHubClient, folder: str, plan: SprintPlan) -> ProjectResult:
        branch = f"{self.config.branch_prefix}/{slugify(folder)}/{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        files: List[Tuple[str, str]] = []

        files.append((f"{folder}/README.md", generate_project_readme(plan)))
        files.append((f"{folder}/.sprint-generator/plan.json", generate_plan_metadata(plan)))

        for sprint in plan.sprints:
            sprint_folder = f"Sprint-{sprint.sprint_number}-{sprint.sprint_name}"
            base_path = f"{folder}/{sprint_folder}"
            files.append((f"{base_path}/README.md", generate_sprint_readme(plan, sprint)))
            for ms in sprint.mini_sprints:
                ms_filename = f"MiniSprint-{ms.mini_sprint_id}-{ms.mini_sprint_name}.md"
                files.append((f"{base_path}/{ms_filename}", generate_mini_sprint_file(plan, sprint, ms)))

        if self.config.dry_run:
            return ProjectResult(folder=folder, status="dry-run", message=f"Planned {len(files)} file(s)", branch=branch, files_written=len(files))

        github.create_branch(branch, self.config.github_branch)
        head_sha = github.get_branch_sha(branch)
        base_tree_sha = github.get_commit_tree_sha(head_sha)

        tree_entries: List[Dict[str, Any]] = []
        for path, content in files:
            blob_sha = github.create_blob(content)
            tree_entries.append({"path": path, "mode": "100644", "type": "blob", "sha": blob_sha})

        tree_sha = github.create_tree(base_tree_sha, tree_entries)
        commit_sha = github.create_commit(f"[sprint-gen] Generate sprint structure for {folder}", tree_sha, head_sha)
        github.update_ref(branch, commit_sha)

        pr_url = None
        if self.config.create_pr:
            pr = github.create_pull_request(
                branch,
                self.config.github_branch,
                f"[sprint-gen] {folder}",
                (
                    f"Automated sprint generation for `{folder}`.\n\n"
                    f"- Source README hash: `{plan.source_readme_sha256}`\n"
                    f"- Generated at: `{plan.generated_at}`\n"
                    f"- Generator: `{APP_NAME} {APP_VERSION}`\n"
                ),
            )
            if pr:
                pr_url = pr.get("html_url")

        if self.config.write_delay_seconds > 0:
            time.sleep(self.config.write_delay_seconds)

        return ProjectResult(folder=folder, status="success", message=f"Wrote {len(files)} file(s)", branch=branch, pull_request_url=pr_url, files_written=len(files))

    def run(self, folders: Optional[List[str]] = None) -> List[ProjectResult]:
        if folders is None:
            folders = self.github_client().list_repo_folders()

        results: List[ProjectResult] = []
        if self.config.max_workers <= 1:
            for folder in folders:
                try:
                    results.append(self.process_project(folder))
                except Exception as exc:
                    LOGGER.exception("Unhandled error for %s", folder)
                    results.append(ProjectResult(folder=folder, status="error", message=str(exc)))
            return results

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_map = {executor.submit(self.process_project, folder): folder for folder in folders}
            for future in as_completed(future_map):
                folder = future_map[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    LOGGER.exception("Unhandled error for %s", folder)
                    results.append(ProjectResult(folder=folder, status="error", message=str(exc)))

        results.sort(key=lambda r: r.folder.lower())
        return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate sprint structures from project README files.")
    parser.add_argument("--github-token", default="", help="GitHub token. Falls back to GITHUB_TOKEN.")
    parser.add_argument("--github-owner", default="", help="GitHub owner/org. Falls back to GITHUB_OWNER.")
    parser.add_argument("--github-repo", default="", help="GitHub repo. Falls back to GITHUB_REPO.")
    parser.add_argument("--github-branch", default="", help="Base branch. Falls back to GITHUB_BRANCH or main.")
    parser.add_argument("--gemini-api-key", default="", help="Gemini API key. Falls back to GEMINI_API_KEY.")
    parser.add_argument("--gemini-model", default="", help="Gemini model name. Defaults to gemini-1.5-flash.")
    parser.add_argument("--workers", type=int, default=4, help="Parallel projects to process.")
    parser.add_argument("--branch-prefix", default="sprint-gen", help="Prefix for generated branches.")
    parser.add_argument("--no-pr", action="store_true", help="Do not create pull requests.")
    parser.add_argument("--dry-run", action="store_true", help="Generate everything without writing to GitHub.")
    parser.add_argument("--write-delay", type=float, default=0.0, help="Optional delay after writes, in seconds.")
    parser.add_argument("--readme-char-limit", type=int, default=12000, help="Max README characters passed to the model.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Gemini temperature.")
    parser.add_argument("--max-output-tokens", type=int, default=4096, help="Gemini max output tokens.")
    parser.add_argument("--retry-attempts", type=int, default=4, help="Retry attempts for API calls.")
    parser.add_argument("--retry-base-delay", type=float, default=1.0, help="Base retry delay in seconds.")
    parser.add_argument("--retry-max-delay", type=float, default=20.0, help="Maximum retry delay in seconds.")
    parser.add_argument("--timeout", type=float, default=45.0, help="HTTP timeout in seconds.")
    parser.add_argument("--skip-folder", action="append", default=[], help="Additional folder name to skip. Repeatable.")
    parser.add_argument("--project", action="append", default=[], help="Process only the specified top-level folder(s). Repeatable.")
    parser.add_argument("--log-level", default="INFO", help="Logging level.")
    parser.add_argument("--load-env", action="store_true", help="Load variables from .env if present.")
    return parser


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.load_env:
        load_dotenv_file()

    configure_logging(args.log_level)

    try:
        config = Config.from_args(args)
    except ValueError as exc:
        LOGGER.error(str(exc))
        return 2

    service = SprintGeneratorService(config)
    if args.project:
        folders = args.project
    else:
        try:
            folders = service.github_client().list_repo_folders()
        except Exception as exc:
            LOGGER.error("Failed to discover project folders: %s", exc)
            return 3

    LOGGER.info("Repo: %s/%s (base branch: %s)", config.github_owner, config.github_repo, config.github_branch)
    LOGGER.info("Projects selected: %s", ", ".join(folders) if folders else "(none)")

    results = service.run(folders)
    success = sum(1 for r in results if r.status == "success")
    skipped = sum(1 for r in results if r.status == "skipped")
    dry_run = sum(1 for r in results if r.status == "dry-run")
    errors = sum(1 for r in results if r.status == "error")

    for result in results:
        extra = []
        if result.branch:
            extra.append(f"branch={result.branch}")
        if result.pull_request_url:
            extra.append(f"pr={result.pull_request_url}")
        suffix = f" ({', '.join(extra)})" if extra else ""
        LOGGER.info("%s: %s%s", result.folder, result.status, suffix)

    LOGGER.info("Done. success=%s skipped=%s dry_run=%s error=%s", success, skipped, dry_run, errors)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
