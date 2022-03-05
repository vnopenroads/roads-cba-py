from enum import IntEnum
from typing import Optional, Dict
from roads_cba_py.configs.config_model import ConfigModel


class SurfaceType(IntEnum):
    CementConcrete = 1
    AsphaltConcrete = 2
    SurfaceTreatment = 3
    Gravel = 4
    Earth = 5
    Macadam = 6
    Cobblestone = 7


class LanesClass(IntEnum):
    OneLane = 1
    TwoLanesNarrow = 2
    TwoLanes = 3
    TwoLanesWide = 4
    FourLanes = 5
    SixLanes = 6
    EightLanes = 7


lane_keys = ["one_lane", "two_lanes_narrow", "two_lanes", "two_lanes_wide", "four_lanes", "six_lanes", "eight_lanes"]


class RecurrentCostsForSurfaceType(ConfigModel):
    one_lane: float
    two_lanes_narrow: float
    two_lanes: float
    two_lanes_wide: float
    four_lanes: float
    six_lanes: float
    eight_lanes: float

    @classmethod
    def from_array(cls, array):
        dct = {k: v for k, v in zip(lane_keys, array)}
        return cls.parse_obj(dct)

    by_lanes: Optional[Dict[LanesClass, float]]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.by_lanes = {
            LanesClass.OneLane: self.one_lane,
            LanesClass.TwoLanesNarrow: self.two_lanes_narrow,
            LanesClass.TwoLanes: self.two_lanes,
            LanesClass.TwoLanesWide: self.two_lanes_wide,
            LanesClass.FourLanes: self.four_lanes,
            LanesClass.SixLanes: self.six_lanes,
            LanesClass.EightLanes: self.eight_lanes,
        }


RC, f = RecurrentCostsForSurfaceType, RecurrentCostsForSurfaceType.from_array


class RecurrentCosts(ConfigModel):
    # fmt: off
    cement_concrete: RC   = f([10167.7938484056, 19115.4524350025, 20282.3695008311, 19928.875942875, 20335.5876968112, 20335.5876968112, 20335.5876968112])
    asphalt_concrete: RC  = f([14758.9085060652, 26861.2134810386, 27746.7479914025, 28632.2825017664, 29517.8170121303, 29517.8170121303, 29517.8170121303])
    surface_treatment: RC = f([12117.2647173132, 18418.242370316, 20357.0047250861, 22295.7670798562, 24234.5294346263, 24234.5294346263, 24234.5294346263])
    gravel: RC            = f([8845.72489898381, 12737.8438545367, 14330.0743363538, 16099.2193161505, 17691.4497979676, 17691.4497979676, 17691.4497979676])
    earth: RC             = f([5662.55318106041, 7361.31913537853, 8607.08083521182, 9966.09359866632, 11325.1063621208, 11325.1063621208, 11325.1063621208])
    macadam: RC           = f([12117.2647173132, 18418.242370316, 20357.0047250861, 22295.7670798562, 24234.5294346263, 24234.5294346263, 24234.5294346263])
    cobblestones: RC      = f([8845.72489898381, 12737.8438545367, 14330.0743363538, 16099.2193161505, 17691.4497979676, 17691.4497979676, 17691.4497979676])
    # fmt: on

    by_surface: Optional[Dict[SurfaceType, RC]]

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.by_surface = {
            SurfaceType.CementConcrete: self.cement_concrete,
            SurfaceType.AsphaltConcrete: self.asphalt_concrete,
            SurfaceType.SurfaceTreatment: self.surface_treatment,
            SurfaceType.Gravel: self.gravel,
            SurfaceType.Earth: self.earth,
            SurfaceType.Macadam: self.macadam,
            SurfaceType.Cobblestone: self.cobblestones,
        }

    def get(self, surface_type: SurfaceType, lanes_class: LanesClass):
        return self.by_surface[surface_type].by_lanes[lanes_class]
