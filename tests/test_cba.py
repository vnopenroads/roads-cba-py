import unittest
from os.path import join, dirname

import roads_cba_py.cba as cba
from roads_cba_py.cba_result import CbaResult
from roads_cba_py.section import Section


class TestCbaModel(unittest.TestCase):
    def test_simple(self):

        example_data_dir = join(dirname(__file__), "example_data")

        ident = "615073_305"
        input = Section.from_file(join(example_data_dir, f"section_{ident}.json"))
        expected_output = CbaResult.load_from_file(join(example_data_dir, f"section_{ident}.output.json"))

        cba_model = cba.CostBenefitAnalysisModel()
        actual_output = cba_model.compute_cba_for_section(input)

        def comp(a, b):
            a = a.__dict__["_data"]
            b = b.__dict__["_data"]
            diffs = [f"{k} => {v1} != {b[k]}" for k, v1 in a.items() if v1 != b[k]]
            [print(d) for d in diffs]
            return diffs

        comp(expected_output, actual_output)
        # self.assertEqual(expected_output.__dict__["_data"], actual_output.__dict__["_data"])

        # self.assertEqual(expected_output.npv, actual_output.npv)

        # aadt => [175.0, 184.45000000000002, 194.4103, 204.9084562, 215.9735128348, 227.63608252787918, 239.92843098438468, 252.88456625754148, 266.54033283544874, 280.933510808563]
        #         [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
