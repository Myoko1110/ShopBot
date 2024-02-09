import yaml

import config
from .Complete import Complete


def create_button(cb: 'Complete'):
    with open(file=config.COMPLETE_BUTTON_DATA_PATH, mode="a+") as f:
        data = yaml.safe_load(f)

        if not data:
            data = {}

        d = {
            "message_id": cb.message_id,
            "user_id": cb.user_id,
        }

        data[cb.channel_id] = d

        yaml.dump(data, f, default_flow_style=False)


def get_buttons():
    with open(file=config.COMPLETE_BUTTON_DATA_PATH, mode="r") as f:
        data = yaml.safe_load(f)
        if not data:
            return None

        return [Complete(i, j["message_id"], j["user_id"]) for i, j in data.items()]
