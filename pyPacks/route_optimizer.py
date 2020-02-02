from typing import List, Set, Callable
import time
from model.location import Location
from model.routing_table import RoutingTable

"""
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

 Metrics:
 - Total miles driven
 - Total time taken
 - Miles per package and time per package
 - Time per location
 
Note: In most cases, I've chosen implementations by simplicity of explanation rather than speed.
      This is due to the fact that I have to explain the time and space complexity of each optimization algorithm
      in a paper. With more time, I'd use a heap sort to turn most functions in this class into O(1) from O(n) by
      making a priority queue of locations by distance from each other location. 
"""


class RouteOptimizer(object):
    # Both bfs_cutoffs were determined experimentally. One thread at 3.9GHz
    bfs_cutoff_fast = 7  # How many locations can BFS do in under a second?
    bfs_cutoff_slow = 8  # How many locations can BFS do in under ten seconds?

    def __init__(self, route_locs: List[Location], route_table: RoutingTable, hub: Location):
        self.route_locs = []

        # Deduplicate locations
        for l in route_locs:
            if l not in self.route_locs:
                self.route_locs.append(l)
        # print(f"{len(route_locs)} locations, {len(self.route_locs)} distinct.")
        self.route_table = route_table
        self.hub = hub

    def get_optimized_smart(self):
        """Select algorithm from options and attempt to return best viable.
        Run BFS if viable, or best of NN and CPM."""
        length = len(self.route_locs)
        if length < self.bfs_cutoff_slow:
            print(f"Smart router chose breadth-first search ({length} locs)")
            return self.get_optimized_bfs()  # O(n!)
        else:
            nn = self.get_optimized_nn()  # O(n^2)
            nn_dist = sum(self.get_route_distances(nn))
            cpm = self.get_optimized_cpm()  # O(n^3)
            cpm_dist = sum(self.get_route_distances(cpm))
            if cpm_dist == nn_dist:
                print(f"Smart router chose ASCP/NN as both were identical at {cpm_dist:.2f} miles.")
                return cpm
            elif cpm_dist < nn_dist:
                print(f"Smart router chose antisocial coproximity, "
                      f"{length} locs. ASCP:{cpm_dist:.2f} NN: {nn_dist:.2f}")
                return cpm
            else:
                print(f"Smart router chose nearest neighbor, "
                      f"{length} locs. ASCP:{cpm_dist:.2f} NN: {nn_dist:.2f}")
                return nn

    def get_optimized_cpm(self):
        """
        Uses the antisocial coproximity metric ("closest to me, farthest from everything else") heuristic.
        Usually better than nearest-neighbor in terms of total path length.
        CPU complexity is roughly O(n^3), proved out by experimentation.
        """
        size = len(self.route_locs) + 2
        output = [self.hub] * size

        remaining_locations = self.route_locs.copy()
        index = 1
        while True:
            if len(remaining_locations) == 0:
                break
            my_cpms = self.get_list_coproximities(output[index - 1], remaining_locations)
            output[index] = my_cpms[0][0]  # Takes largest CPM's location
            remaining_locations.remove(output[index])
            index += 1
        return output

    def get_optimized_nn(self):
        """
        Uses nearest neighbor. O(n^2)
        """
        size = len(self.route_locs) + 2
        output = [self.hub] * size

        remaining_locations = self.route_locs.copy()
        index = 1
        while True:
            if len(remaining_locations) == 0:
                break
            output[index] = self.get_nearest_to(output[index - 1], remaining_locations)
            remaining_locations.remove(output[index])
            index += 1
        return output

    def get_optimized_bfs(self, remaining_locations: List[Location] = None, path_so_far: List[Location] = None,
                          best_complete_path: List[Location] = None, best_dist: List[float] = None):
        """Brute-force or breadth-first search. Should be O(n!) and experimentation proves that out.
        Can only handle up to 8 nodes before exceeding ten seconds, but could prune known-bad to improve speed.
        Threading at the top level is an easy win for DoP-fold speedup."""
        # Initialization
        if path_so_far is None:
            path_so_far = [self.hub]
        if remaining_locations is None:
            remaining_locations = self.route_locs
        if best_dist is None:
            best_dist = [float("inf")]

        # Base case
        if len(remaining_locations) == 0:
            path_so_far.append(self.hub)
            distances = self.get_route_distances(path_so_far)
            total = sum(distances)
            # print(f"Completed path of {total:.2f} miles: ", ', '.join(str(x.loc_id) for x in path_so_far))
            return path_so_far

        child_paths = []
        for loc in remaining_locations:
            my_children = [x for x in remaining_locations if x != loc]
            psf = path_so_far.copy()
            psf.append(loc)
            # print("PSF: ", ', '.join(str(x.loc_id) for x in psf))
            my_path = self.get_optimized_bfs(my_children, psf)
            child_paths.append(my_path)

        best_child_dist = float("inf")
        best_child_path = []
        for path in child_paths:
            total = sum(self.get_route_distances(path))
            if total < best_child_dist:
                best_child_path = path
                best_child_dist = total
        return best_child_path

    def find_furthest_from(self, base_loc: Location):
        farthest_so_far: Location = 0
        farthest_dist: float = 0
        for loc in self.route_locs:
            my_dist = self.route_table.lookup(loc.loc_id, base_loc.loc_id)
            if my_dist > farthest_dist:
                farthest_dist = my_dist
                farthest_so_far = loc
                print(f"{loc} is now farthest from {base_loc.name} at {my_dist} miles.")
        return farthest_so_far

    def get_average_distance_from_others(self, base_loc: Location):
        total = 0.0
        for loc in self.route_locs:
            if loc == base_loc:  # Skip self
                continue
            total += self.route_table.lookup(loc.loc_id, base_loc.loc_id)
        return total / len(self.route_locs)

    def get_nearest_to(self, base_loc: Location, of_set=[]):
        my_set = of_set or self.route_locs

        closest_so_far: Location = None
        closest_dist: float = float("inf")
        for loc in my_set:
            my_dist = self.route_table.lookup(loc.loc_id, base_loc.loc_id)
            if my_dist is None:
                print(f"Looking up {loc.loc_id} to {base_loc.loc_id} failed")
            if my_dist < closest_dist:
                closest_dist = my_dist
                closest_so_far = loc
        return closest_so_far

    def get_coproximity_metric(self, base_loc: Location, compare_loc: Location):
        """How close is a node to me relative to how far it is from other nodes?"""
        dist_from_base = self.route_table.lookup(base_loc.loc_id, compare_loc.loc_id)  # O(1), lookup
        average_from_others = self.get_average_distance_from_others(compare_loc)  # O(n), scan
        output = average_from_others / dist_from_base
        # print(f"{compare_loc.shortname} is {dist_from_base} miles from {base_loc.shortname} and "
        #       f"averages {average_from_others:.1f} from others. CPM = {output:.2f}")
        return output

    def get_list_coproximities(self, base_loc, of_set: List[Location] = []):
        cpms = {}
        for loc in of_set:  # O(n^2) now, since it's looping through a loop
            cpms[loc] = (self.get_coproximity_metric(base_loc, loc))  # O(n)
        return sorted(cpms.items(), key=lambda x: x[1], reverse=True)

    def print_route_evaluation(self, description: str, route: List[Location], elapsed: float = 0):
        route = route.copy()

        # Unoptimized routes don't have the hub
        if route[0] is not self.hub:
            route.insert(0, self.hub)
        if route[-1] is not self.hub:
            route.append(self.hub)

        distances = self.get_route_distances(route)
        total = sum(distances)
        print(f"Opt type: {description:^25}\tTotal: {total:.2f}\tTime to drive: {(total / 18):.1f}h"
              f"\tCalc time: {elapsed * 1000:5.3f}ms")

    def get_route_distances(self, route: List[Location]) -> List[float]:
        i = 0
        distances: List[float] = []
        while i < (len(route) - 1):
            next = self.route_table.lookup(route[i].loc_id, route[i + 1].loc_id)
            if next is not None:
                distances.append(next)
            i += 1
        return distances

    def run_time_test(self, description: str, method: Callable, test_count: int = 10000):
        times = []
        for i in range(1, test_count):
            start = time.perf_counter()
            self.get_optimized_nn()
            stop = time.perf_counter()
            times.append(stop - start)
        total = sum(times) * 1000
        average = total / len(times)
        average_per_n = average / (len(self.route_locs) + 2)  # Two extra for hub at each end
        mint = min(times) * 1000
        maxt = max(times) * 1000
        print(f"{description:^15}Total: {total:>8,.2f}\tMean: {average:>8.3f}\tMean/n: {average_per_n:>8.3f}\t"
              f"Min/max: {mint:.3f}/{maxt:.3f}")

    def run_time_tests(self, test_count: int = 10000):
        print(f"-- Time tests ({len(self.route_locs)} locations, {test_count} runs) - All times ms --")
        self.run_time_test("NearestN", self.get_optimized_nn, test_count)
        self.run_time_test("Coproximity", self.get_optimized_cpm, test_count)
        if len(self.route_locs) <= RouteOptimizer.bfs_cutoff_fast:
            self.run_time_test("BFS / Brute x5", self.get_optimized_bfs(), 5)
