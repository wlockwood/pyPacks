from texttable import Texttable

class RoutingTable(object):
    """
    Routing table will allow a quick distance lookup between two locations.
    It should implement a lookup(a,b) function that will look up the distance between two locations by integer id.
    lookup() will automatically check the swapped values.
    """

    # TODO: Add method descriptions. How? Docstrings?


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

    def set_route_distance(self, id1, id2, distance):
        self.table[self.make_key(id1, id2)] = distance

    def lookup(self, id1, id2):
        print(f"Trying to find the distance between {id1} and {id2}...")
        output = self.table.get(self.make_key(id1, id2), self.make_key(id2, id1))

        # table.get returning nothing for some reason returns the key that was attempted. Dunno.
        if output == self.make_key(id1, id2) or output == self.make_key(id2, id1):
            return None
        return output

    def display(self):
        # Build headers
        header_list = ["Name"]
        for loc in self.locations:
            header_list.append(loc.name[0:5])

        # Build data rows


        t_printer = Texttable()
        t_printer.add_rows(rows=[[]])

    @staticmethod
    def make_key(id1, id2):
        return f"{str(id1)}-{str(id2)}"
