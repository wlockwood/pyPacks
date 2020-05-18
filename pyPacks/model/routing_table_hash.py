import unittest
import re
from typing import List, Dict
from model.location import Location
from model.i_routing_table import IRoutingTable


class RoutingTableHash(IRoutingTable):
    """
    (Hash-based) Routing table will allow a quick distance lookup between two locations.
    It should implement a lookup(a,b) function that will look up the distance between two locations by integer id.
    lookup() will automatically check the swapped values.
    """

    # Looking back, this really should have been a two-dimensional array.

    def __init__(self, location_list):
        super().__init__(location_list)

        self.inner_table = dict()  # Empty dictionary

        for source_loc in self.locations:
            for dest_loc in source_loc.distances:
                src = source_loc.loc_id
                dest = int(dest_loc)
                distance = source_loc.distances[dest_loc]

                if distance > 0:
                    self.set_route_distance(src, dest, distance)

    def set_route_distance(self, id1: int, id2: int, distance) -> None:
        """Add or update the distance between two places."""
        self.inner_table[self.make_key(id1, id2)] = distance
        self.inner_table[self.make_key(id2, id1)] = distance

    def remove_route(self, id1: int, id2: int):
        """Removes a route and its reverse."""
        self.inner_table.pop(self.make_key(id1, id2), None)
        self.inner_table.pop(self.make_key(id2, id1), None)

    def lookup(self, id1: int, id2: int) -> int:
        output = self.inner_table.get(self.make_key(id1, id2), None)
        if output is None:
            output = self.inner_table.get(self.make_key(id2, id1), None)
        if output is None:
            print(f"No route found between {id1} and {id2}!")
        return output

    def get_all_routes_from_id(self, routes_from_id: int) -> List[float]:
        """Returns a dictionary of destinations from this id, with distances as values"""
        output = {}
        for k, v in self.inner_table.items():
            partial_key = ""
            if re.search(rf"(^{routes_from_id}-)", k):  # Search forwards and reverse
                partial_key = int(re.sub(rf"^{routes_from_id}-", "", k))
            if re.search(rf"-{routes_from_id}$", k):
                partial_key = int(re.sub(rf"-{routes_from_id}$", "", k))
            output[partial_key] = v
        return output



    @staticmethod
    def make_key(id1, id2):
        return f"{str(id1)}-{str(id2)}"
