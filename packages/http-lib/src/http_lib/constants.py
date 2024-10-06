from __future__ import annotations

"""HTTP response codes.

Docs: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
"""
## Common HTTP success response codes
SUCCESS_CODES: list[int] = [200, 201, 202, 204]
## Common HTTP redirect responsee codes
REDIRECT_CODES: list[int] = [300, 301, 302, 303, 304, 307, 308]
## Common HTTP error response codes
CLIENT_ERROR_CODES: list[int] = [400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410]
## Common HTTP server error response codes
SERVER_ERROR_CODES: list[int] = [500, 501, 502, 503, 504, 505]
## Joined list of all server/client side error response codes
ALL_ERROR_CODES: list[int] = [CLIENT_ERROR_CODES, SERVER_ERROR_CODES]
