from pathlib import Path
import json
import os
import time

DRIVE_ROOT = Path(os.environ.get('DRIVE_ROOT', '/content/drive/MyDrive/ComfyUI'))
FLOWS_DIR = DRIVE_ROOT / 'flows'
FLOWS_DIR.mkdir(parents=True, exist_ok=True)

def compose_flow(prompt, model_key=None, sampler='DDIM', steps=20, seed=-1, lora=None, upscaler=None, fmt='comfyui'):
    """Compose a minimal ComfyUI-compatible flow JSON and save to FLOWS_DIR.

    Returns (path, flow_dict).
    """
    ts = int(time.time())
    filename = f'flow_{ts}.json'
    flow = {
        'nodes': [
            {
                'id': 'txt2img',
                'type': 'StableDiffusion',
                'params': {
                    'prompt': prompt,
                    'sampler': sampler,
                    'steps': steps,
                    'seed': seed,
                    'model': model_key,
                    'lora': lora,
                    'upscaler': upscaler,
                }
            },
        ],
        'created_at': ts,
        'format': fmt,
    }
    path = FLOWS_DIR / filename
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)
    return str(path), flow
