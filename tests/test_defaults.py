import time
import unittest

import numpy as np
from intervaltree import IntervalTree

from roads_cba_py.defaults import traffic_ranges, traffic_ranges_data, default_range, default_from_range_lookup


# [50, 100, 2],
# [100, 250, 3],
# [250, 500, 4],
# [500, 1000, 5],
# [1000, 3000, 6],
# [3000, 5000, 7],
# [5000, 7000, 8],
# [7000, 9000, 9],
# [9000, 12000, 10],
# [12000, 15000, 11],


class TestCbaModel(unittest.TestCase):
    def test_perf(self):

        vs = np.random.rand(1000) * 15000

        lu = default_range(traffic_ranges_data)

        start = time.process_time()
        news = [lu(v) for v in vs]
        print(news)
        print(time.process_time() - start)

        def f(v):
            x = default_from_range_lookup(traffic_ranges, v, value_col="traffic_class")

        start = time.process_time()
        olds = [f(v) for v in vs]
        print(time.process_time() - start)

        print(olds)
        print(news)
