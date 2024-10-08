from __future__ import annotations

import typing as t

import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as so

## Generic type representing an instance of a class
T = t.TypeVar("T")


class Base(so.DeclarativeBase):
    pass


class BaseRepository(t.Generic[T]):
    """Base class for a SQLAlchemy database repository.

    Usage:
        When creating a new repository class, inherit from this BaseRepository.
        The new class will have sessions for create(), get(), update(), delete(), and list().
    """

    def __init__(self, session: so.Session, model: t.Type[T]):
        self.session = session
        self.model = model

    def create(self, obj: T) -> T:
        self.session.add(obj)

        self.session.commit()
        self.session.refresh(obj)

        return obj

    def get(self, id: int) -> t.Optional[T]:
        return self.session.get(self.model, id)

    def update(self, obj: T, data: dict) -> T:
        for key, value in data.items():
            setattr(obj, key, value)

        self.session.commit()

        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)

        self.session.commit()

    def list(self) -> list[T]:
        return self.session.execute(sa.select(self.model)).scalars().all()

    def count(self) -> int:
        """Return the count of entities in the table."""
        return self.session.query(self.model).count()
