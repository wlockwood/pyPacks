import re

class Location(object):
    def __init__(self, id, name, address, distances):
        self.id = id
        self.name = name

        # Parse address into street and zip
        address_parts = [part.strip() for part in re.split('[\(\)]',address) if part.strip()]
        self.address = address_parts[0]
        self.zip = address_parts[1]

        self.distances = distances

    def __repr__(self):
        return f"Location({self.id},{self.name})"

    def __str__(self):
        return f"({self.id},{self.name})"
