import re
from typing import List, Dict
from model.location import Location
from model.i_routing_table import IRoutingTable
from pprint import pprint as pp

class RoutingTableArray(IRoutingTable):
    """
    (Array-based) Routing table will allow a quick distance lookup between two locations.
    It should implement a lookup(a,b) function that will look up the distance between two locations by integer id.
    lookup() will automatically check the swapped values.
    """

    def __init__(self, location_list):

        super().__init__(location_list)

        size = len(location_list)

        # Empty square array
        self.inner_table: List[List[float]] = [[-1 for i in range(size + 1)] for j in range(size + 1)]

        for source_loc in self.locations:
            for dest_loc in source_loc.distances:
                src = source_loc.loc_id
                dest = int(dest_loc)
                distance = source_loc.distances[dest_loc]

                self.set_route_distance(src, dest, distance)

        """ # Likely optimization path, but not currently in use
        self.min_list_by_location: List[List[Location]] = []
        for base_loc in self.locations:
            list_from_base = sorted(location_list, key=lambda l: self.lookup(base_loc.loc_id, l.loc_id))
            del list_from_base[0]  # Remove self-distance
            self.min_list_by_location[base_loc.loc_id] = list_from_base
        """



    def set_route_distance(self, id1: int, id2: int, distance: float):
        self.inner_table[id1][id2] = distance
        self.inner_table[id2][id1] = distance

    def lookup(self, id1: int, id2: int) -> float:
        return self.inner_table[id1][id2]

    def get_all_routes_from_id(self, id1: int) -> List:
        return self.inner_table[id1]

    def __repr__(self):
        return f"Routing table with {len(self.inner_table)-1} locations"