from __future__ import annotations

from contextlib import AbstractContextManager, contextmanager
import logging
from pathlib import Path
import typing as t

log = logging.getLogger(__name__)

from . import cache

from dynaconf import Dynaconf
import hishel
import httpx

## Load HTTP settings from environment
HTTP_SETTINGS = Dynaconf(
    environments=True,
    env="http",
    envvar_prefix="HTTP_CACHE",
    settings_files=[".settings.toml", ".secrets.toml"],
)


def ensure_dir_exists(path: str) -> None:
    """Create directory if it does not exist.

    Params:
        path (str): The path to ensure existence of.

    """
    path: Path = Path(str(path))

    if not path.exists():
        ## Create path if it does not exist
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = f"({type(exc)}) Error creating directory '{path}'. Details: {exc}"
            log.error(msg)

            raise exc


def get_http_controller(
    use_cache: bool = True,
    force_cache: bool = True,
    follow_redirects: bool = False,
    cache_type: str = HTTP_SETTINGS.get("HTTP_CACHE_TYPE", default="sqlite"),
    cache_file_dir: str = HTTP_SETTINGS.get(
        "HTTP_CACHE_FILE_DIR", default=".cache/http/hishel"
    ),
    cache_db_file: str = HTTP_SETTINGS.get(
        "HTTP_CACHE_DB_FILE", default=".cache/http/hishel.sqlite3"
    ),
    cache_ttl: int | None = HTTP_SETTINGS.get("HTTP_CACHE_TTL", default=900),
    check_ttl_every: float | None = HTTP_SETTINGS.get(
        "HTTP_CACHE_CHECK_TTL_EVERY", default=60
    ),
    cacheable_methods: list[str] | None = None,
    cacheable_status_codes: list[int] | None = None,
    cache_allow_heuristics: bool = True,
    cache_allow_stale: bool = False,
) -> HttpxController:
    """Return an initialized HttpxController class object.

    Description:
        The HttpxController class handles an httpx Client. It manages cache configuration
        & building cache storage/controller/transport, as well as managing the httpx client &
        its interactions with the cache.

        The controller class offers a convenient interface for a number of http_lib backend
        functionality.

    Params:
        use_cache (bool): (default: True) When `False`, cache will not be used if it is
            configured for the controller.
        force_cache (bool) (default: True) When `False`, client will respect server response headers
            that disable response caching.
        follow_redirects (bool): (default: True) When `True`, follow any redirect responses from the
            remote to the new location.
        cache_type (str): The type of hishel cache to use, i.e. "sqlite", "file", & more.
        cache_file_dir (str): If hishel.FileStorage is the cache backend, define the path where cache
            files will be saved.
        cache_db_file (str): If hishel.SQLiteStorage is the cache backend, define the path where the
            cache SQLite database file will be saved.
        cache_ttl (int): (default: 900) Amount of time, in seconds, cached items should live for.
        check_ttl_every (int): (default: 60) Interval where cache will check for stale objects to remove.
        cacheable_methods (list[str] | None): List of HTTP methods that will be cached, i.e. "GET", "POST", etc.
        cacheable_status_codes (list[int] | None): List of HTTP response codes that will be cached, i.e. 200, 301, etc.
        cache_allow_heuristics (bool): (default: True) Use heuristics to match objects in cache, improves performance &
            reliability of caching new objects.
        cache_allow_stale (bool): (default: False) When `True`, allow stale/expired responses from cache.

    Returns:
        (HttpxController): Initialized HttpxController object to use for requests.

    """
    ## Build HttpxController object
    try:
        http_ctl: HttpxController = HttpxController(
            use_cache=use_cache,
            force_cache=force_cache,
            follow_redirects=follow_redirects,
            cache_type=cache_type,
            cache_file_dir=cache_file_dir,
            cache_db_file=cache_db_file,
            cache_ttl=cache_ttl,
            check_ttl_every=check_ttl_every,
            cacheable_methods=cacheable_methods,
            cacheable_status_codes=cacheable_status_codes,
            cache_allow_heuristics=cache_allow_heuristics,
            cache_allow_stale=cache_allow_stale,
        )

        return http_ctl
    except Exception as exc:
        msg = f"({type(exc)}) Error initializing HttpxController. Details: {exc}"
        log.error(msg)

        raise exc


