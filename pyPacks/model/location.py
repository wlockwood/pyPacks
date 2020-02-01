from typing import List
import random
import re


class Location(object):
    loc_count = 0

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

        Location.loc_count += 1

    @classmethod
    def generate_fake_locations(cls, count: int = 10) -> List['Location']:
        id_offset = 100
        print("Loc count:", cls.loc_count)
        output = []
        for i in range(1, count):
            my_id = cls.loc_count + id_offset
            distances = {}
            for j in range(1, Location.loc_count + id_offset):
                distances[j]=(random.random() * 10 % 50)
            output.append(Location(my_id, f"Fake loc: {my_id:,d}", "no address,00000", distances))
        return output

    def __repr__(self):
        return f"Location({self.loc_id},{self.name})"

    def __str__(self):
        return f"({self.loc_id},{self.name})"
