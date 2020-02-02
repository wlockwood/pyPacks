import csv
import re
from typing import List
from model.package import Package, PackageStatus, PackageLogEntry
from model.location import Location
from model.sim_time import SimTime


def read_locations(source_file_name: str):
    """Loads locations from the specified CSV file and returns a collection of location instances.
    :param source_file_name: The CSV file to load.
    """
    with open(source_file_name) as location_file:
        location_reader = csv.DictReader(location_file)
        output_locations = []

        int_fieldnames = [i for i in location_reader.fieldnames if re.match(r'\d+', i)]

        for row in location_reader:
            # Build distance dictionary
            my_dists = dict.fromkeys(int_fieldnames, 0)

            for ifn in my_dists.keys():
                try:
                    my_dists[ifn] = float(row[ifn])
                except ValueError:
                    my_dists[ifn] = -1
            # Add to output
            this_row_location = Location(int(row["ID"]), row["Name"], row["Address"], my_dists)
            output_locations.append(this_row_location)
        print(f'Read in {location_reader.line_num} lines from {source_file_name}, '
              f'created {len(output_locations)} package objects.')
        Location.hub = output_locations[0]
        return output_locations


def read_packages(source_file_name: str, locations: List[Location], sim_time: SimTime):
    """Loads packages from the specified CSV file and returns a collection of package instances.
    :param source_file_name: The CSV file to load.
    :param locations: List of Location objects, probably from read_locations()
    :param sim_time: Reference to the global simulation time object. Optional if only doing tests.
    """
    with open(source_file_name) as packages_file:
        packages_reader = csv.DictReader(packages_file)

        # Build location dictionary
        loc_dict = {}
        for loc in locations:
            loc_dict[loc.address + "-" + loc.zip] = loc

        output_packages = []
        fail_count = 0

        for row in packages_reader:
            # Identify the location this package should end up at
            location_hash = row["Address"] + "-" + row["Zip"]

            try:
                my_location = loc_dict[location_hash]
            except KeyError:
                print(f"Couldn't match '{location_hash}' in location dictionary.")
                fail_count += 1
            this_row_package = Package(row["Package ID"], sim_time, my_location, row["City"],
                                       row["Delivery Deadline"], row["Mass KILO"], row["Notes"])
            output_packages.append(this_row_package)

        print(f'Read in {packages_reader.line_num} lines from {source_file_name}, '
              f'created {len(output_packages)} package objects.')
        if fail_count > 0:
            print("Location keys:")
            for k in loc_dict.keys():
                print(k)
            print(f"Failed to identify the correct address for {fail_count} packages.")
        return output_packages
