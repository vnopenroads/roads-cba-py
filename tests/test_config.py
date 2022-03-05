import copy
from roads_cba_py.configs.traffic_levels import TrafficProportionsByLevel
import unittest
import json
from os.path import join, dirname
import numpy as np
import numpy.testing as npt

from roads_cba_py.configs.growth_rates import GrowthRate, GrowthRateByMode, GrowthRates, GrowthScenario, GrowthRate
from roads_cba_py.configs.traffic_levels import TrafficProportionsByLevel


class TestConfig(unittest.TestCase):
    EXAMPLE_DATA_DIR = join(dirname(__file__), "example_data")

    def test_simple(self):

        json = self.simple_growth_rate_obj()
        json2 = copy.deepcopy(json)
        json3 = copy.deepcopy(json)
        json4 = copy.deepcopy(json)
        json5 = copy.deepcopy(json)
        json5["large_bus"] = 3.0

        scenario_rates = GrowthRateByMode.parse_obj(json)
        self.assertEqual(scenario_rates.medium_bus, 1.0)
        self.assertEqual(scenario_rates.large_bus, 2.0)

        rates = GrowthRates.parse_obj(
            {"very_low": json, "low": json2, "medium": json3, "high": json4, "very_high": json5}
        )
        self.assertEqual(rates.very_low.large_bus, 2.0)
        self.assertEqual(rates.very_high.large_bus, 3.0)

    def test_growth_enum(self):
        self.assertEqual(3, GrowthScenario(3))
        self.assertRaises(ValueError, GrowthScenario, 7)

    def test_singular_growth_rate(self):
        GrowthRate(7.7)

    def test_computed_fields(self):
        scenario_rates = GrowthRateByMode.parse_obj(self.simple_growth_rate_obj())

        expected_array = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2])
        npt.assert_array_almost_equal(scenario_rates.as_numpy, expected_array)

    def simple_growth_rate_obj(self):
        return {
            "motorcycle": 1.0,
            "small_car": 1.0,
            "medium_car": 1.0,
            "delivery": 1.0,
            "four_wheel_drive": 1.0,
            "light_truck": 1.0,
            "medium_truck": 1.0,
            "heavy_truck": 1.0,
            "articulated_truck": 1.0,
            "small_bus": 1.0,
            "medium_bus": 1.0,
            "large_bus": 2.0,
        }

    def test_traffic_levels(self):
        tpbl = TrafficProportionsByLevel()
        # print((tpbl.json(exclude={"by_level": {"__all__": {"proportions"}}})))
