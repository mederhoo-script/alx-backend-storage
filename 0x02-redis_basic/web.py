#!/usr/bin/env python3
"""
Web cache and tracker
"""
import requests
import redis
from functools import wraps

cache = redis.Redis()


def track_url_access(method):
    """Decorator that counts how many times
    a URL is accessed and caches the result"""
    @wraps(method)
    def wrapper(url):
        cache_key = "cache:" + url
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response.decode("utf-8")

        access_count_key = "access_count:" + url
        html_content = method(url)

        cache.incr(access_count_key)
        cache.set(cache_key, html_content)
        cache.expire(cache_key, 10)
        return html_content
    return wrapper


@track_url_access
def get_page(url: str) -> str:
    """Fetches and returns the HTML content of a URL"""
    response = requests.get(url)
    return response.text
