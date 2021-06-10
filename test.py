import glob
import os
import re
import time
from os.path import join, dirname

from roads_cba_py import cba
from roads_cba_py.section import Section

EXAMPLE_DATA_DIR = join(dirname(__file__), "tests", "example_data")
files = [f for f in glob.glob(os.path.join(EXAMPLE_DATA_DIR, "section_*.json")) if "output" not in f]
files = files[0:10]
# files = sample(files, 10)
idents = [re.match(".*section_(.*).json", f)[1] for f in files]

print(idents)


def process_ident(ident):
    input = Section.from_file(join(EXAMPLE_DATA_DIR, f"section_{ident}.json"))
    cba_model = cba.CostBenefitAnalysisModel()
    return cba_model.compute_cba_for_section(input)


actual_outputs = {ident: process_ident(ident) for ident in idents}
print(actual_outputs)
