import json
from roads_cba_py.utils import split_on_condition
import unittest
from os.path import join, dirname
import sys
from json import dumps

import os

from schematics.exceptions import DataError

sys.path.append(".")
from roads_cba_py.section import Section, parse_section


class TestSection(unittest.TestCase):
    def setUp(self):
        import warnings
        from schematics.deprecated import SchematicsDeprecationWarning

        warnings.filterwarnings("ignore", category=SchematicsDeprecationWarning)

    def test_simple(self):
        s = Section({"orma_way_id": "7"})
        s = TestSection.load_from_file("section_635950_304.json")
        self.assertEqual("635950_304", s.orma_way_id)

    @classmethod
    def load_from_file(cls, filename):
        example_data_dir = join(dirname(__file__), "example_data")
        return Section.from_file(join(example_data_dir, filename))

    def test_invalid(self):
        s = Section({"orma_way_id": "7", "aadt_delivery": "17"})
        self.assertEqual(17, s.aadt_delivery)

        s = parse_section({"orma_way_id": "7", "aadt_delivery": "17;"})
        self.assertEqual(
            ["Invalid characters in 'aadt_delivery', expected float"],
            s.invalid_reason(),
        )

    def test_split(self):
        a = [1, 2, 3, 4, 5]
        evens, odds = split_on_condition(a, lambda x: x % 2 == 0)
        self.assertEqual([1, 3, 5], odds)
        self.assertEqual([2, 4], evens)
