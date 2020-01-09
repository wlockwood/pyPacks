import re

class Location(object):
    def __init__(self, location_id, name, address, distance_array):
        self.location_id = location_id
        self.name = name

        # Parse address into street and zip
        address_parts = [part.strip() for part in re.split('[\(\)]',address) if part.strip()]
        self.address = address_parts[0]
        self.zip = address_parts[1]

        self.distance_array = distance_array

    def __repr__(self):
        return f"Location({self.location_id},{self.address},{self.zip},{self.delivery_deadline},{self.notes})"

    def __str__(self):
        return f"({self.location_id},{self.name},{self.delivery_deadline},{self.notes})"
