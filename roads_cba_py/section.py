import json

from schematics.models import Model
from schematics.types import IntType, StringType, FloatType


class Section(Model):
    orma_way_id = StringType(max_length=20, min_length=1)
    vpromm_id = StringType(max_length=20, min_length=1)
    section_id = StringType(max_length=30, required=True)
    road_number = StringType(max_length=10)
    road_name = StringType(max_length=255, min_length=1)
    road_start = StringType(max_length=255, min_length=1)
    road_end = StringType(max_length=255, min_length=1)

    section_order = IntType()

    province = StringType(max_length=255, min_length=1)
    district = StringType(max_length=255, min_length=1)
    # province = ForeignKey('administrations.AdminUnit', null=True,
    #                              blank=True, on_delete=PROTECT,
    #                              related_name='province_sections')
    # district = ForeignKey('administrations.AdminUnit', null=True,
    #                              blank=True, on_delete=PROTECT,
    #                              related_name='district_sections')

    commune = StringType(max_length=25)
    management = IntType()

    start_km = FloatType()
    end_km = FloatType()
    length = FloatType(required=True)
    lanes = IntType()
    width = StringType()
    road_class = IntType()
    terrain = IntType()
    temperature = IntType()
    moisture = IntType()
    road_type = IntType()
    surface_type = IntType()
    condition_class = IntType()
    roughness = FloatType()
    traffic_level = IntType()
    traffic_growth = IntType()
    structural_no = FloatType()
    pavement_age = IntType()

    aadt_motorcyle = FloatType()
    aadt_carsmall = FloatType()
    aadt_carmedium = FloatType()
    aadt_delivery = FloatType()
    aadt_4wheel = FloatType()
    aadt_smalltruck = FloatType()
    aadt_mediumtruck = FloatType()
    aadt_largetruck = FloatType()
    aadt_articulatedtruck = FloatType()
    aadt_smallbus = FloatType()
    aadt_mediumbus = FloatType()
    aadt_largebus = FloatType()
    aadt_total = FloatType()

    def __str__(self):
        return str(self.to_primitive())

    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            return Section(json.load(f))
