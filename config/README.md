# Config

This directory stores configuration files that can be read by [`dynaconf`](https://dynaconf.com). These settings files are only meant to be used during local development, you should set environment variables when running in production.

This lets me set environment variables for all my apps, using a single directory (`config/`) to store all of my configurations for local development. In production, I would set environment variables for all of my configurations defined in `settings.toml` file(s) in this folder.

## How to use settings files with Dynaconf

- Reference: [`dynaconf`docs: setting variables in files](https://www.dynaconf.com/#on-files) goes into more detail than I will here.

Dynaconf can read settings from a number of file formats (`.toml`, `.yaml|.yml`, `.json`, & more). This project uses `.toml` files for configuration, and assumes you do as well. If you are using a different format, make sure to check Dynaconf's documentation for syntax.

Dynaconf will read configurations from a directory named `config/`. It will start by looking for a `.local.toml` "version" of your configuration. When setting variables for location development, you should copy `settings.toml` to `settings.local.toml` and override your configurations in the `settings.local.toml` file, leaving the configurations defined in `settings.toml` unchanged.

This is so that you can safely commit `settings.toml` to git, without accidentally committing any secrets or configurations you only want to use on your local machine.

The same goes for any `.secrets.toml` files. You can define your variables, without setting any actual values, in a file `.secrets.example.toml`, and copy it to `.secrets.toml` to define your configurations.

In a Python app, initialize a `Dynaconf` object and tell it where to read settings from. For example, this app interacts with multiple weather APIs, and each API's configuration is stored in a different directory in the [`config/apis`](./apis/) directory. Each API in `config/apis/` has a `.secrets.example.toml` file, where that API's API key (and any other secrets) are stored, but without their real value. To set an API key for the WeatherAPI API, you would copy [`./config/apis/weatherapi/.secrets.example.toml](./apis/weatherapi/.secrets.example.toml) to `./config/apis/weatherapi/.secrets.toml`, and set your API key in the `[weatherapi]` section, under the `weatherapi_api_key = ""` variable.

## How to set environment variables for Dynaconf

- Referencee: [`dynaconf`'s docs: setting variables in environment](https://www.dynaconf.com/#on-env-vars)

When defining environment variables in a `settings.toml` or `settings.local.toml` file, you can use upper or lowercase for variable names, it does not matter. For example, it is ok to set a value like:

```toml
## settings.toml

[logging]

log_level = "INFO"
```

When you set environment variables, they must be all uppercase, and should match the name of the setting in your `settings.toml` file. In this case, to set the `log_level` variable as an environment variable, you would name it `LOG_LEVEL`.

- Windows: `$env:LOG_LEVEL = "DEBUG"`
- Mac/Linux: `export LOG_LEVEL=DEBUG`

Dynaconf loads from the environment first, and if it cannot find a value, will try to load from a `settings.toml` or `settings.local.toml`, uppercasing any variables encountered in the `.toml` file.

## Loading settings with Dynaconf in Python files

After setting your environment variables (either [in a settings.toml](#how-to-use-settings-files-with-dynaconf) file or [in your environment](#how-to-set-environment-variables-for-dynaconf)), you need to read them in your Python app.

First, import Dynaconf:

```python
## example.py

from dynaconf import Dynaconf

```

Then, create a settings object. You can name this anything you like, but Dynaconf will "scope" your permissions to the settings.toml path you give it, and it's a good idea to name your variables something that will make sense to you later.

For example, to load logging settings from [`./config/settings.toml`](./settings.toml) (or, more appropriately, a `./config/settings.local.toml` file to override defaults in `settings.toml`), you must first have a `[logging]` section defined in `settings.toml`, and variables that start with `log_` or `LOG_`.

Pretend this is your app's `./config/settings.toml` file:

```toml
[default]
## Set default values that will be used if a user does not declare the variables in a settings.toml file or the environment
log_level = "INFO"
log_format = "%(asctime)s | [%(levelname)s] | (%(name)s): %(module)s.%(funcName)s:%(lineno)s |> %(message)s"
log_datefmt = "%Y-%m-%d_%H-%M-%S"

[logging]
## Override logging settings by redefining them here
log_level = "DEBUG"

```

Then, in a file (i.e. a `settings.py` file), load the settings:

```python
## example.py

LOGGING_SETTINGS = Dynaconf(
    ## Tell Dynaconf to load from environments, defined in settings.toml
    #  like [env_name]
    environments=True,
    ## Tell Dynaconf to look in a section named [logging]
    env="logging",
    ## Tell Dynaconf to look for variables prepended with "LOG_"
    envvar_prefix="LOG",
    ## Tell Dynaconf to read configurations from the file ./config/settings.toml
    #  Dynaconf will load from the environment first, then from any files with .local.toml in the name
    settings_files=["settings.toml", ".secrets.toml"]
)

```

To get a configuration value from this new `LOGGING_SETTINGS` object, you can use Dynaconf's `.get()` method:

```python
## example.py

...

## Try to load a variable "log_level" from settings.toml or the environment,
#  use "INFO" if neither can be found
log_level = LOGGING_SETTINGS.get("LOG_LEVEL", default="INFO")
```

Setting defaults with the `.get()` method can help ensure your program doesn't crash on missing environment variables.
