from sqlalchemy.types import UserDefinedType, TypeDecorator, Integer
from sqlalchemy.sql import type_coerce
from sqlalchemy import func
from fire.api.model import geometry

# Based on https://github.com/zzzeek/sqlalchemy/blob/master/examples/postgis/postgis.py


class Geometry(UserDefinedType):
    """Base Oracle Geometry column type."""

    name = "GEOMETRY"

    def __init__(self, dimension=None, srid=-1):
        self.dimension = dimension
        self.srid = srid

    def _coerce_compared_value(self, op, value):
        return self

    def get_col_spec(self):
        return self.name

    def bind_expression(self, bindvalue):
        return Geometry(bindvalue)

    def column_expression(self, col):
        return func.SDO_UTIL.TO_WKTGEOMETRY(col, type_=self)

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, geometry.Geometry):
                return value.wkt
            else:
                return value

        return process

    def result_processor(self, dialect, coltype):
        fac = geometry.geometry_factory

        def process(value):
            if value is not None:
                return fac(value, self.srid)
            else:
                return value

        return process

    def adapt(self, impltype):
        return impltype(dimension=self.dimension, srid=self.srid)


class Point(Geometry):
    name = "POINT"


class Curve(Geometry):
    name = "CURVE"


class LineString(Curve):
    name = "LINESTRING"


class IntegerEnum(TypeDecorator):
    """Column type which persists the integer value of a Python enumeration"""

    impl = Integer

    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)
