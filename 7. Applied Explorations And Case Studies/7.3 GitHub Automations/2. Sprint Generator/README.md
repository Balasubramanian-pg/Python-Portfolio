# Sprint Generator

Production-hardened Python automation for converting project README files into sprint structures and writing them back to GitHub.

## What it does

- Reads top-level project folders in a repo
- Fetches README.md from each project folder
- Uses Gemini to generate a sprint plan
- Validates and repairs model output
- Writes project README, sprint folders, mini-sprint files, and metadata
- Uses GitHub Git Data API for batch commits
- Creates a branch per project and can open a PR
- Supports retries, dry-run mode, concurrency, and `.env` loading

## Install

```bash
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` and fill in the values.

## Run

```bash
python sprint_generator.py --load-env
```

Process only specific folders:

```bash
python sprint_generator.py --load-env --project Project-A --project Project-B
```

Dry run:

```bash
python sprint_generator.py --load-env --dry-run
```
