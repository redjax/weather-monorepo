from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from .models import ForecastJSONModel

from core.db.base import BaseRepository
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

class ForecastJSONRepository(BaseRepository):
    def __init__(self, session: so.Session):
        super().__init__(session, ForecastJSONModel)
