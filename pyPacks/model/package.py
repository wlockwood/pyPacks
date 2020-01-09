class Package(object):
    def __init__(self, package_id, dest_address, dest_zip, delivery_deadline, notes):
        self.package_id = package_id
        self.dest_address = dest_address
        self.dest_zip = dest_zip
        self.delivery_deadline = delivery_deadline
        self.notes = notes

    def __repr__(self):
        return f"Package({self.package_id},{self.destination_location},{self.delivery_deadline},{self.notes})"

    def __str__(self):
        return f"({self.package_id},{self.destination_location},{self.delivery_deadline},{self.notes})"
