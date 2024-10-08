# Scripts

Scripts can import code from [`packages/`](../packages/) or [`shared/`](../shared/), and serve as repeatable entrypoints into the repo's code. For example, [`count_current_weather_rows.py`](./count_current_weather_rows.py) imports from [`packages/weatherapi_client`](../packages/weatherapi-client/), [`core.setup`](../shared/core/src/core/setup/), and the [`celery-app`](../packages/celery-app/) package. The script uses these code modules to count the number of current_weather rows in the database, utilizing `celery` and `sqlalchemy`.
