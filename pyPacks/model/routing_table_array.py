import re
from typing import List, Dict
from model.location import Location
from model.routing_table import RoutingTable


class RoutingTableArray:
    """
    (Array-based) Routing table will allow a quick distance lookup between two locations.
    It should implement a lookup(a,b) function that will look up the distance between two locations by integer id.
    lookup() will automatically check the swapped values.
    """

    def __init__(self, location_list):

        self.inner_table = dict()  # Empty dictionary
        self.locations = location_list

        for source_loc in self.locations:
            for dest_loc in source_loc.distances:
                src = source_loc.loc_id
                dest = int(dest_loc)
                distance = source_loc.distances[dest_loc]

                if distance > 0:
                    self.set_route_distance(src, dest, distance)