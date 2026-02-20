from datetime import datetime, timedelta
from threading import RLock
from typing import Any, Hashable, Optional

class LocalTTLCache:
    def __init__(self):
        self._store: dict[Hashable, type[Any, datetime]] = {}
        self._lock = RLock()

    def get(self, key: Hashable) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if not item:
                return None
            value, expires_at = item
            if expires_at < datetime.utcnow():
                del self._store[key]
                return None
            
            return value

    def set(self, key: Hashable, value: Any, ttl_seconds: int) -> None:
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        with self._lock:
            self._store[key] = (value, expires_at)

    def clear(self, prefix: Optional[str] = None) -> None:
        with self._lock:
            if prefix is None:
                self._store.clear()
                return
            
            to_delete = [
                k for k in self._store
                if isinstance(k, str) and k.startwith(prefix)
            ]
            for k in to_delete:
                del self._store[k]


posts_cache = LocalTTLCache()