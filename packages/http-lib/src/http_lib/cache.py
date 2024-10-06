from __future__ import annotations

from pathlib import Path
import sqlite3
import typing as t

import hishel
import httpx

def get_sqlite_cache_storage(
    cache_db_path: str = ".cache/http/hishel.sqlite3", ttl=900
) -> hishel.SQLiteStorage:
    """Get a hishel.SQLiteStorage cache.

    Params:
        cache_db_path (str): The path where the SQLite database file will be saved.
        ttl (int): (default: 900) Amount of time, in seconds, for cached items to live.

    Returns:
        (hishel.SQLiteStorage): An initialized SQLiteStorage object.

    """
    ## Ensure database filename ends with a valid SQLite file extension
    if Path(cache_db_path).suffix not in [".sqlite", ".sqlite3", ".db"]:
        cache_db_path = f"{cache_db_path}/.sqlite3"

    cache_dir: Path = Path(cache_db_path).parent
    ## Ensure the cache directory exists
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)

    ## Get sqlite3 connection to cache database
    conn: sqlite3.Connection = sqlite3.connect(database=cache_db_path)
    ## Create SQLiteStorage object using sqlite3 connection
    storage: hishel.SQLiteStorage = hishel.SQLiteStorage(connection=conn, ttl=ttl)

    return storage


def get_file_cache_storage(
    base_path: str = ".cache/http/hishel", ttl: int = 900, check_ttl_every: float = 60
) -> hishel.FileStorage:
    """Get a hishel.FileStorage cache.

    Params:
        base_path (str): The path where file caches will be saved.
        ttl (int): (default: 900) Amount of time, in seconds, for cached items to live.
        check_ttl_every (int): (default: 60) Interval in seconds to check cached item ttl.

    Returns:
        (hishel.FileStorage): An initialized FileStorage object.

    """
    ## Ensure cache directory exists
    if not Path(base_path).exists():
        Path(base_path).mkdir(parents=True, exist_ok=True)

    ## Initialize FileStorage cache
    storage: hishel.FileStorage = hishel.FileStorage(
        base_path=base_path, ttl=ttl, check_ttl_every=check_ttl_every
    )

    return storage


def get_cache_controller(
    force_cache: bool = False,
    cacheable_methods: list[str] | None = None,
    cacheable_status_codes: list[int] | None = None,
    allow_heuristics: bool = True,
    allow_stale: bool = False,
) -> hishel.Controller:
    """Get a hishel.Controller cache controller.

    Description:
        A cache controller handles options/configuration of the chosen cache (SQLiteStorage, FileStorage, etc).
        Configurations include forcing requests to use the cache (if server's response headers have a directive not to),
        only cache certain HTTP methods/response codes, & more.

    Params:
        force_cache (bool): (default: False) If `True`, attempt to override request and force response from cache.
        cacheable_methods (list[str] | None): List of HTTP methods to cache, i.e. `["GET", "POST", "DELETE"]`.
            **NOTE**: Not all HTTP methods are cacheable. The `UPDATE` method, for example.
            Mozilla docs for HTTP request methods: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
        cacheable_status_codes (list[int] | None): List of HTTP response codes to cache, i.e. `[200, 201, 301, 308]`.
            Mozilla docs for HTTP response/status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        allow_heuristics (bool): (default: True) Enable heuristics, which improves cache reliability.
        allow_stale (bool): (default: False) Allow retrieval of stale/expired cached objects.

    Returns:
        (hishel.Controller): An initialized hishel.Controller cache controller.

    """
    ## Build controller
    controller = hishel.Controller(
        force_cache=force_cache,
        cacheable_methods=cacheable_methods,
        cacheable_status_codes=cacheable_status_codes,
        allow_heuristics=allow_heuristics,
        allow_stale=allow_stale,
    )

    return controller


def get_cache_transport(
    transport_base: httpx.HTTPTransport = httpx.HTTPTransport(),
    cache_storage: t.Union[
        hishel.SQLiteStorage, hishel.FileStorage
    ] = get_sqlite_cache_storage(),
    cache_controller: hishel.Controller = get_cache_controller(),
) -> hishel.CacheTransport:
    """Build & return a hishel.CacheTransport for httpx client.

    Description:
        The cache transport joins a cache storage, controller, and httpx.HTTPTransport into a cache transport
        usable by the httpx library.

        Using a transport allows for request sessions (multiple requests through a context manager), redirect handling,
        & more.

    Params:
        trasport_base (httpx.HTTPTransport): The base transport object to append a cache storage & controller to.
        cache_storage (hishel.SQLiteStorage | hishel.FileStorage): The cache storage to use for requests made using a client
            with this transport mounted.
        cache_controller (hishel.Controller): The cache controller that handles responses from HTTP requests made using a client
            with this transport mounted.

    Returns:
        (hishel.CacheTransport): An initialized hishel.CacheTransport HTTP transport.

    """
    ## Build cache transport
    transport: hishel.CacheTransport = hishel.CacheTransport(
        transport=transport_base, storage=cache_storage, controller=cache_controller
    )

    return transport
