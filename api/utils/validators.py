from urllib.parse import urlparse
import loguru

def validate_url(url):
    if not is_valid_url(url):
        loguru.logger.error(f"Invalid url: {url}")
        return False
    else:
        return True
    

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
