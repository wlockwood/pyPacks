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

    def get_linked_package_ids(self) -> List[int]:
        output: List[int] = []
        for package in self.packages:
            output.extend(package.linked_package_ids)
        return output

    def is_linked_to_id(self, remote_id: int):
        return any(x for x in self.packages if remote_id in x.linked_package_ids)

    def is_linked_to_ids(self, remote_ids: List[int]):
        return any(x for x in remote_ids if self.is_linked_to_id(x))

    def contains_package_id(self, search_id: int) -> bool:
        return any([x for x in self.packages if x.package_id == search_id])

    def __repr__(self):
        return f"PackageGroup({len(self.packages)})"

    def __str__(self):
        return f"PackageGroup({len(self.packages)})"
