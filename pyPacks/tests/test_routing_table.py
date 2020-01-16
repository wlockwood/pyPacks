from unittest import TestCase
from model.routing_table import RoutingTable

class TestRoutingTable(TestCase):
    def setUp(self):
        self.test_table = RoutingTable([])

    def test_set_route_distance(self):
        self.test_table.set_route_distance(1, 2, 10)
        key = self.test_table.make_key(1, 2)
        self.assertEqual(self.test_table.inner_table[key], 10)

    def test_remove_route(self):
        self.test_table.set_route_distance(1, 2, 10)
        key = self.test_table.make_key(1, 2)
        self.assertEqual(self.test_table.inner_table[key], 10)
        self.test_table.remove_route(1, 2)
        self.assertNotIn("key", self.test_table.inner_table)

    def test_lookup(self):
        self.test_table.set_route_distance(1, 2, 10)
        forward = self.test_table.lookup(1, 2)
        self.assertEqual(forward, 10)
        reverse = self.test_table.lookup(2, 1)
        self.assertEqual(reverse, 10)

        self.test_table.set_route_distance(13, 46, 45.2)
        forward = self.test_table.lookup(13, 46)
        self.assertEqual(forward, 45.2)
        reverse = self.test_table.lookup(13, 46)
        self.assertEqual(reverse, 45.2)

    def test_make_key(self):
        gen_key = self.test_table.make_key(1,2)
        self.assertEqual(gen_key, "1-2")
        gen_key = self.test_table.make_key(15,33)
        self.assertEqual(gen_key, "15-33")
