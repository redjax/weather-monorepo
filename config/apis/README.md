# API Configurations

This app queries a number of weather APIs. Each API has configurations, like a location name or coordinates, an API key, etc.

By setting those values in folders under this `config/apis` directory, I can isolate each API's settings by ensuring Dynaconf only loads values for the correct API, by scoping them to folders in `config/apis/`.

## Example: weatherapi

I have defined settings for [weatherapi](https://weatherapi.com) in [`config/apis/weatherapi/`](./weatherapi/). My API secrets are in [`config/apis/weatherapi/.secrets.example.toml`](./weatherapi/.secrets.example.toml), which I will copy to `.secrets.toml` for local development, and my general/non-secret settings are in [`config/apis/weatherapi/settings.toml](./weatherapi/settings.toml), which I will copy to `settings.local.toml` for local development.

After setting my environment variables in `settings.local.toml` and `.secrets.toml`, I can load them in a Python app with something like:

```python
from dynaconf import Dynaconf

WEATHERAPI_SETTINGS = Dynaconf(
    environments=True,
    env="weatherapi",
    envvar_prefix="WEATHERAPI",
    settings_files=["apis/weatherapi/settings.toml", "apis/weatherapi/.secrets.toml"]
)

```

Then, I can load my values, i.e. the API key, like:

```python
weatherapi_api_key = WEATHERAPI_SETTINGS.get("WEATHERAPI_API_KEY", default="")

if weatherapi_api_key is None:
    raise ValueError("Missing an API key. Set an environment variable for WEATHERAPI_API_KEY with your API key to load it in this app.")
```
