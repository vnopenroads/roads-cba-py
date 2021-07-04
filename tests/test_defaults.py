import time
import unittest

import numpy as np
from intervaltree import IntervalTree

from roads_cba_py.defaults import traffic_ranges, traffic_ranges_data, default_range



class TestDefaults(unittest.TestCase):
    def test_interval_based_lookups(self):

        lu = default_range([(0.5, 1.5, 'first bucket'), (1.5, 3.5, "second bucket"), (3.5, 10, "last bucket")])
        values = [lu(v) for v in np.arange(1,5)]

        self.assertEqual(['first bucket', 'second bucket', 'second bucket', "last bucket"], values)

        # Buckets are [lower inclusive, upper exclusive)
        self.assertEqual('first bucket', lu(1.49))
        self.assertEqual('second bucket', lu(1.5))
