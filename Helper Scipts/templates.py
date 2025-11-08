from pathlib import Path
import json
import os

DRIVE_ROOT = Path(os.environ.get('DRIVE_ROOT', '/content/drive/MyDrive/ComfyUI'))
TEMPLATES_PATH = DRIVE_ROOT / 'config' / 'prompt_templates.json'

def ensure_templates_file():
    TEMPLATES_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not TEMPLATES_PATH.exists():
        defaults = [
            {"name": "Photorealistic", "template": "Photorealistic photo of {prompt}"},
            {"name": "Cinematic", "template": "Cinematic poster of {prompt}"},
            {"name": "Studio Portrait", "template": "Studio portrait of {prompt}"},
            {"name": "Fantasy", "template": "Fantasy illustration of {prompt}"},
            {"name": "Minimal", "template": "{prompt}"}
        ]
        with open(TEMPLATES_PATH, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=2, ensure_ascii=False)

def get_prompt_templates():
    try:
        ensure_templates_file()
        with open(TEMPLATES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_prompt_templates(templates):
    ensure_templates_file()
    with open(TEMPLATES_PATH, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)
    return True
