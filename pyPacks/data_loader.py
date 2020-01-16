import csv
import re
from model.package import Package
from model.location import Location


def read_packages(source_file_name: str):
    """Loads packages from the specified CSV file and returns a collection of package instances.
    :param source_file_name: The CSV file to load.
    """
    with open(source_file_name) as packages_file:
        packages_reader = csv.DictReader(packages_file)
        next(packages_reader)  # Skips the header row
        output_packages = []

        for row in packages_reader:
            this_row_package = Package(row["Package ID"], row["Address"], row["Zip"],
                                       row["Delivery Deadline"], row["Notes"])
            output_packages.append(this_row_package)
        print(f'Read in {packages_reader.line_num} lines from {source_file_name}, '
              f'created {len(output_packages)} package objects.')
        return output_packages


def read_locations(source_file_name: str):
    """Loads locations from the specified CSV file and returns a collection of location instances.
    :param source_file_name: The CSV file to load.
    """
    with open(source_file_name) as location_file:
        location_reader = csv.DictReader(location_file)
        output_locations = []
        next(location_reader)  # Skips the header row

        int_fieldnames = [i for i in location_reader.fieldnames if re.match('\d+', i)]

        distance_array_fields = list(map(lambda x: int(x), int_fieldnames)) # Not sure this is necessary?

        for row in location_reader:
            # Build distance array
            my_dists = dict.fromkeys(int_fieldnames, 0)

            for ifn in my_dists.keys():
                try:
                    my_dists[ifn] = float(row[ifn])
                except ValueError:
                    my_dists[ifn] = -1
            # Add to output
            this_row_location = Location(row["ID"], row["Name"], row["Address"], my_dists)
            output_locations.append(this_row_location)
            # print(f"{this_row_location.name}, {len([x for x in my_dists.values() if x >= 0])} valid distance entries")
        print(f'Read in {location_reader.line_num} lines from {source_file_name}, '
              f'created {len(output_locations)} package objects.')
        return output_locations
