from enum import IntEnum
from typing import Optional, List
from roads_cba_py.configs.config_model import ConfigModel


class Terrain(IntEnum):
    Flat = 1
    Hilly = 2
    Mountainous = 3


# fmt: off
keys = [ "name", "code", "work_class", "cost_flat", "cost_hilly", "cost_mountainous", "iri", "lanes_class",
         "width", "surface", "thickness", "strength", "snc", "repair", "repair_period"] 
# fmt: on


class MaintenanceAlternative(ConfigModel):
    name: str
    code: str
    work_class: str
    cost_flat: float
    cost_hilly: float
    cost_mountainous: float
    iri: float
    lanes_class: int
    width: float
    surface: int
    thickness: Optional[int]
    strength: Optional[float]
    snc: Optional[float]
    repair: int
    repair_period: int

    idx: int

    @classmethod
    def from_array(cls, array, idx):
        dct = {k: v for k, v in zip(keys, array)}
        dct["idx"] = idx
        return cls.parse_obj(dct)

    def get_unit_cost(self, terrain: Terrain):
        return {1: self.cost_flat, 2: self.cost_hilly, 3: self.cost_mountainous}[terrain]


# fmt: off
DEFAULTS = [
    ["Periodic Maintenance (Concrete)", "C-P", "Periodic", 132.0, 132.0, 132.0, 3.0, 0, 0, 0, None, None, None, 1, 8,],
    ["Reconstruction (Concrete)", "C-R", "Rehabilitation", 549.0, 549.0, 549.0, 1.8, 0, 0, 0, None, None, None, 1, 8,],
    ["Reseal", "B-P1", "Periodic", 127.0, 127.0, 127.0, 4.0, 0, 0, 0, 25, 0.20, None, 4, 8],
    ["Functional Overlay (<=50mm)", "B-P2", "Periodic", 176.25, 176.25, 176.25, 3.5, 0, 0, 0, 50, 0.40, None, 4, 8],
    ["Structural Overlay (51-100mm)", "B-P3", "Periodic", 282.0, 282.0, 282.0, 3.0, 0, 0, 0, 80, 0.40, None, 4, 8],
    ["Thick Overlay (>100mm)", "B-R1", "Rehabilitation", 352.5, 352.5, 352.5, 2.5, 0, 0, 0, 100, 0.40, None, 4, 8],
    ["Reconstruction Type V", "B-R2", "Rehabilitation", 397.0, 397.0, 397.0, 2.0, 0, 0, 0, None, None, 2.0, 4, 8],
    ["Reconstruction Type IV", "B-R3", "Rehabilitation", 397.0, 397.0, 397.0, 2.0, 0, 0, 0, None, None, 3.0, 4, 8],
    ["Reconstruction Type III", "B-R4", "Rehabilitation", 397.0, 397.0, 397.0, 2.0, 0, 0, 0, None, None, 4.0, 4, 8],
    ["Reconstruction Type II", "B-R5", "Rehabilitation", 397.0, 397.0, 397.0, 2.0, 0, 0, 0, None, None, 5.0, 4, 8],
    ["Reconstruction Type I", "B-R6", "Rehabilitation", 397.0, 397.0, 397.0, 2.0, 0, 0, 0, None, None, 6.0, 4, 8],
    ["Regravelling (Gravel)", "G-P", "Periodic", 37.0, 37.0, 37.0, 12.0, 0, 0, 0, None, None, None, 12, 4],
    ["Reconstruction (Gravel)", "G-R", "Rehabilitation", 114.0, 114.0, 114.0, 7.0, 0, 0, 0, None, None, None, 12, 4,],
    ["Heavy Grading (Earth)", "E-P", "Periodic", 16.0, 16.0, 16.0, 16.0, 0, 0, 0, None, None, None, 14, 4],
    ["Reconstruction (Earth)", "E-R", "Rehabilitation", 24.0, 24.0, 24.0, 10.0, 0, 0, 0, None, None, None, 14, 4],
    ["Periodic Maintenance (Macadam)", "M-P", "Periodic", 37.0, 37.0, 37.0, 8.0, 0, 0, 0, None, None, None, 16, 8],
    ["Reconstruction (Macadam)", "M-R", "Rehabilitation", 114.0, 114.0, 114.0, 4.0, 0, 0, 0, None, None, None, 16, 8,],
    ["Periodic Maintenance (Cobblestone)", "O-P", "Periodic", 37.0, 37.0, 37.0, 8.0, 0, 0, 0, None, None, None, 18, 8,],
    ["Reconstruction (Cobblestone)", "O-R", "Rehabilitation", 114.0, 114.0, 114.0, 4.0, 0, 0, 0, None, None, None, 18, 8,],
    ["Upgrade to Cobblestone", "U-C", "Upgrade", 500.0, 500.0, 500.0, 4.0, 3, 7.0, 7, None, None, None, 18, 8],
    ["Upgrade to Macadam", "U-M", "Upgrade", 500.0, 500.0, 500.0, 4.0, 3, 7.0, 6, None, None, None, 16, 8],
    ["Upgrade to Gravel", "U-G", "Upgrade", 500.0, 500.0, 500.0, 8.0, 3, 7.0, 4, None, None, None, 12, 4],
    ["Upgrade to Surface Treatment", "U-S", "Upgrade", 500.0, 500.0, 500.0, 2.6, 3, 7.0, 3, None, None, 2.0, 4, 8],
    ["Upgrade to Asphalt Concrete", "U-A", "Upgrade", 500.0, 500.0, 500.0, 2.2, 3, 7.0, 2, None, None, 4.0, 4, 8],
    ["Upgrade to Cement Concrete", "U-C", "Upgrade", 500.0, 500.0, 500.0, 1.8, 3, 7.0, 1, None, None, None, 1, 8],
]
# fmt: on


class RoadWorks(ConfigModel):
    alternatives: List[MaintenanceAlternative] = [
        MaintenanceAlternative.from_array(arr, i) for i, arr in enumerate(DEFAULTS)
    ]
