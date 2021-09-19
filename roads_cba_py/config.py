import json

from pydantic import BaseModel


class ScenarioGrowthRates(BaseModel):
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


class GrowthRates(BaseModel):
    very_low: ScenarioGrowthRates
    low: ScenarioGrowthRates
    medium: ScenarioGrowthRates
    high: ScenarioGrowthRates
    very_high: ScenarioGrowthRates


class Config(BaseModel):
    growth_rates: GrowthRates
    # fleet_characteristics = ModelType(FleetCharacters, required=True)


def load_config(model, file):
    return model(json.load(file))
