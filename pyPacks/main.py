from data_loader import load_packages, load_locations
from itertools import groupby
import model.routing_table

# Initial data load
packages = load_packages("sample_packages.csv")
locations = load_locations("sample_locations.csv")

# Build location+location distance lookup hash table
routing = model.routing_table.RoutingTable(locations)

print(routing)

exit(0)

# Associate packages to location objects
keyfunc = lambda x: x.dest_address
sortedPacks = sorted(packages, key=keyfunc)

for k, v in (groupby(sortedPacks, keyfunc)):
    print("Location {} has {} packages".format(k, sum(1 for x in v)))

# TODO: Quick stats

