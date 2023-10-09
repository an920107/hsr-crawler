from model.discount import Discount

from datetime import time
from pydantic import BaseModel


class Train(BaseModel):
    departure: time
    arrival: time
    no: int
    discounts: list[Discount]
