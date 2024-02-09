import datetime
from enum import Enum
from typing import Union

import yaml

import config


class SlotType(Enum):
    WEEKLY = "一週間"
    MONTHLY = "一ヶ月"
    PERMANENT = "永久"
    MUTUAL = "相互"


class SlotData:
    def __init__(self, user_id: int, expiry: Union[datetime.date, None], channel_id: int):
        self.user_id = user_id
        self.expiry = expiry
        self.channel_id = channel_id


class SlotDataManager:
    @staticmethod
    def create(sd: SlotData):
        with open(file=config.SLOT_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                data = {}


            if sd.expiry:
                data[sd.channel_id] = {"user_id": sd.user_id, "expiry": str(sd.expiry)}
            else:
                data[sd.channel_id] = {"user_id": sd.user_id, "expiry": sd.expiry}

        with open(file=config.SLOT_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)

    @staticmethod
    def delete(id: int):
        with open(file=config.SLOT_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            if id not in data:
                return False

            del data[id]

        with open(file=config.SLOT_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)
            return True

    @staticmethod
    def getall():
        with open(file=config.SLOT_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            return [SlotData(j["user_id"], datetime.datetime.strptime(j["expiry"], '%Y-%m-%d').date(), i) for i, j in data.items() if j["expiry"]]

    @staticmethod
    def get(id: int):
        with open(file=config.SLOT_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            if id not in data:
                return False

            return SlotData(data[id]["user_id"],
                            datetime.datetime.strptime(data[id]["expiry"], '%Y-%m-%d').date(),
                            id)

    @staticmethod
    def extend(id: int, date: datetime.date):
        with open(file=config.SLOT_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            if id not in data:
                return False

            data[id]["expiry"] = str(date)

        with open(file=config.SLOT_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)
            return True
