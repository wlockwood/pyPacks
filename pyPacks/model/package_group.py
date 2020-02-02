from typing import List, Dict, Set
from model.location import Location
from model.package import Package, PackageStatus


class PackageGroup(object):
    package_group_dict: Dict[int, 'PackageGroup'] = {}

    def __init__(self, package_list: List[Package]):
        self.packages = package_list
        self.destination: Location = self.packages[0].dest_location
        for p in package_list:
            self.package_group_dict[p.package_id] = self
        self.linked_package_groups: Set[PackageGroup] = set()

    @classmethod
    def get_owning_package_group(cls, package_id: int):
        return cls.package_group_dict.get(package_id)

    def get_count(self):
        return len(self.packages)

    def get_ids(self) -> List[int]:
        return [x.package_id for x in self.packages]

    def get_status(self):
        return self.packages[0].status  # All packages in group should have same status

    def update_status(self, new_state: PackageStatus):
        for p in self.packages:
            p.update_status(new_state)

    def get_remaining_time(self) -> float:
        return min(x.get_rem_time() for x in self.packages)

    def get_linked_package_groups(self, found_pgs: Set['PackageGroup'] = [], depth_so_far = 0):
        """Recursively find linked package groups.
        Requires object links to have been created by load_builder"""
        depth_so_far += 1
        found_pgs = set(found_pgs)
        found_pgs.add(self)
        for pg in (set(self.linked_package_groups) - found_pgs):
            #print(f"{self} had {len(self.linked_package_groups)} links: {self.linked_package_groups}. Depth: {depth_so_far}")  # DEBUG!
            found_pgs = found_pgs.union(pg.get_linked_package_groups(found_pgs, depth_so_far))
        return found_pgs

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

    def rebuild_package_group(self):
        # Determine groups
        print(f"Rebuilding {self}...")
        distinct_locations = ()
        for p in self.packages:
            distinct_locations.add(p.dest_location)
        new_pgs = []

        print(f"Package group rebuild resulted in:")
        for l in distinct_locations:
            my_packages = [p for p in self.packages if p.dest_location == l]
            new_pg = (PackageGroup(my_packages))
            new_pgs.append(new_pg)
            print(" - ", new_pg)
        return new_pgs

    def __repr__(self):
        return f"PackageGroup({self.get_count()}: {', '.join([str(x.package_id) for x in self.packages])})"

    def __str__(self):
        return f"({self.get_count()}: {', '.join([str(x.package_id) for x in self.packages])})"
