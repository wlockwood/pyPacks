import re

class Location(object):
    def __init__(self, location_id, name, address, distances):
        self.location_id = location_id
        self.name = name

        # Parse address into street and zip
        address_parts = [part.strip() for part in re.split('[\(\)]',address) if part.strip()]
        self.address = address_parts[0]
        self.zip = address_parts[1]

        self.distances = distances

    def __repr__(self):
        return f"Location({self.location_id},{self.name},{self.distances})"

    def __str__(self):
        return f"({self.location_id},{self.name},{self.distances})"
