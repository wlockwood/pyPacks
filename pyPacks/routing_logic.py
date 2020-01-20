""" Routing logic
 - Group undelivered packages by location and availability
 - Pick the farthest package from the hub with achievable constraints and the earliest deadline
 - Find nearest neighbor groups until truck is full (nearest-neighbor should use a heap)
 - - Make sure no location is partially loaded on a truck
 - Once truck is full, add "return to hub" to location node list and brute-force the best route.

 Constraints and requirements
 - Must be able to recalculate at an arbitrary time. Recalculation shouldn't interrupt package delivery.
 - Some packages must be delivered with other specified packages. "Linked packages"
 - Some packages will arrive late and can't be picked up until a specified time.
 - Some packages can only be on certain trucks.

Possible Upgrades:
 - If truck approaches within x miles of hub with less than y% capacity, pick up more packages.
    This could be implemented by checking to see if a route X->Y is longer than X->Hub. Only do this if packages
    that can be picked up are close to other routed nodes.
 - Maybe: If deadlines for special constraint packages can't be met reliably, add a "truck holding pattern"
    option that keeps it nearby or at the hub.
 - Maybe: Try alternate starting points to see if that results in a more optimal result.
 - Maybe: If X->Y is not significantly longer than X->M->Y, trim X->Y?
 - Maybe: Check if any nodes are closer to our nodes than the ones we have selected?

 Metrics:
 - Total miles driven
 - Total time taken
 - Miles per package and time per package
 - Time per location

"""
from itertools import groupby


class RouteBuilder(object):

    def __init__(self, locations, packages, trucks, routing_table):
        self.locations = locations
        self.packages = packages
        self.trucks = trucks
        self.table = routing_table

    def group_packages(self):
        """Group undelivered packages by location and availability."""
        # Associate packages to location objects
        keyfunc = lambda x: x.dest_address
        sortedPacks = sorted(self.packages, key=keyfunc)
        for k, v in (groupby(sortedPacks, keyfunc)):
            print("Location {} has {} packages".format(k, sum(
                1 for x in v)))  # The other modern string format, for practice

    def choose_starting_group(self):
        """Pick the farthest unconstrained package from the hub, prioritizing earlier deadlines."""
        raise NotImplementedError("choose_starting_group")

    def recalculate_route(self):
        print("This should recalculate the route. Not yet implemented.")
        raise NotImplementedError("Recalculate route")

    def build_route(self):
        raise NotImplementedError("build_route")
