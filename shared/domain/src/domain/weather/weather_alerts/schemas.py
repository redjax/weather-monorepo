from __future__ import annotations

from pydantic import BaseModel

class WeatherAlertIn(BaseModel):
    headline: str | None = None
    msgtype: str | None = None
    severity: str | None = None
    urgency: str | None = None
    areas: str | None = None
    category: str | None = None
    certainty: str | None = None
    event: str | None = None
    note: str | None = None
    effective: str | None = None
    expires: str | None = None
    description: str | None = None
    instruction: str | None = None


class WeatherAlertOut(WeatherAlertIn):
    id: int


class WeatherAlertsIn(BaseModel):
    alert: list[WeatherAlertIn] = []


class WeatherAlertsOut(WeatherAlertsIn):
    id: int
