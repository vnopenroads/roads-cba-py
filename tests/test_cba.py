import unittest
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

        ident = "615073_305"

        idents = [
            "603159_301",
            "603646_298",
            "614761_296",
            "614791_297",
            "614818_300",
            "614835_302",
            "614835_303",
            "614835_304",
            "614896_297",
            "614947_295",
            "614984_299",
            "614987_298",
            "614991_298",
            "615061_299",
            "615069_299",
            "615073_305",
            "615080_302",
            "615080_303",
            "615082_303",
            "615093_302",
            "615093_303",
            "615101_299",
            "615107_299",
            "615110_299",
            "615129_298",
            "615129_299",
            "615130_299",
            "615131_298",
            "615136_298",
            "615137_298",
            "615139_298",
            "615143_299",
            "615144_299",
            "615151_299",
            "615152_299",
            "615156_299",
            "615160_301",
            "615161_299",
            "615163_301",
            "615164_299",
            "615167_304",
            "615167_305",
            "615177_299",
            "615177_300",
            "615184_300",
            "615185_298",
            "615187_298",
            "615188_298",
            "615196_298",
            "615199_303",
            "615205_298",
            "615207_298",
            "615231_300",
            "615237_302",
            "615237_303",
            "615243_299",
            "615244_299",
            "635950_304",
        ]

        for ident in idents:
            print(f"COMPARING {ident}")
            input = Section.from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.json"))
            expected_output = CbaResult.load_from_file(join(self.EXAMPLE_DATA_DIR, f"section_{ident}.output.json"))
            actual_output = self.cba_model.compute_cba_for_section(input)

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
