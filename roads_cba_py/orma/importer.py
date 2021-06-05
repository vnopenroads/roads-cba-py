import os

import pandas as pd
import psycopg2
import shapely


class OrmaImport(object):
    def __init__(self):
        self.conn = self.get_db_conn()

    def get_data(self):
        sql = """SELECT way_id, st_asBinary(geom) AS geom, district, province, "length" from lines_with_admin where length>0"""
        ways_by_region = pd.read_sql(sql, self.conn)

        ways_by_region.geom = ways_by_region.geom.apply(shapely.wkb.loads)
        ways_by_region.columns = ["way_id", "geom", "district_id", "province_id", "length"]

        ways_by_region = ways_by_region.assign(way_id_district="")
        ways_by_region["way_id_district"] = (
            ways_by_region["way_id"].astype(str) + "_" + ways_by_region["district_id"].astype(str)
        )
        # ways_by_region = ways_by_region[ways_by_region['length']>0.025] #Lets only get stretches longer than 25 meters
        ways_by_region.head()

    @staticmethod
    def get_db_conn():
        return psycopg2.connect(
            database=os.environ["VN_ORMA_DB_DB"],
            user=os.environ["VN_ORMA_DB_USER"],
            password=os.environ["VN_ORMA_DB_PASS"],
            host=os.environ["VN_ORMA_DB_HOST"],
        )


def bytea2bytes(value, cur):
    m = psycopg2.BINARY(value, cur)
    if m is not None:
        return m.tobytes()


bytea_to_bytes = psycopg2.extensions.new_type(psycopg2.BINARY.values, "BYTEA2BYTES", bytea2bytes)
psycopg2.extensions.register_type(bytea_to_bytes)
