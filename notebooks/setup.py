import os
from os.path import join, abspath
import sys
import json
import geopandas as gpd
import pandas as pd
import numpy as np
from pandas import json_normalize
import psycopg2
import shapely.wkt
import shapely.wkb

import matplotlib.pyplot as plt
from ast import literal_eval
from shapely.geometry import LineString


src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "roads_cba_py")
if src_dir not in sys.path:
    sys.path.append(src_dir)

project_dir = abspath(join(src_dir, ".."))
if project_dir not in sys.path:
    sys.path.append(project_dir)
