import datetime
from typing import List, Dict

from dataclasses import dataclass, field
from marshmallow import fields, Schema

from b123_api.helpers import localize
from b123_api.translations import car_services as service_translate


@dataclass(unsafe_hash=True, order=True)
class Train:
    t_id: str = field(compare=True)
    t_name: str = field(compare=False)
    start_s: str = field(compare=False)
    o123_code: str = field(compare=False)
    end_s: str = field(compare=False)
    d123_code: str = field(compare=False)
    duration: int = field(compare=False)
    service_classes: Dict[str, List[str]] = field(default=None, compare=False)
    services: Dict[str, List[str]] = field(default=None, compare=False)
    _dt_start_sell: datetime.datetime = None
    _dtt_d123: datetime.datetime = field(default=None, compare=False)
    dtt_a123: datetime.datetime = field(default=None, compare=False)
    sort_id: int = 0
    status: str = None

    def __init__(self, t_id, t_name=None, o123_name=None,
                 o123_code=None,
                 d123_name=None, d123_code=None,
                 dtt_d123=None,
                 dtt_a123=None, duration=None, car_groups=None,
                 car_services=None):
        self.t_id = t_id
        self.t_name = t_name
        self.start_s = o123_name
        self.o123_code = o123_code
        self.end_s = d123_name
        self.d123_code = d123_code
        if dtt_d123:
            self._dtt_d123 = localize(dtt_d123)
        if dtt_a123:
            self.dtt_a123 = localize(dtt_a123)
        self.duration = duration
        if car_groups:
            self.service_classes = {}
            if isinstance(car_groups, dict):
                self.service_classes = car_groups
            else:
                for car_group in car_groups:
                    for key, value in car_group.items():
                        self.service_classes.setdefault(key, []).append(value)
        if car_services:
            self.services = {}
            if isinstance(car_services, dict):
                self.services = car_services
            else:
                for service in car_services:
                    translate = service_translate[service]
                    self.services.setdefault('eng', []).append(service)
                    self.services.setdefault('rus', []).append(translate)
        if self.dtt_d123:
            self._dt_start_sell = self.dtt_d123 - datetime.timedelta(
                days=89)

    @property
    def dtt_d123(self):
        return self._dtt_d123

    @dtt_d123.setter
    def dtt_d123(self, date: 'datetime.date'):
        d = datetime.datetime.combine(date, self.dtt_d123.time())
        d = d.replace(tzinfo=self.dtt_d123.tzinfo)
        delta = d - self.dtt_d123
        self._dtt_d123 = d
        self.dtt_a123 = self.dtt_a123 + delta

    @property
    def dt_start_sell(self):
        return self._dt_start_sell

    @dt_start_sell.setter
    def dt_start_sell(self, days: int):
        self._dt_start_sell = self.dtt_d123 - datetime.timedelta(days=days)


class TRequestSchema(Schema):
    dtt_d123 = fields.Date(required=True)
    start_s = fields.Str(required=True)
    start_s_name = fields.Str(required=True)
    end_s = fields.Str(required=True)
    end_s_name = fields.Str(required=True)
    lng = fields.Str(missing='rus')
    email = fields.Str()
    user_id = fields.Str()


class TResponseSchema(Schema):
    id = fields.Int(attribute='sort_id', required=True)
    t_id = fields.Str(required=True)
    t_name = fields.Str()
    dtt_d123 = fields.DateTime()
    dtt_a123 = fields.DateTime()
    duration = fields.Int()
    service_classes = fields.List(fields.Str())
    services = fields.List(fields.Str())
    dt_start_sell = fields.DateTime()
    start_s = fields.Str()
    end_s = fields.Str()
    status = fields.Str()
