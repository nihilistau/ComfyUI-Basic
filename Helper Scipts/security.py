def set_api_key(name: str, key: str, target_globals: dict):
    """Set an API key in the provided globals dict (kernel) without writing to disk.

    Example: set_api_key('COMFYUI_API_KEY', 'xxx', globals())
    """
    if not key:
        return False
    target_globals[name] = key
    return True
