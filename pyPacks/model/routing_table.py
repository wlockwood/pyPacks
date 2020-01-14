import unittest

class RoutingTable(object):
    """
    Routing table will allow a quick distance lookup between two locations.
    It should implement a lookup(a,b) function that will look up the distance between two locations by integer id.
    lookup() will automatically check the swapped values.
    """

    # Looking back, this really should have been a two-dimensional array.
    # TODO: Unit tests! ... right?
    # TODO: Display routing table, attempt two.
    # TODO: get_nearest_neighbor(). Takes in a location id, returns the nearest location id.
    # TODO: Maybe route calculation should be in this class?

    def __init__(self, location_list):
        self.table = dict()  # Empty dictionary
        self.locations = location_list

        for source_loc in self.locations:
            for dest_loc in source_loc.distances:
                src = source_loc.location_id
                dest = int(dest_loc)
                distance = source_loc.distances[dest_loc]

                if distance > 0:
                    self.set_route_distance(src, dest, distance)
                    print(f"Added {src}, {dest}, {distance}")

    def set_route_distance(self, id1: int, id2: int, distance) -> None:
        """Add or update the distance between two places."""
        self.table[self.make_key(id1, id2)] = distance

    def remove_route(self,id1: int, id2: int):
        """Removes a route and its reverse."""
        self.table.pop(self.make_key(id1, id2))
        self.table.pop(self.make_key(id2, id1))

    def lookup(self, id1: int, id2: int) -> int:
        print(f"Trying to find the distance between {id1} and {id2}...")
        output = self.table.get(self.make_key(id1, id2))
        if(output == None):
            output = self.table.get(self.make_key(id2, id1))

        if(output == None):
            print("No route found.")
        else:
            print(f"Distance between {id1} and {id2}: {output}")

        return output

    @staticmethod
    def make_key(id1, id2):
        return f"{str(id1)}-{str(id2)}"

class Test_RoutingTable(unittest.TestCase):
    def test_make_key(self):
        valid_key = "1-2"
        made_key = RoutingTable.make_key(1,2)
        self.assertEqual(valid_key, made_key)

    def test_set_lookup_distance(self):
        routing = RoutingTable([])
        routing.set_route_distance(1, 2, 10)
        stored_dist = routing.lookup(1, 2)
        self.assertEqual(10, stored_dist)

