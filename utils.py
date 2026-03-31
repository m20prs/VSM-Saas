import hashlib

def get_url_id(url):
    return hashlib.md5(url.strip().lower().encode()).hexdigest()[:8]