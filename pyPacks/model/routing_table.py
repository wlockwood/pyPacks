import unittest
import re
from typing import List, Dict
from model.location import Location


class RoutingTable(object):
    """
    Routing table will allow a quick distance lookup between two locations.
    It should implement a lookup(a,b) function that will look up the distance between two locations by integer id.
    lookup() will automatically check the swapped values.
    """

    # Looking back, this really should have been a two-dimensional array.
    # TODO: Display routing table, attempt two.

    def __init__(self, location_list):
        self.inner_table = dict()  # Empty dictionary
        self.locations = location_list

        for source_loc in self.locations:
            for dest_loc in source_loc.distances:
                src = source_loc.id
                dest = int(dest_loc)
                distance = source_loc.distances[dest_loc]

                if distance > 0:
                    self.set_route_distance(src, dest, distance)

    def set_route_distance(self, id1: int, id2: int, distance) -> None:
        """Add or update the distance between two places."""
        self.inner_table[self.make_key(id1, id2)] = distance

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

    def get_all_routes_from_id(self, routes_from_id: int) -> Dict[int, int]:
        """Returns a dictionary of destinations from this id, with distances as values"""
        output = {}
        for k, v in self.inner_table.items():
            if re.search(rf"(^{routes_from_id}-)", k):  # Search forwards and reverse
                partial_key = int(re.sub(rf"^{routes_from_id}-", "", k))
            if re.search(rf"-{routes_from_id}$", k):
                partial_key = int(re.sub(rf"-{routes_from_id}$", "", k))
            output[partial_key] = v
        return output

    def get_nearest_neighbor_by_id(self, id1: int, ignore_node_ids: List[int] = []) -> int:
        routes = self.get_all_routes_from_id(id1)
        for ignore_key in ignore_node_ids:
            del routes[ignore_key]
        nearest_id = min(routes, key=routes.get)
        # nearest_id = min([x for x in starting_point_distances if x not in ignore_node_ids])
        distance = routes[nearest_id]
        if len(ignore_node_ids) > 0:
            print(f"Nearest neighbor to {id1} is {nearest_id}, {distance} miles away, ignoring {ignore_node_ids}")
        else:
            print(f"Nearest neighbor to {id1} is {nearest_id}, {distance} miles away")
        return nearest_id

    def get_nearest_neighbor(self, start: Location, ignore_locations: List[Location] = []) -> Location:
        """Wrapper for get_nearest_neighbor_by_id that handles remapping the object."""
        nearest_id = self.get_nearest_neighbor_by_id(Location.id, [x.id for x in ignore_locations])
        return next(x for x in self.locations if x.id == start.id)

    def get_nearest_neighbor_of_set(self, start: Location, other_locs: List[Location]) -> Location:
        distances = {}
        for i in other_locs:
            distances[i] = self.lookup(start.id, i.id)
        return min(distances, key=distances.get)

    @staticmethod
    def make_key(id1, id2):
        return f"{str(id1)}-{str(id2)}"
