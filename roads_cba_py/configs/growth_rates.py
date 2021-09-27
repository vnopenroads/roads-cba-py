import json
import numpy as np

from enum import IntEnum
from typing import Optional, Union
from pydantic import validator
from roads_cba_py.configs.config_model import ConfigModel


class GrowthRateByMode(ConfigModel):
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


class GrowthRate(object):
    def __init__(self, val):
        self.default = val
        self.as_numpy = np.array([val] * 12)


class GrowthScenario(IntEnum):
    very_low = 1
    low = 2
    medium = 3
    high = 4
    very_high = 5


def upgrade_float(v):
    if isinstance(v, float):
        return GrowthRate(v)
    return v


class GrowthRates(ConfigModel):
    very_low: Union[GrowthRateByMode, GrowthRate, float] = GrowthRate(0.034)
    low: Union[GrowthRateByMode, GrowthRate, float] = GrowthRate(0.046)
    medium: Union[GrowthRateByMode, GrowthRate, float] = GrowthRate(0.054)
    high: Union[GrowthRateByMode, GrowthRate, float] = GrowthRate(0.057)
    very_high: Union[GrowthRateByMode, GrowthRate, float] = GrowthRate(0.086)
    by_scenario: dict = {}

    def for_scenario(self, scenario: GrowthScenario):
        return self.by_scenario[scenario]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.by_scenario = {
            GrowthScenario.very_low: self.very_low,
            GrowthScenario.low: self.low,
            GrowthScenario.medium: self.medium,
            GrowthScenario.high: self.high,
            GrowthScenario.very_high: self.very_high,
        }

    _normalize_vl = validator("very_low", allow_reuse=True)(upgrade_float)
    _normalize_l = validator("low", allow_reuse=True)(upgrade_float)
    _normalize_m = validator("medium", allow_reuse=True)(upgrade_float)
    _normalize_h = validator("high", allow_reuse=True)(upgrade_float)
    _normalize_vh = validator("very_high", allow_reuse=True)(upgrade_float)
