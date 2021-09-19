import json
from roads_cba_py.utils import split_on_condition
import unittest
from os.path import join, dirname
import sys
from json import dumps

import os

sys.path.append(".")
from roads_cba_py.section import Section, parse_section


example_data_dir = join(dirname(__file__), "example_data")


class TestSection(unittest.TestCase):
    def test_simple(self):
        s = Section(orma_way_id="635950_304", length=7.0)
        self.assertEqual("635950_304", s.orma_way_id)

        print(os.getcwd())
        s = Section.parse_file(join(example_data_dir, "section_635950_304.json"))
        self.assertEqual("635950_304", s.orma_way_id)

    def test_invalid(self):
        s = Section(orma_way_id=7, aadt_delivery=17, length=0.7)
        self.assertEqual(17, s.aadt_delivery)

        s = parse_section({"orma_way_id": "7", "length": 0.7, "aadt_delivery": "17;"})
        self.assertEqual(
            ["Invalid characters in 'aadt_delivery', expected float"],
            s.invalid_reason(),
        )

        s = parse_section({"orma_way_id": None, "length": 0.7, "aadt_delivery": "17"})
        self.assertEqual(["Missing required field: 'orma_way_id'"], s.invalid_reason())

    def test_split(self):
        a = [1, 2, 3, 4, 5]
        evens, odds = split_on_condition(a, lambda x: x % 2 == 0)
        self.assertEqual([1, 3, 5], odds)
        self.assertEqual([2, 4], evens)
