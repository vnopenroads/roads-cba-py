import json
from os import stat
from typing import List, Optional

from pydantic import BaseModel


class InvalidSection(object):
    def __init__(self, errors, original_data):
        self.errors = InvalidSection.clean_errors(errors)
        self.original_data = original_data

    def invalid_reason(self):
        return self.errors

    @staticmethod
    def clean_errors(errors):
        return [InvalidSection.clean_error(e) for e in errors]

    @staticmethod
    def clean_error(e):
        (field,) = e["loc"]
        if "value is not a valid" in e["msg"]:
            return f"Invalid characters in '{field}', expected float"
        if e["type"] == "type_error.none.not_allowed":
            return f"Missing required field: '{field}'"
        return f"Generic error: {e}"


def parse_section(dict_obj):
    try:
        return Section.parse_obj(dict_obj)
    except Exception as err:
        return InvalidSection(err.errors(), dict_obj)


class Section(BaseModel):
    orma_way_id: str
    vpromms_id: Optional[str] = ""
    road_number = ""
    road_name: str = ""
    road_start: str = ""
    road_end: str = ""

    section_order: Optional[int] = -1

    province: str = ""
    district: str = ""
    commune: str = ""
    management: int = -1

    start_km: float = 0.0
    end_km: float = 0.0
    length: float
    vpromms_length: float = 0.0
    lanes: int = 0
    width: float = 0.0
    road_class: int = 0
    terrain: int = 0
    temperature: int = 0
    moisture: int = 0
    road_type: Optional[int] = 0
    surface_type: int = 0
    condition_class: int = 0
    roughness: float = 0.0
    traffic_level: int = 0
    traffic_growth: int = 0
    structural_no: Optional[float] = 0.0
    pavement_age: int = 0

    aadt_motorcyle: float = 0.0
    aadt_carsmall: float = 0.0
    aadt_carmedium: float = 0.0
    aadt_delivery: float = 0.0
    aadt_4wheel: float = 0.0
    aadt_smalltruck: float = 0.0
    aadt_mediumtruck: float = 0.0
    aadt_largetruck: float = 0.0
    aadt_articulatedtruck: float = 0.0
    aadt_smallbus: float = 0.0
    aadt_mediumbus: float = 0.0
    aadt_largebus: float = 0.0
    aadt_total: float = 0.0

    def __str__(self):
        return self.json()

    @staticmethod
    def maybe_int(maybe_int: Optional[int]):
        return int(maybe_int) if maybe_int else 0.0

    @staticmethod
    def maybe_float(maybe_float: Optional[float]):
        return float(maybe_float) if maybe_float else 0.0

    @classmethod
    def from_row(cls, row):
        in_data = {
            "orma_way_id": row["way_id_district"],
            "section_id": row["way_id_district"],
            "road_number": row["road number"],
            "road_name": row["name"],
            "road_start": row["road start location"],
            "road_end": row["road end location"],
            "province": row["province"],
            "district": row["district"],
            "commune": row["section_commune_gso"],
            "management": Section.maybe_int(row["management"]),
            # "start_km": float(row["Start_Km"]),
            # "end_km": float(row["End_Km"]),
            "length": row["length"],
            "lanes": Section.maybe_int(row["section_lanes"]),
            "width": 6.0 if row["width"] == "6+" else Section.maybe_float(row["width"]),
            "road_class": row["link_class"],
            "terrain": row["section_terrain"],
            "temperature": row["section_temperature"],
            "moisture": row["section_moisture"],
            "surface_type": row["section_surface"],
            "condition_class": row["condition"],
            "roughness": Section.maybe_float(row["iri"]),
            "traffic_level": row["section_traffic"],
            "traffic_growth": row["section_traffic_growth"],
            "pavement_age": Section.maybe_int(row["section_pavement_age"]),
            "aadt_motorcyle": Section.maybe_int(row["section_motorcycle"]),
            "aadt_carsmall": Section.maybe_int(row["section_small_car"]),
            "aadt_carmedium": Section.maybe_int(row["section_medium_car"]),
            "aadt_delivery": Section.maybe_int(row["section_delivery_vehicle"]),
            "aadt_4wheel": Section.maybe_int(row["section_four_wheel"]),
            "aadt_smalltruck": Section.maybe_int(row["section_light_truck"]),
            "aadt_mediumtruck": Section.maybe_int(row["section_medium_truck"]),
            "aadt_largetruck": Section.maybe_int(row["section_heavy_truck"]),
            "aadt_articulatedtruck": Section.maybe_int(row["section_articulated_truck"]),
            "aadt_smallbus": Section.maybe_int(row["section_small_bus"]),
            "aadt_mediumbus": Section.maybe_int(row["section_medium_bus"]),
            "aadt_largebus": Section.maybe_int(row["section_large_bus"]),
            "aadt_total": Section.maybe_int(row["aadt"]),
        }
        try:
            return Section(in_data)
        except Exception as err:
            return InvalidSection(err, in_data)

    def to_dict(self):
        return {
            "orma_way_id": self.id,
            "section_id": self.section_id,
            "road_number": self.road_number,
            "road_name": self.road_name,
            "road_start": self.road_start,
            "road_end": self.road_end,
            "province": self.province,
            "district": self.district,
            "commune": self.commune,
            "management": self.management,
            "road_length": self.length,
            "lanes": self.lanes,
            "width": self.width,
            "road_class": self.road_class,
            "terrain": self.terrain,
            "temperature": self.temperature,
            "moisture": self.moisture,
            "surface_type": self.surface_type,
            "condition_class": self.condition_class,
            "roughness": self.roughness,
            "pavement_age": self.pavement_age,
            "aadt_total": self.aadt_total,
        }

    def set_aadts(self, aadts: List[float]):
        (
            self.aadt_motorcyle,
            self.aadt_carsmall,
            self.aadt_carmedium,
            self.aadt_delivery,
            self.aadt_4wheel,
            self.aadt_smalltruck,
            self.aadt_mediumtruck,
            self.aadt_largetruck,
            self.aadt_articulatedtruck,
            self.aadt_smallbus,
            self.aadt_mediumbus,
            self.aadt_largebus,
        ) = aadts

    def get_aadts(self):
        return (
            self.aadt_motorcyle,
            self.aadt_carsmall,
            self.aadt_carmedium,
            self.aadt_delivery,
            self.aadt_4wheel,
            self.aadt_smalltruck,
            self.aadt_mediumtruck,
            self.aadt_largetruck,
            self.aadt_articulatedtruck,
            self.aadt_smallbus,
            self.aadt_mediumbus,
            self.aadt_largebus,
        )

    REQUIRED_FIELDS = ["lanes", "width"]

    def invalid_reason(self):
        errors = []
        if is_missing(self.road_type) and is_missing(self.surface_type):
            errors.append("Must define either road type or road surface type")
        if is_missing(self.width) and is_missing(self.lanes):
            errors.append("Must define either road width or number of lanes")
        if is_missing(self.roughness) and is_missing(self.condition_class):
            errors.append("Must define either roughness or road condition")
        if is_missing(self.traffic_level) and is_missing(self.aadt_total):
            errors.append("Must define either aadt_total or traffic_level")
        if is_missing(self.terrain):
            errors.append("No terrain data")
        return errors if errors else None


def is_missing(val):
    return val is None or val == 0
