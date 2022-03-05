import json
import numpy as np

from pydantic import BaseModel

from roads_cba_py.configs.growth_rates import GrowthRates, GrowthRate
from roads_cba_py.configs.traffic_levels import TrafficProportionsByLevel
from roads_cba_py.configs.road_works import RoadWorks
from roads_cba_py.configs.recurrent_costs import RecurrentCosts


class Config(BaseModel):
    discount_rate: float = 0.12
    economic_factor: float = 0.91
    growth_rates: GrowthRates = GrowthRates()
    traffic_levels: TrafficProportionsByLevel = TrafficProportionsByLevel()
    road_works: RoadWorks = RoadWorks()
    recurrent_costs: RecurrentCosts = RecurrentCosts()

    class Config:
        json_encoders = {GrowthRate: lambda v: v.default, np.ndarray: lambda v: v.tolist()}


def default_config():
    return Config()
