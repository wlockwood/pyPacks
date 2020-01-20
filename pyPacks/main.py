
from data_loader import read_packages, read_locations
from model.routing_table import RoutingTable
from model.truck import Truck
from model.sim_time import SimTime

sim_time = SimTime(800)  # Global time tracker

# Initial data load
locations = read_locations("sample_locations.csv")
packages = read_packages("sample_packages.csv", locations, sim_time)
routing_table = RoutingTable(locations)  # Build location+location distance lookup hash table



trucks = [Truck(1), Truck(2)]  # Build trucks. There's a third truck, but I think it's an error in the instructions.


"""
Flow:
Build suggested delivery pattern
Execute delivery pattern until delayed package time is hit
"""

# TODO: Quick stats
# TODO: Build main time loop? Don't use a time loop?
# TODO: Print snapshots of current package status
# TODO: Print snapshots of truck location
