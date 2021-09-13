import os
import re
import time
import unittest
import glob
import warnings
from os.path import join, dirname
from pstats import SortKey
from random import sample

import schematics

import roads_cba_py.cba as cba
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.section import Section


class TestCbaModel(unittest.TestCase):
    EXAMPLE_DATA_DIR = join(dirname(__file__), "example_data")

    def setUp(self) -> None:
        self.cba_model = cba.CostBenefitAnalysisModel()
        warnings.filterwarnings("ignore", category=schematics.deprecated.SchematicsDeprecationWarning)

    def test_all_data_matches(self):

        files = [f for f in glob.glob(os.path.join(self.EXAMPLE_DATA_DIR, "section_*.json")) if "output" not in f]
        files = files[0:10]
        # files = sample(files, 10)
        idents = [re.match(".*section_(.*).json", f)[1] for f in files]

        def process_ident(ident):
            input = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))
            return self.cba_model.compute_cba_for_section(input)

        start = time.time()
        actual_outputs = {ident: process_ident(ident) for ident in idents}
        # print(f"Time: {time.time() - start}")

        for ident, actual_output in actual_outputs.items():
            expected_output = CbaResult.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.output.json"))
            diffs = {
                k: [actual_output.to_dict()[k], expected_output.to_dict()[k], v]
                for k, v in actual_output.compare(expected_output).items()
                if ((isinstance(v, float) and v != 0.0) or (isinstance(v, str) and "==" not in v))
            }
            if diffs != {}:
                for k, v in diffs.items():
                    print(k, v)
            self.assertEqual({}, diffs)

    def test_performance(self):
        import cProfile

        files = [f for f in glob.glob(os.path.join(self.EXAMPLE_DATA_DIR, "section_*.json")) if "output" not in f]
        files = files[0:1]
        # print(files)
        # files = sample(files, 10)
        idents = [re.match(".*section_(.*).json", f)[1] for f in files]

        def process_ident(ident):
            input = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))
            return self.cba_model.compute_cba_for_section(input)

        def foo():
            start = time.time()
            actual_outputs = {ident: process_ident(ident) for ident in idents}
            # print(f"Time: {time.time() - start}")
            return actual_outputs

        # with cProfile.Profile() as pr:
        foo()
        # pr.print_stats(SortKey.TIME)

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
        # self.assertRaises(ValueError, self.cba_model.get_default_lanes, -1)
        # self.assertRaises(ValueError, self.cba_model.get_default_lanes, 100.0)

        section.condition_class = 0
        section.road_type = 3
        section = self.cba_model.fill_defaults(section)
        self.assertEqual(7.0, section.roughness)
        self.assertEqual(3, section.condition_class)

        # kself.assertEqual(3, get_cc_from_iri_(7, 3))
        # kself.assertEqual(4, get_cc_from_iri_(9.5, 3))
