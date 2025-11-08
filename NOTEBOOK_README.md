NOTEBOOK: how to run the Colab notebooks in this repo

Purpose

This short README explains how to run the notebooks in this repository on Google Colab and locally, how to configure `DRIVE_ROOT`, and common issues (Drive permission errors, large downloads, GPU wheel selection).

Quick start (Colab)

1. Open `knacks_comfyui_colab_manager.ipynb` in Google Colab.
2. In the first cell, mount Google Drive if you want persistent storage. You can run:

```python
from google.colab import drive
drive.mount('/content/drive')
```

3. Set `DRIVE_ROOT` to the folder where you want ComfyUI files stored. The notebooks expect `/content/drive/MyDrive/ComfyUI` by default. You can set it manually in the notebook or export it as an environment variable in a cell:

```python
import os
os.environ['DRIVE_ROOT'] = '/content/drive/MyDrive/ComfyUI'
```

4. Install dependencies (notebooks include cells that call `pip install -r requirements.txt`). Prefer the notebook's cells because they include GPU-specific wheel links when appropriate.

Run cells sequentially from top to bottom. The notebooks are written to be idempotent where possible.

Quick start (Local / Windows)

1. Create and activate a Python 3.10 virtual environment.

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the example notebook locally using Jupyter or run scripts in `Helper Scipts/` directly.

Key environment variables and paths

- `DRIVE_ROOT` (default `/content/drive/MyDrive/ComfyUI` in Colab) — used by helpers to locate flows, state DB, and templates. Modules reference constants like `DRIVE_ROOT`, `FLOWS_DIR`, `DB_PATH`, and `TEMPLATES_PATH`.

Common issues and troubleshooting

1. Drive permission errors (most frequent)
   - Symptoms: failures to write files under `/content/drive/MyDrive/...`, `Permission denied`, or missing files after running cells.
   - Fixes:
     - Re-run `drive.mount('/content/drive')` and follow the interactive OAuth flow.
     - Check that the notebook has permission to access the correct Google account.
     - Ensure the `DRIVE_ROOT` path exists and is writable: `!mkdir -p /content/drive/MyDrive/ComfyUI` in a Colab cell.

2. Large downloads blocking the notebook
   - Symptoms: long-running `streaming_download` calls or hitting network limits.
   - Fixes:
     - Do not run large downloads inside example cells. Use the downloader helper with explicit URLs and verify hashes.
     - For heavy downloads, prefer doing them outside Colab (local machine) or ensure you have the correct quota and network speed.

3. GPU wheel / torch mismatch
   - Symptoms: pip install errors when trying to install torch with an incompatible CUDA wheel.
   - Fixes:
     - Use the notebook-provided `pip` cells which include `--extra-index-url` variants for different CUDA versions. Match the wheel to the runtime GPU (e.g., cu121 in the notebook). If in doubt, use CPU-only wheels or the CI path (pip install -r requirements.txt) for local testing.

4. Notebook-specific helper import errors due to the folder name `Helper Scipts`
   - Symptoms: `ModuleNotFoundError` when trying `import composer` etc.
   - Fixes:
     - Import by path (examples in `colab_templates.ipynb`) using `importlib.util.spec_from_file_location`.
     - Alternatively rename the folder (not recommended if preserving checkpoint) — if you must rename, update all references and tests.

Best practices for edits and additions

- Keep changes Colab-compatible: prefer environment-driven paths (`DRIVE_ROOT`) and idempotent operations.
- Avoid hiding or hardcoding secrets. Use environment variables for API tokens (e.g., `CIVITAI_API_TOKEN`) and set them manually in the Colab session if needed.
- Small, additive changes are preferred: new helper functions should accept `drive_root` or read `DRIVE_ROOT` from env to remain compatible with existing notebooks.

If you want, I can:
- Add a `tests/test_basics.py` that checks `compose_flow` and queue behavior (no GPU).\n- Add a short PR that converts `colab_templates.ipynb` into a 3-cell 'first-run' walkthrough you can share.\n