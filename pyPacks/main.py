from itertools import groupby
from data_loader import read_packages, read_locations
from model.routing_table import RoutingTable
from model.truck import Truck
from model.sim_time import SimTime

sim_time = SimTime(800)  # Global time tracker

# Initial data load
packages = read_packages("sample_packages.csv", sim_time)
locations = read_locations("sample_locations.csv")
routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table

# Associate packages to location objects
keyfunc = lambda x: x.dest_address
sortedPacks = sorted(packages, key=keyfunc)
for k, v in (groupby(sortedPacks, keyfunc)):
    print("Location {} has {} packages".format(k, sum(1 for x in v)))  # The other modern string format, for practice

trucks = [Truck(1), Truck(2)]  # Build trucks. There's a third truck, but I think it's an error in the instructions.

routing_table.get_nearest_neighbor(1)
routing_table.get_nearest_neighbor(1, [16])


"""
Flow:
Build suggested delivery pattern
Execute delivery pattern until delayed package time is hit
"""

# TODO: Quick stats
# TODO: Build main time loop? Don't use a time loop?
# TODO: Print snapshots of current package status
# TODO: Print snapshots of truck location
