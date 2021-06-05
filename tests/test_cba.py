import os
import re
import unittest
import glob
from os.path import join, dirname

import roads_cba_py.cba as cba
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.defaults import get_cc_from_iri_
from roads_cba_py.section import Section
from roads_cba_py.utils import print_diff, check, comp


class TestCbaModel(unittest.TestCase):
    EXAMPLE_DATA_DIR = join(dirname(__file__), "example_data")

    def setUp(self) -> None:
        self.cba_model = cba.CostBenefitAnalysisModel()

    def test_simple(self):

        files = [f for f in glob.glob(os.path.join(self.EXAMPLE_DATA_DIR, "section_*.json")) if "output" not in f]
        idents = [re.match(".*section_(.*).json", f)[1] for f in files]
        idents = ["637227_299"]

        for ident in idents:
            print(f"COMPARING {ident}")
            input = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))
            expected_output = CbaResult.load_from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.output.json"))
            actual_output = self.cba_model.compute_cba_for_section(input)
            print(actual_output.compare(expected_output))

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
