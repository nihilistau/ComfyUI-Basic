import os
import tempfile
import json
from pathlib import Path
import importlib.util


def import_module_from_path(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, str(Path(path)))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compose_flow_creates_file(tmp_path, monkeypatch):
    # Use a temporary DRIVE_ROOT so we don't touch the user's Drive
    tmp_drive = tmp_path / 'drive'
    monkeypatch.setenv('DRIVE_ROOT', str(tmp_drive))
    tmp_drive.mkdir(parents=True, exist_ok=True)

    composer_path = Path('Helper Scipts') / 'composer.py'
    assert composer_path.exists(), 'composer.py missing'
    composer = import_module_from_path('composer', composer_path)

    out_path, flow = composer.compose_flow('unit test prompt', model_key='test-model')
    p = Path(out_path)
    assert p.exists(), 'compose_flow did not write flow file'
    with open(p, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert 'nodes' in data and data.get('format')


def test_queue_roundtrip(tmp_path, monkeypatch):
    # Ensure the queue uses a temp DB location
    tmp_drive = tmp_path / 'drive'
    monkeypatch.setenv('DRIVE_ROOT', str(tmp_drive))
    tmp_drive.mkdir(parents=True, exist_ok=True)

    queue_path = Path('Helper Scipts') / 'queue.py'
    assert queue_path.exists(), 'queue.py missing'
    qmod = import_module_from_path('queue', queue_path)

    item = {'task': 'unittest', 'payload': {'v': 1}}
    id_ = qmod.enqueue(item)
    assert isinstance(id_, int) and id_ > 0
    row = qmod.dequeue()
    assert row and 'item' in row and row['item']['task'] == 'unittest'
    qmod.mark_done(row['id'])
