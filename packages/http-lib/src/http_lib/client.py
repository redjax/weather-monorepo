"""The client is the user-facing piece of http_lib.

Users can call the client to build a request, decode a response, encode data for a request, save JSON, & more.

"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import typing as t

log = logging.getLogger(__name__)

import httpx

def build_request(
    method: str = "GET",
    url: str = None,
    params: dict | None = None,
    headers: dict | None = None,
    data: dict | None = None,
    files: t.Any | None = None,
    json: t.Any | None = None,
    stream: httpx.SyncByteStream | httpx.AsyncByteStream | None = None,
    extensions: t.MutableMapping[str, t.Any] | None = None,
) -> httpx.Request:
    """Build an httpx.Request object from inputs.

    Params:
        method (str): (default: "GET") The HTTP method for the request.
        url (str): The URL to send request to.
        params (dict | None): Optional dict of URL params.
        headers (dict | None): Optional dict to use for headers.
        data (dict | None): Optional request body data.
        files (Any | None): Optional file(s) to send with request body.
        json (Any | None): Optional JSON body to send with request.
        stream (httpx.SyncByteStream | httpx.AsyncByteStream | None): Client to stream response. Useful for file downloads.
        extensions (MutableMapping[str, Any] | None): Optional httpx extensions for request.
            Httpx extensions docs: https://www.python-httpx.org/advanced/extensions/
    """
    if method is None:
        ## Default to GET on empty method
        method: str = "GET"
    ## Ensure method is uppercase
    method: str = method.upper()

    ## Build request object
    request: httpx.Request = httpx.Request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        data=data,
        files=files,
        json=json,
        stream=stream,
        extensions=extensions,
    )

    return request


def decode_response(response: httpx.Response = None, encoding: str = "utf-8") -> dict:
    """Decode an httpx.Response object to a Python dict.

    Params:
        response (httpx.Response): An httpx.Response object to convert to a dict.
        encoding (str): (default: "utf-8"): Encoding of response content.

    Returns:
        (dict): A dict representation of the input response object.

    """
    ## Extract response content
    content: bytes = response.content

    ## Decode content to str
    decoded_str: str = content.decode(encoding=encoding)
    ## Load decoded str to dict
    data: dict = json.loads(decoded_str)

    return data


def encode_data(data: t.Union[dict, str], encoding: str = "utf-8") -> bytes:
    """Intelligently encode input data.

    Description:
        If input data is a dict, it will be converted to a JSON string first, then encoded.
        If input data is a string, it will be encoded immediately.

    Params:
        data (dict | str): Input data to encode.
        encoding (str): (default: "utf-8") Codec to encode content with.

    Returns:
        (bytes): The encoded string.

    """
    if isinstance(data, dict):
        data: str = json.dumps(data, indent=2).encode(encoding)
    elif isinstance(data, str):
        pass
    else:
        raise TypeError(f"Invalid type for data: ({type(data)}). Must be a dict or str")

    encoded: bytes = data.encode(encoding)

    return encoded


def save_json(
    data: t.Union[dict, str], output_file: t.Union[str, Path], overwrite: bool = True
) -> None:
    """Save input data to a JSON file.

    Params:
        data (dict | str): The input data to save to JSON.
        output_file (str | Path): Path to the JSON file where data will be saved.
        overwrite (bool): (default: True) Overwrite JSON file if it exists.

    """
    ## Ensure filename ends with .json
    if not str(output_file).endswith(".json"):
        output_file: str = f"{output_file}.json"

    ## If path exists, ensure overwrite=True before continuing
    if Path(str(output_file)).exists():
        if not overwrite:
            ## File exists and overwrite=False, return before saving
            log.warning(
                f"File '{output_file}' exists, and overwrite=False. Skipping save JSON."
            )
            return

    if isinstance(data, dict):
        ## Convert data dict to JSON str
        try:
            _data: str = json.dumps(data, indent=4)
            data = _data
        except Exception as exc:
            msg: str = (
                f"({type(exc)}) Unhandled exception dumping dict to JSON string. Details: {exc}"
            )
            log.error(msg)

            raise exc

    ## Save JSON string to file
    try:
        with open(str(output_file), "w") as f:
            f.write(data)
    except Exception as exc:
        msg = f"({type(exc)}) Unhandled exception writing JSON to file '{output_file}'. Details: {exc}"
        log.error(msg)

        raise exc
