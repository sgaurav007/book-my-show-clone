from pydantic import BaseModel


class CityResponse(BaseModel):
    name: str
    theater_count: int
