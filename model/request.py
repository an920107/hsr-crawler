from model.station import Station

from datetime import datetime
from pydantic import BaseModel, model_validator


class SearchRequest(BaseModel):
    station_from: Station
    station_to: Station
    adult_count: int = 0
    child_count: int = 0
    heart_count: int = 0
    elder_count: int = 0
    student_count: int = 0
    departure: datetime

    @model_validator(mode="after")
    def check_count_has_value(cls, values: 'SearchRequest'):
        values.departure.replace(tzinfo=None)

        if values.station_from == values.station_to:
            raise ValueError(
                "`station_from` and `station_to` should be different")
        if values.adult_count | values.child_count | values.heart_count | values.elder_count | values.student_count == 0:
            raise ValueError(
                "At least one of the values of `adult_count`, `child_count`, `heart_count`, `elder_count`, `student_count` should be set more than 0.")
        if not 0 <= values.adult_count <= 10:
            raise ValueError(
                "The value of `adult_count` should be between 0 and 10.")
        if not 0 <= values.child_count <= 10:
            raise ValueError(
                "The value of `child_count` should be between 0 and 10.")
        if not 0 <= values.heart_count <= 10:
            raise ValueError(
                "The value of `heart_count` should be between 0 and 10.")
        if not 0 <= values.elder_count <= 10:
            raise ValueError(
                "The value of `elder_count` should be between 0 and 10.")
        if not 0 <= values.student_count <= 10:
            raise ValueError(
                "The value of `student_count` should be between 0 and 10.")
        if values.departure < datetime.today():
            raise ValueError(
                "The date of `departure` should not be before today.")
        if 1 <= values.departure.hour <= 4:
            raise ValueError(
                "The hour of `departure` should not be between 1 and 4.")
        return values


class BookRequest(BaseModel):
    selected_index: int
    id_card_number: str
    phone: str
    email: str
