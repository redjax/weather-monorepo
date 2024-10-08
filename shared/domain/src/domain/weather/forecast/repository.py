import logging
import typing as t

log = logging.getLogger(__name__)

from core.db.base import BaseRepository

from .models import ForecastJSONModel

import sqlalchemy as sa
import sqlalchemy.orm as so
import sqlalchemy.exc as sa_exc


class ForecastJSONRepository(BaseRepository):
    def __init__(self, session: so.Session):
        super().__init__(session, ForecastJSONModel)
