import math
import unittest
from os.path import join, dirname

import roads_cba_py.cba as cba
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.defaults import get_cc_from_iri_
from roads_cba_py.section import Section


class TestCbaModel(unittest.TestCase):
    EXAMPLE_DATA_DIR = join(dirname(__file__), "example_data")

    def setUp(self) -> None:
        self.cba_model = cba.CostBenefitAnalysisModel()

    def test_simple(self):

        ident = "615073_305"
        input = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))
        expected_output = CbaResult.load_from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.output.json"))

        actual_output = self.cba_model.compute_cba_for_section(input)

        def comp(a, b):
            def check(x, y):
                if isinstance(x, str) or isinstance(x, int) or x is None:
                    return x == y
                if isinstance(x, float):
                    return math.isclose(x, y)
                if isinstance(x, list):
                    if len(x) == 10 and len(y) == 20:
                        y = y[0:10]
                    if len(y) == 10 and len(x) == 20:
                        x = x[0:10]
                    return all(math.isclose(xx, yy) for xx, yy in zip(x, y))
                raise ValueError(type(x))

            def print_diff(k, v1, v2):
                if isinstance(v1, list):
                    if len(v1) == 10 and len(v2) == 20:
                        v2 = v2[0:10]
                    if len(v2) == 10 and len(v1) == 20:
                        v1 = v1[0:10]
                    print(f"{k}:")
                    return [
                        print(f"    {x:>2.3f} {'==' if x == y else '!='} {y:>2.3f} ({x - y})") for x, y in zip(v1, v2)
                    ]

                return print(f"{k} => {v1} != {b[k]}")

            a = a.__dict__["_data"]
            b = b.__dict__["_data"]
            diffs = [print_diff(k, v1, b[k]) for k, v1 in a.items() if not check(v1, b[k])]
            [print(d) for d in diffs]
            return diffs

        comp(expected_output, actual_output)
        # self.assertEqual(expected_output.__dict__["_data"], actual_output.__dict__["_data"])

        # self.assertEqual(expected_output.npv, actual_output.npv)

        # aadt => [175.0, 184.45000000000002, 194.4103, 204.9084562, 215.9735128348, 227.63608252787918, 239.92843098438468, 252.88456625754148, 266.54033283544874, 280.933510808563]
        #         [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def test_defaults(self):
        ident = "615073_305"
        section = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))

        self.assertEqual(0, section.roughness)
        section = self.cba_model.get_initial_roughness(section)
        self.assertEqual(7.0, section.roughness)

        self.assertEqual(1, self.cba_model.get_default_lanes(0.1))
        self.assertEqual(1, self.cba_model.get_default_lanes(4.24))
        self.assertEqual(2, self.cba_model.get_default_lanes(4.25))
        self.assertEqual(4, self.cba_model.get_default_lanes(10.0))
        self.assertRaises(ValueError, self.cba_model.get_default_lanes, -1)
        self.assertRaises(ValueError, self.cba_model.get_default_lanes, 100.0)

        section.condition_class = 0
        section.road_type = 3
        section = self.cba_model.get_initial_roughness(section)
        self.assertEqual(7.0, section.roughness)
        self.assertEqual(3, section.condition_class)

        self.assertEqual(3, get_cc_from_iri_(7, 3))
        self.assertEqual(4, get_cc_from_iri_(9.5, 3))
