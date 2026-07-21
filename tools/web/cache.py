# tools/web/cache.py
import time
import threading


class TTLCache:
    """线程安全的简单 TTL 缓存，用于减少重复搜索的调用/费用"""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._store: dict[str, tuple[object, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, ts = item
            if time.time() - ts > self.ttl:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value):
        with self._lock:
            self._store[key] = (value, time.time())