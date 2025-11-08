"""Manifest resolver stub: preview URL, follow redirects, capture headers, and return resolved info.
This is a lightweight, testable implementation using requests. In production, expand provider-specific heuristics.
"""
import requests
from urllib.parse import urljoin

def preview_url(url, headers=None, timeout=15):
    """Perform a HEAD request (fallback to GET) following redirects and return dict with final_url, headers, content_length."""
    headers = headers or {}
    try:
        r = requests.head(url, allow_redirects=True, headers=headers, timeout=timeout)
        if r.status_code >= 400 or 'content-length' not in r.headers:
            # fallback to GET but stream only headers
            r = requests.get(url, allow_redirects=True, headers=headers, stream=True, timeout=timeout)
        final = r.url
        return {'final_url': final, 'headers': dict(r.headers), 'status_code': r.status_code}
    except Exception as e:
        return {'error': str(e)}
