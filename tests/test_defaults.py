import unittest

import numpy as np

from roads_cba_py.defaults import default_range
from roads_cba_py.configs.road_works import RoadWorks


class TestDefaults(unittest.TestCase):
    def test_interval_based_lookups(self):

        lu = default_range([(0.5, 1.5, "first bucket"), (1.5, 3.5, "second bucket"), (3.5, 10, "last bucket")])
        values = [lu(v) for v in np.arange(1, 5)]

        self.assertEqual(["first bucket", "second bucket", "second bucket", "last bucket"], values)

        # Buckets are [lower inclusive, upper exclusive)
        self.assertEqual("first bucket", lu(1.49))
        self.assertEqual("second bucket", lu(1.5))

    # def test_alternatives(self):
    #     pass
    #     # print([e.json() for e in RoadWorks().alternatives])
