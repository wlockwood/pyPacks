from typing import List
from model.location import Location
from model.package import Package, PackageStatus


class PackageGroup(object):
    def __init__(self, package_list: List[Package]):
        self.packages = package_list
        self.destination: Location = self.packages[0].dest_location

    def get_count(self):
        return len(self.packages)

    def get_status(self):
        return self.packages[0].status  # All packages in group should have same status

    def update_status(self, new_state: PackageStatus):
        for p in self.packages:
            p.update_status(new_state)

    def __repr__(self):
        return f"PackageGroup({len(self.packages)})"

    def __str__(self):
        return f"PackageGroup({len(self.packages)})"
