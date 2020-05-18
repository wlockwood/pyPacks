from typing import List
from abc import ABC, abstractmethod
from model.location import Location


class IRoutingTable(ABC):
    def __init__(self, location_list):
        self.locations = list(location_list)

    @abstractmethod
    def set_route_distance(self, id1: int, id2: int, distance: float):
        pass

    @abstractmethod
    def lookup(self, id1: int, id2: int) -> float:
        pass

    @abstractmethod
    def get_all_routes_from_id(self, id1: int) -> List:
        pass

    def get_nearest_neighbor_by_id(self, start: int, ignore_node_ids: List[int] = []) -> int:
        routes = self.get_all_routes_from_id(start)
        for ignore_key in ignore_node_ids:
            del routes[ignore_key]
        nearest_id = min(routes)
        # nearest_id = min([x for x in starting_point_distances if x not in ignore_node_ids])
        distance = routes[nearest_id]
        if len(ignore_node_ids) > 0:
            print(f"Nearest neighbor to {start} is {nearest_id}, {distance} miles away, ignoring {ignore_node_ids}")
        else:
            print(f"Nearest neighbor to {start} is {nearest_id}, {distance} miles away")
        return nearest_id

    def get_nearest_neighbor(self, start: Location, ignore_locations: List[Location] = []) -> Location:
        """Wrapper for get_nearest_neighbor_by_id that handles remapping the object."""
        nearest_id = self.get_nearest_neighbor_by_id(start.loc_id, [x.loc_id for x in ignore_locations])
        return next(x for x in self.locations if x.id == start.loc_id)

    def get_nearest_neighbor_of_set(self, start: Location, other_locs: List[Location]) -> Location:
        distances = {}
        for loc in other_locs:
            distances[loc] = self.lookup(start.loc_id, loc.loc_id)
        return min(distances, key=distances.get)