class HttpxController(AbstractContextManager):
    """Controller for an httpx client with optional hishel cache storage.

    Description:
        The HttpxController class handles an httpx Client. It manages hishel cache configuration
        & building cache storage/controller/transport, as well as managing the httpx client &
        its interactions with the cache.

        The controller class offers a convenient interface for a number of http_lib backend
        functionality.

    Params:
        use_cache (bool): (default: True) When `False`, cache will not be used if it is
            configured for the controller.
        force_cache (bool) (default: True) When `False`, client will respect server response headers
            that disable response caching.
        follow_redirects (bool): (default: True) When `True`, follow any redirect responses from the
            remote to the new location.
        cache_type (str): The type of hishel cache to use, i.e. "sqlite", "file", & more.
        cache_file_dir (str): If hishel.FileStorage is the cache backend, define the path where cache
            files will be saved.
        cache_db_file (str): If hishel.SQLiteStorage is the cache backend, define the path where the
            cache SQLite database file will be saved.
        cache_ttl (int): (default: 900) Amount of time, in seconds, cached items should live for.
        check_ttl_every (int): (default: 60) Interval where cache will check for stale objects to remove.
        cacheable_methods (list[str] | None): List of HTTP methods that will be cached, i.e. "GET", "POST", etc.
        cacheable_status_codes (list[int] | None): List of HTTP response codes that will be cached, i.e. 200, 301, etc.
        cache_allow_heuristics (bool): (default: True) Use heuristics to match objects in cache, improves performance &
            reliability of caching new objects.
        cache_allow_stale (bool): (default: False) When `True`, allow stale/expired responses from cache.
    """

    def __init__(
        self,
        use_cache: bool = True,
        force_cache: bool = True,
        follow_redirects: bool = False,
        cache_type: str | None = "sqlite",
        cache_file_dir: str | None = ".cache/http/hishel",
        cache_db_file: str = ".cache/http/hishel.sqlite3",
        cache_ttl: int | None = 900,
        check_ttl_every: float | None = 60,
        cacheable_methods: list[str] | None = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "HEAD",
            "CONNECT",
            "TRACE",
            "PATCH",
        ],
        cacheable_status_codes: list[int] | None = [200, 201, 202, 301, 308],
        cache_allow_heuristics: bool = True,
        cache_allow_stale: bool = False,
    ) -> None:
        self.use_cache: bool = use_cache
        self.force_cache: bool = force_cache
        self.follow_redirects: bool = follow_redirects
        self.cache_type: str | None = cache_type.lower()
        self.cache_file_dir: str | None = cache_file_dir
        self.cache_db_file: str = cache_db_file
        self.cache_ttl: int | None = cache_ttl
        self.check_ttl_every: float | None = check_ttl_every
        self.cacheable_methods: list[str] | None = cacheable_methods
        self.cacheable_status_codes: list[int] | None = cacheable_status_codes
        self.cache_allow_heuristics: bool = cache_allow_heuristics
        self.cache_allow_stale: bool = cache_allow_stale

        ## Placeholder for initialized httpx.Client
        self.client: httpx.Client | None = None
        ## Placeholder for hishel cache storage object
        self.cache: t.Union[hishel.SQLiteStorage, hishel.FileStorage] | None = None
        ## Placeholder for hishel cache controller object
        self.cache_controller: hishel.Controller | None = None
        ## Placeholder for hishel cache transport object
        self.cache_transport: hishel.CacheTransport | None = None

        ## Class logger
        self.logger: logging.Logger = log.getChild("HttpxController")

    def __enter__(self) -> t.Self:
        if self.use_cache:
            ## If cache is enabled, build cache from class params
            cache: hishel.SQLiteStorage | hishel.FileStorage | None = self._get_cache()
            transport: hishel.CacheTransport = self._get_cache_transport()
            controller: hishel.Controller = self._get_cache_controller()
        else:
            ## Set all cache objects to None to disable
            cache = None
            transport = None
            controller = None

        self.cache = cache
        self.cache_transport = transport
        self.cache_controller = controller

        ## Initialize httpx Client
        self.client: httpx.Client = self._get_client()

        return self

    def __exit__(self, exc_type, exc_val, traceback) -> t.Literal[False] | None:
        if self.client:
            self.client.close()

        if exc_val:
            msg = f"({exc_type}) {exc_val}"
            self.logger.error(msg)

            if traceback:
                self.logger.error(f"Traceback: {traceback}")

            return False

        return

    def _get_cache(self) -> t.Union[hishel.SQLiteStorage, hishel.FileStorage] | None:
        """Initialize hishel cache storage."""
        match self.cache_type:
            case None:
                return None
            case "sqlite":
                ## Get hishel SQLite storage object
                _cache: hishel.SQLiteStorage = cache.get_sqlite_cache_storage(
                    cache_db_path=self.cache_db_file, ttl=self.cache_ttl
                )
            case "file":
                ## Get hishel file storage object
                _cache: hishel.FileStorage = cache.get_file_cache_storage(
                    base_path=self.cache_file_dir,
                    ttl=self.cache_ttl,
                    check_ttl_every=self.check_ttl_every,
                )
            case _:
                ## Unsupported cache type
                log.error(f"Unrecognized cache type: {self.cache_type}")

                return None

        return _cache

    def _get_cache_controller(self) -> hishel.Controller:
        """Initialize hishel cache controller."""
        _controller: hishel.Controller = cache.get_cache_controller(
            force_cache=self.force_cache,
            cacheable_methods=self.cacheable_methods,
            cacheable_status_codes=self.cacheable_status_codes,
            allow_heuristics=self.cache_allow_heuristics,
            allow_stale=self.cache_allow_stale,
        )

        return _controller

    def _get_cache_transport(self) -> hishel.CacheTransport:
        """Initialize hishel cache transport from class params."""
        if self.cache is None:
            cache_storage: hishel.SQLiteStorage | hishel.FileStorage | None = (
                self._get_cache()
            )
            self.cache = cache_storage

        if self.cache_controller is None:
            cache_controller: hishel.Controller = self._get_cache_controller()
            self.cache_controller = cache_controller

        _transport: hishel.CacheTransport = cache.get_cache_transport(
            cache_storage=self.cache, cache_controller=self.cache_controller
        )

        self.cache_transport = _transport

        return _transport

    def _get_client(self) -> httpx.Client:
        """Return an httpx.Client object initialized from class parameters."""
        transport: hishel.CacheTransport | None = self.cache_transport
        client = httpx.Client(
            transport=transport, follow_redirects=self.follow_redirects
        )

        return client
