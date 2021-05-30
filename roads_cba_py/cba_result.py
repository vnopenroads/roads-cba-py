import json
from os.path import join, dirname

from schematics import Model
from schematics.types import StringType, FloatType, ListType


class CbaResult(Model):
    work_class = StringType(required=True, min_length=1)
    work_type = StringType(required=True, min_length=1)
    work_name = StringType(required=True, min_length=1)
    work_cost = FloatType(required=True)
    work_cost_km = FloatType(required=True)
    work_year = FloatType(required=True)
    npv = FloatType(required=True)
    npv_km = FloatType(required=True)
    npv_cost = FloatType(required=True)
    eirr = FloatType(required=True)
    aadt = ListType(FloatType, required=True, min_size=20, max_size=20)
    truck_percent = FloatType(required=True)
    vehicle_utilization = FloatType(required=True)
    esa_loading = FloatType(required=True)
    iri_projection = ListType(FloatType, required=True, min_size=20, max_size=20)
    iri_base = ListType(FloatType, required=True, min_size=20, max_size=20)
    con_projection = ListType(FloatType, required=True, min_size=20, max_size=20)
    con_base = ListType(FloatType, required=True, min_size=20, max_size=20)
    financial_recurrent_cost = ListType(FloatType, required=True, min_size=20, max_size=20)
    net_benefits = ListType(FloatType, required=True, min_size=20, max_size=20)

    def __repr__(self):
        return str(self.to_primitive())

    @classmethod
    def load_from_file(cls, filename):
        with open(filename) as f:
            return CbaResult(json.load(f))
