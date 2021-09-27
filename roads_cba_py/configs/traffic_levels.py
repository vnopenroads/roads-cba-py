import json
import numpy as np

from enum import IntEnum
from typing import Optional, Dict
from roads_cba_py.configs.config_model import ConfigModel

VEHICLE_TYPES = [
    "motorcycle",
    "small_car",
    "medium_car",
    "delivery",
    "four_wheel_drive",
    "light_truck",
    "medium_truck",
    "heavy_truck",
    "articulated_truck",
    "small_bus",
    "medium_bus",
    "large_bus",
]


class TrafficLevel(IntEnum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9
    LEVEL_10 = 10
    LEVEL_11 = 11
    LEVEL_12 = 12
    LEVEL_13 = 13


class TrafficProportions(ConfigModel):
    aadt: int
    struct_no: float
    motorcycle: float
    small_car: float
    medium_car: float
    delivery: float
    four_wheel_drive: float
    light_truck: float
    medium_truck: float
    heavy_truck: float
    articulated_truck: float
    small_bus: float
    medium_bus: float
    large_bus: float

    as_numpy: Optional[np.ndarray]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.as_numpy = np.array(
            [
                self.motorcycle,
                self.small_car,
                self.medium_car,
                self.delivery,
                self.four_wheel_drive,
                self.light_truck,
                self.medium_truck,
                self.heavy_truck,
                self.articulated_truck,
                self.small_bus,
                self.medium_bus,
                self.large_bus,
            ]
        )

    @classmethod
    def from_array(cls, array):
        aadt, struct_no, *proportions = array
        obj = {k: v for k, v in zip(VEHICLE_TYPES, proportions)}
        obj["aadt"] = aadt
        obj["struct_no"] = struct_no
        return cls.parse_obj(obj)


DEFAULTS = {
    0: [25, 1.5, 0.75, 0.02, 0.05, 0.01, 0.01, 0.12, 0.03, 0, 0, 0.01, 0, 0],
    1: [75, 1.5, 0.75, 0.02, 0.05, 0.01, 0.01, 0.12, 0.03, 0, 0, 0.01, 0, 0],
    2: [175, 1.5, 0.65, 0.03, 0.07, 0.02, 0.02, 0.13, 0.04, 0.01, 0, 0.02, 0.01, 0],
    3: [375, 2.0, 0.65, 0.03, 0.07, 0.02, 0.02, 0.13, 0.04, 0.01, 0, 0.02, 0.01, 0],
    4: [750, 3.0, 0.5, 0.05, 0.09, 0.04, 0.04, 0.15, 0.06, 0.02, 0, 0.04, 0.01, 0],
    5: [2000, 4.0, 0.5, 0.05, 0.09, 0.04, 0.04, 0.15, 0.06, 0.02, 0, 0.04, 0.01, 0],
    6: [4000, 5.0, 0.5, 0.05, 0.09, 0.04, 0.04, 0.15, 0.06, 0.02, 0, 0.04, 0.01, 0],
    7: [6000, 6.0, 0.5, 0.05, 0.09, 0.04, 0.04, 0.15, 0.06, 0.02, 0, 0.04, 0.01, 0],
    8: [8000, 7.0, 0.5, 0.05, 0.09, 0.04, 0.04, 0.15, 0.06, 0.02, 0, 0.04, 0.01, 0],
    9: [10500, 8.0, 0.25, 0.08, 0.12, 0.07, 0.07, 0.18, 0.08, 0.05, 0.01, 0.06, 0.02, 0.01],
    10: [13500, 8.0, 0.25, 0.08, 0.12, 0.07, 0.07, 0.18, 0.08, 0.05, 0.01, 0.06, 0.02, 0.01],
    11: [17500, 8.0, 0.25, 0.08, 0.12, 0.07, 0.07, 0.18, 0.08, 0.05, 0.01, 0.06, 0.02, 0.01],
    12: [25000, 8.0, 0.25, 0.08, 0.12, 0.07, 0.07, 0.18, 0.08, 0.05, 0.01, 0.06, 0.02, 0.01],
    13: [35000, 8.0, 0.25, 0.08, 0.12, 0.07, 0.07, 0.18, 0.08, 0.05, 0.01, 0.06, 0.02, 0.01],
    14: [500000, 8.0, 0.25, 0.08, 0.12, 0.07, 0.07, 0.18, 0.08, 0.05, 0.01, 0.06, 0.02, 0.01],
}


class TrafficProportionsByLevel(ConfigModel):
    by_level: Dict[TrafficLevel, TrafficProportions] = {}

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        missing_keys = DEFAULTS.keys() - self.by_level.keys()
        for k in missing_keys:
            self.by_level[k] = TrafficProportions.from_array(DEFAULTS[k])
