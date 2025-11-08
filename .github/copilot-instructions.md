## Purpose

Short, actionable guidance for AI coding agents working in this repository. Focus on where to make changes, how the data flows, and concrete commands to run and test locally.

## Big picture

- This repo contains helper tooling around ComfyUI (external project). The helpers are designed to run inside a Colab / Google Drive environment and also under a normal Python environment. Key concerns: flow composition, model download/verification, local queuing and prompt templates.
- Major components:
  - `Helper Scipts/` — small Python modules that implement core behaviors: `composer.py` (compose flows), `downloader.py` (streaming model downloads + sha256 checks), `queue.py` (sqlite-based queue), `templates.py` (prompt templates stored under DRIVE_ROOT), `manifest_resolver.py` (URL resolution heuristics), `security.py` (API key helpers), `cli.py` (tiny CLI shim).
  - `workflows/` — example ComfyUI JSON flows (see `simple_t2i_workflow.json`, `lora_workflow.json`) to understand node/link structure used by the composer.
  - Notebook(s) (`knacks_comfyui_colab_manager.ipynb`, `Ultimate_ComfyUI_Playground.ipynb`) — environment setup and installation commands frequently used by humans; treat them as living docs for runtime setup.

## Key files & why they matter (examples)

- `Helper Scipts/composer.py` — compose_flow(prompt, model_key=None) returns (path, flow_dict) and writes to FLOWS_DIR (driven by env var `DRIVE_ROOT`). Example: calling compose_flow('A test prompt') creates `flows/flow_<ts>.json`.
- `Helper Scipts/downloader.py` — use streaming_download(url, dest, verify_sha256=...) to fetch large files safely; it writes a `.part` file then moves it and validates sha256 using compute_sha256(path). Respect retries and surface network errors.
- `Helper Scipts/queue.py` — persistent queue stored at `${DRIVE_ROOT}/state/queue.db`. Use enqueue(item), dequeue(), mark_done(id) and list_items(status). The DB is sqlite3 and created lazily.
- `Helper Scipts/templates.py` — prompt templates live at `${DRIVE_ROOT}/config/prompt_templates.json`. Call get_prompt_templates() and save_prompt_templates(...) rather than editing the file directly to preserve drive path behavior.
- `Helper Scipts/manifest_resolver.py` — simple HEAD->GET fallback for URL discovery. It returns `{final_url, headers, status_code}`; use it before downloads to capture server-provided hashes.

## Conventions & patterns agents must follow

- Environment-aware paths: many helpers use DRIVE_ROOT env var (default `/content/drive/MyDrive/ComfyUI`). Do not hardcode repo-root paths — prefer the constants defined in modules (`DRIVE_ROOT`, `FLOWS_DIR`, `DB_PATH`, `TEMPLATES_PATH`).
- Notebook-first workflow: several install commands are in notebooks (see top cells of `knacks_comfyui_colab_manager.ipynb`) and include GPU-specific wheels (torch with extra-index-url). If recommending install commands, prefer `pip install -r requirements.txt` for CI/local and note GPU wheel URLs only when GPU is expected.
- Idempotent file operations: downloader writes a `.part` file then moves; composer ensures directories exist. Preserve this behavior when editing.
- Keep network code sync with `requests` semantics used in repository: HEAD then fallback to GET (streaming). Use the same error-handling style (return dicts with `error` or expected keys) when adding new helpers.
- SQLite concurrency: `sqlite3.connect(..., check_same_thread=False)` is used; prefer reusing get_conn() where provided instead of creating ad-hoc connections.

## How to run & test locally (commands)

1. Install dependencies (CI / local):

```pwsh
pip install -r requirements.txt
python -m pip install -r requirements.txt  # alternate
```

2. CI runner uses Python 3.10 and `pytest -q` (see `Helper Scipts/ci.yml`). To run tests locally replicate that environment and run:

```pwsh
# set up Python 3.10 venv then
pip install -r requirements.txt
pytest -q
```

3. Notebook setup: the Colab notebook installs extra packages and GPU-specific wheels. If you need to reproduce notebook behavior, follow the top cells of `knacks_comfyui_colab_manager.ipynb` (it installs accelerate, transformers, safetensors and specific torch wheels via extra-index-url).

## Integration points / external dependencies

- ComfyUI (external project) — flows and custom node expectations. The `workflows/` JSON shows expected node IDs/types (e.g., `CheckpointLoaderSimple`, `KSampler`, `CLIPTextEncode`). Changing flow structure requires compatibility with ComfyUI.
- ComfyUI-Manager — `knacks_comfyui_colab_manager.ipynb` clones and interacts with `ComfyUI-Manager` (see notebook cells). Be careful when scripting installs that expect `custom_nodes/ComfyUI-Manager`.
- Civitai / model sources — downloader + manifest_resolver are used to fetch artifacts; environment variable `CIVITAI_API_TOKEN` may be used by the notebooks (see comments). When implementing new download logic, check `downloader.py` heuristics (headers and x-goog-hash handling).

## Editing guidelines & examples for agents

- When adding a new helper that touches storage, accept a `drive_root` argument or read `DRIVE_ROOT` from env to remain consistent.
- Example change: to change the default sampler in composed flows update `compose_flow(..., sampler='DDIM')` in `Helper Scipts/composer.py` — the function returns (path, flow_dict) so tests should call it and assert the returned `flow['nodes']` contains the expected params.

## Small notes & gotchas

- The repository contains a directory named `Helper Scipts` (note the space/typo). Always use the exact path string when referencing files.
- Many helpers are designed to run inside a Jupyter/Colab kernel: expect shell-embedded commands and `!pip` usage in notebooks. Prefer the Python modules for programmatic changes.
- No `.github/copilot-instructions.md` existed before — keep this file short and update when new patterns or CI changes appear.

If anything here is unclear or you want more details (tests, example PR diffs, or expansion of the notebook-run workflow), tell me which section to expand and I will iterate.
