import copy
import unittest
from os.path import join, dirname

from roads_cba_py.config import ScenarioGrowthRates, GrowthRates


class TestConfig(unittest.TestCase):
    EXAMPLE_DATA_DIR = join(dirname(__file__), "example_data")

    def test_simple(self):
        json = {
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
        json2 = copy.deepcopy(json)
        json3 = copy.deepcopy(json)
        json4 = copy.deepcopy(json)
        json5 = copy.deepcopy(json)
        json5["large_bus"] = 3.0

        scenario_rates = ScenarioGrowthRates.parse_obj(json)
        self.assertEqual(scenario_rates.medium_bus, 1.0)
        self.assertEqual(scenario_rates.large_bus, 2.0)

        rates = GrowthRates.parse_obj(
            {"very_low": json, "low": json2, "medium": json3, "high": json4, "very_high": json5}
        )
        self.assertEqual(rates.very_low.large_bus, 2.0)
        self.assertEqual(rates.very_high.large_bus, 3.0)
