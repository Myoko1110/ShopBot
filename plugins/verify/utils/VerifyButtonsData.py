from enum import Enum

import yaml

import config


class SlotType(Enum):
    WEEKLY = "一週間"
    MONTHLY = "一ヶ月"
    PERMANENT = "永久"
    MUTUAL = "相互"


class VerifyButtonData:
    def __init__(self, message_id: int, channel_id: int, role_id: int, guild_id: int):
        self.message_id = message_id
        self.channel_id = channel_id
        self.role_id = role_id
        self.guild_id = guild_id


class VerifyButtonManager:
    @staticmethod
    def create(vb: VerifyButtonData):
        with open(file=config.VERIFY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                data = {}

            data[vb.message_id] = {"channel_id": vb.channel_id, "role_id": vb.role_id,
                                   "guild_id": vb.guild_id}

        with open(file=config.VERIFY_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)

    @staticmethod
    def getall():
        with open(file=config.VERIFY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            return [VerifyButtonData(i, j["channel_id"], j["role_id"], j["guild_id"]) for i, j in
                    data.items()]
