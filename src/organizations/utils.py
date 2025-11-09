
import re
from decimal import Decimal
from math import radians, sin, cos, atan2, sqrt

from fastapi import HTTPException
from starlette import status


def check_latitude(latitude: str | None) -> str | None:
    """Check latitude."""
    pattern = re.compile(r'-?\d{1,2}(\.\d+)?')
    if latitude is not None:
        if not pattern.match(latitude):
            error = [{'field': 'latitude', 'message': 'Latitude should be in format 00.0000'}]
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, error)
    return latitude


def check_longitude(longitude: str | None) -> str | None:
    """Check longitude."""
    pattern = re.compile(r'-?\d{1,3}(\.\d+)?')
    if longitude is not None:
        if not pattern.match(longitude):
            error = [{'field': 'longitude', 'message': 'Longitude should be in format 000.0000'}]
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, error)
    return longitude


def haversine(lat1: Decimal, lon1: Decimal, lat2: Decimal, lon2: Decimal) -> float:
    """Calculate distance between two pair coordinates."""
    earth_radius = 6371
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    distance = 2 * earth_radius * atan2(sqrt(a), sqrt(1 - a))
    return distance
