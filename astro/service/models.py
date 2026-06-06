"""Request/response models for the HTTP service."""

from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel, Field

from engine.birth_data import BirthData


class BirthInput(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: Union[str, float]      # IANA name or fixed UTC offset in hours
    fold: int = 0
    name: str = ""

    def to_birth(self) -> BirthData:
        return BirthData(
            self.year, self.month, self.day, self.hour, self.minute, self.second,
            self.latitude, self.longitude, self.timezone, fold=self.fold,
            name=self.name)


class ChartRequest(BirthInput):
    system: str = "vedic"            # "vedic" | "kp"


class VargaRequest(BirthInput):
    code: str = "D9"


class DashaRequest(BirthInput):
    depth: int = 2


class DashaAtRequest(BirthInput):
    date: str                        # ISO date, e.g. "2025-06-01"


class HouseRequest(BirthInput):
    house: int = Field(..., ge=1, le=12)


class EventRequest(BirthInput):
    event: str                       # marriage / career / ...


class SensitivityRequest(BirthInput):
    minutes: float = 2.0


class AskRequest(BirthInput):
    question: str
