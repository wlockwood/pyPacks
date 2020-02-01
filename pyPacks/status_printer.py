from typing import List
from model.package import Package, PackageStatus
from model.truck import Truck


def print_package_status(packages: List[Package]):
    status_header_len = max(len("Status"), PackageStatus.get_longest_len())

    # Build package pairs
    # TODO: This fails for odd numbers of packages?
    # TODO: Some kind of coloring by status?
    first_col = packages[:len(packages) // 2]
    second_col = packages[len(packages) // 2:]
    zipped = zip(first_col, second_col)
    print("Package ID    {:{sw}}      ".format("Status", sw=status_header_len)*2)
    for pair in zipped:
        first_col_string = \
            "{:^10}    {:{sw}}".format(pair[0].package_id, str(pair[0].status.value), sw=status_header_len)
        second_col_string = \
            "{:^10}    {:{sw}}".format(pair[1].package_id, str(pair[1].status.value), sw=status_header_len)
        print(first_col_string, "    ", second_col_string)

def print_truck_status(trucks: List[Truck]):
    for t in trucks:
        print(f"Truck {t.truck_num} is at {t.current_location.name} and has {t.get_package_count()}: "
              f"{', '.join(t.get_loaded_ids())}")
        print()