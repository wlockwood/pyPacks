from typing import List
import re


class Location(object):
    def __init__(self, location_id: int, name: str, address, distances):
        self.loc_id: int = location_id
        self.name = name
        self.shortname = name\
            .replace("Salt Lake", "SL")\
            .replace("Western Governors University", "WGU")\
            .replace("City", "C")[:15]
        # Parse address into street and zip. Hub has no address.

        address_parts = [part.strip() for part in re.split(r'[\(\)]', address) if part.strip()]
        self.address = address_parts[0]
        if len(address_parts) > 1:
            self.zip = address_parts[1]
        else:
            self.zip = ""
        self.distances = distances

    def __repr__(self):
        return f"Location({self.loc_id},{self.name})"

    def __str__(self):
        return f"({self.loc_id},{self.name})"
