import datetime

import yaml

import config


class GiveawayData:
    def __init__(self, message_id: int, entries: list[int], end_at: datetime.datetime,
                 channel_id: int, winners: int, prize: str):
        self.message_id = message_id
        self.entries = entries
        self.end_at = end_at
        self.channel_id = channel_id
        self.winners = winners
        self.prize = prize


class GiveawayDataManager:
    @staticmethod
    def create(id: int, end_at: datetime.datetime, channel_id: int, winners, prize):
        with open(file=config.GIVEAWAY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                data = {}

            data[id] = {"entries": [], "end_at": str(end_at), "channel_id": channel_id,
                        "winners": winners, "prize": prize}

        with open(file=config.GIVEAWAY_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)

    @staticmethod
    def add_entries(id: int, user_id: int):
        with open(file=config.GIVEAWAY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            if user_id in data[id]["entries"]:
                return False

            data[id]["entries"].append(user_id)

        with open(file=config.GIVEAWAY_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)
            return True

    @staticmethod
    def getall():
        with open(file=config.GIVEAWAY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            return [GiveawayData(i, j["entries"], datetime.datetime.strptime(j["end_at"], '%Y-%m-%d %H:%M:%S'), j["channel_id"], j["winners"], j["prize"]) for i, j in
                    data.items()]

    @staticmethod
    def get(id: int):
        with open(file=config.GIVEAWAY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            if id not in data:
                return False

            ga = data[id]

            return GiveawayData(id, ga["entries"],
                                 datetime.datetime.strptime(ga["end_at"], '%Y-%m-%d %H:%M:%S'),
                                 ga["channel_id"], ga["winners"], ga["prize"])

    @staticmethod
    def delete(id: int):
        with open(file=config.GIVEAWAY_DATA_PATH, mode="r") as fr:
            data = yaml.safe_load(fr)

            if not data:
                return None

            if id not in data:
                return False

            del data[id]

        with open(file=config.GIVEAWAY_DATA_PATH, mode="w") as fw:
            yaml.dump(data, fw, default_flow_style=False)
            return True
