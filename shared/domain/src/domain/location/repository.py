from __future__ import annotations

import logging
import typing as t

log = logging.getLogger(__name__)

from core.db.base import BaseRepository

from .models import LocationModel

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so


class LocationRepository(BaseRepository[LocationModel]):
    def __init__(self, session: so.Session):
        super().__init__(session, LocationModel)

    def get_by_id(self, id: int) -> LocationModel | None:
        return (
            self.session.query(LocationModel)
            .filter(LocationModel.id == id)
            .one_or_none()
        )

    def get_by_country(self, country: str) -> list[LocationModel] | None:
        return (
            self.session.query(LocationModel)
            .filter(LocationModel.country == country)
            .all()
        )

    def get_by_country_and_state(
        self, state: str, country: str
    ) -> LocationModel | None:
        return (
            self.session.query(LocationModel)
            .filter(LocationModel.country == country and LocationModel.name == state)
            .one_or_none()
        )
