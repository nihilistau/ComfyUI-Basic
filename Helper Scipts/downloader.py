import requests
from pathlib import Path
import hashlib
import shutil
import os
import time
from typing import Optional

CHUNK_SIZE = 1024 * 1024

def compute_sha256(path: Path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            h.update(chunk)
    return h.hexdigest()

def preview_url(url: str, headers: Optional[dict]=None, timeout=15):
    headers = headers or {}
    try:
        r = requests.head(url, allow_redirects=True, headers=headers, timeout=timeout)
        if r.status_code >= 400 or 'content-length' not in r.headers:
            r = requests.get(url, allow_redirects=True, headers=headers, stream=True, timeout=timeout)
        return {'final_url': r.url, 'headers': dict(r.headers), 'status_code': r.status_code}
    except Exception as e:
        return {'error': str(e)}

def normalize_server_hash(headers: dict):
    # Heuristics to extract server-side hash signatures from common headers
    # Look for ETag or x-goog-hash, content-md5, etag style values
    if not headers:
        return None
    et = headers.get('ETag') or headers.get('Etag') or headers.get('etag')
    if et:
        return et.strip('"')
    xg = headers.get('x-goog-hash')
    if xg:
        # example: crc32c=... , md5=... ; pick md5 if present
        parts = [p.strip() for p in xg.split(',')]
        for p in parts:
            if p.startswith('md5='):
                return p.split('=',1)[1]
        return parts[0]
    cl = headers.get('content-md5')
    if cl:
        return cl
    return None

def streaming_download(url: str, dest: str, headers: Optional[dict]=None, timeout=60, verify_sha256: Optional[str]=None):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + '.part')
    headers = headers or {}
    with requests.get(url, stream=True, headers=headers, timeout=timeout) as r:
        r.raise_for_status()
        with open(part, 'ab') as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    # move part to final
    shutil.move(str(part), str(dest))
    if verify_sha256:
        got = compute_sha256(dest)
        if got != verify_sha256:
            raise ValueError(f'SHA256 mismatch: expected {verify_sha256} got {got}')
    return {'path': str(dest), 'sha256': compute_sha256(dest)}
