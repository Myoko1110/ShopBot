import yaml

import config
from .Request import Request


def create_request(req: 'Request'):
    with open(file=config.REQUEST_DATA_PATH, mode="a+") as f:
        data = yaml.safe_load(f)

        if not data:
            data = {}

        d = {
            "title": req.title,
            "description": req.description,
            "request": req.requests,
        }

        data[req.id] = d

        yaml.dump(data, f, default_flow_style=False)


def get_request(id: int):
    with open(file=config.REQUEST_DATA_PATH, mode="r") as f:
        data = yaml.safe_load(f)
        if not data:
            return None

        return Request(id, data["title"], data["description"], data["request"])


def get_requests():
    with open(file=config.REQUEST_DATA_PATH, mode="r") as f:
        data = yaml.safe_load(f)
        if not data:
            return None

        return [Request(i, j["title"], j["description"], j["request"]) for i, j in data.items()]
