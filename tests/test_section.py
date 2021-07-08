import json
import unittest
from os.path import join, dirname

from roads_cba_py.section import Section


class TestSection(unittest.TestCase):
    def setUp(self):
        import warnings
        from schematics.deprecated import SchematicsDeprecationWarning

        warnings.filterwarnings("ignore", category=SchematicsDeprecationWarning)

    def test_simple(self):
        s = Section({"section_id": "7"})
        s = TestSection.load_from_file("section_635950_304.json")
        self.assertEqual("635950_304", s.orma_way_id)

    @classmethod
    def load_from_file(cls, filename):
        example_data_dir = join(dirname(__file__), "example_data")
        return Section.from_file(join(example_data_dir, filename))
