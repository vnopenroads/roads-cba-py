import os
import re
import unittest
import glob
import warnings
from os.path import join, dirname

import schematics

import roads_cba_py.cba as cba
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.defaults import get_cc_from_iri_
from roads_cba_py.section import Section
from roads_cba_py.utils import print_diff, check, comp


class TestCbaModel(unittest.TestCase):
    EXAMPLE_DATA_DIR = join(dirname(__file__), "example_data")

    def setUp(self) -> None:
        self.cba_model = cba.CostBenefitAnalysisModel()
        warnings.filterwarnings("ignore", category=schematics.deprecated.SchematicsDeprecationWarning)

    def test_all_data_matches(self):

        files = [f for f in glob.glob(os.path.join(self.EXAMPLE_DATA_DIR, "section_*.json")) if "output" not in f]
        idents = [re.match(".*section_(.*).json", f)[1] for f in files]

        for ident in idents[0:20]:
            print(f"COMPARING {ident}")
            input = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))
            expected_output = CbaResult.load_from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.output.json"))
            actual_output = self.cba_model.compute_cba_for_section(input)
            print(
                {
                    k: v
                    for k, v in actual_output.compare(expected_output).items()
                    if ((isinstance(v, float) and v != 0.0) or (isinstance(v, str) and "==" not in v))
                }
            )

            comp(expected_output, actual_output)

    def test_defaults(self):
        ident = "615073_305"
        section = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))

        self.assertEqual(0, section.roughness)
        section = self.cba_model.fill_defaults(section)
        self.assertEqual(7.0, section.roughness)

        self.assertEqual(1, self.cba_model.get_default_lanes(0.1))
        self.assertEqual(1, self.cba_model.get_default_lanes(4.24))
        self.assertEqual(2, self.cba_model.get_default_lanes(4.25))
        self.assertEqual(4, self.cba_model.get_default_lanes(10.0))
        self.assertRaises(ValueError, self.cba_model.get_default_lanes, -1)
        self.assertRaises(ValueError, self.cba_model.get_default_lanes, 100.0)

        section.condition_class = 0
        section.road_type = 3
        section = self.cba_model.fill_defaults(section)
        self.assertEqual(7.0, section.roughness)
        self.assertEqual(3, section.condition_class)

        self.assertEqual(3, get_cc_from_iri_(7, 3))
        self.assertEqual(4, get_cc_from_iri_(9.5, 3))
