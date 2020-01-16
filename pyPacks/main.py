from data_loader import read_packages, read_locations
from itertools import groupby
import model.routing_table

# Initial data load
packages = read_packages("sample_packages.csv")
locations = read_locations("sample_locations.csv")

# Build location+location distance lookup hash table
routing = model.routing_table.RoutingTable(locations)


exit(0)

# Associate packages to location objects
keyfunc = lambda x: x.dest_address
sortedPacks = sorted(packages, key=keyfunc)

for k, v in (groupby(sortedPacks, keyfunc)):
    print("Location {} has {} packages".format(k, sum(1 for x in v)))

# TODO: Quick stats
# TODO: Build main time loop
# TODO: Print snapshots of current package status
# TODO: Print snapshots of truck location



