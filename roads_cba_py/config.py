import json
import numpy as np

from pydantic import BaseModel

from roads_cba_py.configs.growth_rates import GrowthRates


class Config(BaseModel):
    discount_rate: float = 0.12
    economic_factor: float = 0.91
    growth_rates: GrowthRates = GrowthRates()
    # fleet_characteristics = ModelType(FleetCharacters, required=True)


def default_config():
    return Config()
