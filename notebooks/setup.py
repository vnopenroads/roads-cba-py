import os
from os.path import join, abspath, isfile, dirname
import sys
import glob
import re
import json
import geopandas as gpd
import pandas as pd
import numpy as np
from pandas import json_normalize
import shapely.wkt
import shapely.wkb
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from ast import literal_eval
from shapely.geometry import LineString

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def find_pipfile(curr_dir):
    if isfile(join(curr_dir, "Pipfile")):
        return curr_dir
    parent_dir = str(Path(curr_dir).parent)
    return find_pipfile(parent_dir)


project_dir = find_pipfile(os.path.dirname(__file__))
if project_dir not in sys.path:
    sys.path.append(project_dir)

notebook_dir = join(project_dir, "notebooks")
if notebook_dir not in sys.path:
    sys.path.append(notebook_dir)


from os.path import expanduser

home = expanduser("~")
sys.environ["TEMP_DIR"] = join(home, "tmp")
