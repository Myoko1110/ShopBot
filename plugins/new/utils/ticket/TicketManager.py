import discord
import yaml

import config
from .TicketStatus import TicketStatus


def create_ticket(id: id, user: discord.User, request: str, log: discord.Message):
    with open(file=config.TICKET_DATA_PATH, mode="a+") as f:
        data = yaml.safe_load(f)

        if not data:
            data = {}

        d = {
            "user_id": user.id,
            "request": request,
            "log": log.id,
            "status": TicketStatus.WAITING.name,
        }

        data[id] = d

        yaml.dump(data, f, default_flow_style=False)


async def create_ticket_channel(user: discord.User, category: discord.CategoryChannel):
    overwrites = {
        category.guild.get_role(config.ADMIN_ROLE_ID):
            discord.PermissionOverwrite(read_messages=True, send_messages=True),
        user:
            discord.PermissionOverwrite(read_messages=True, send_messages=True),
        category.guild.default_role:
            discord.PermissionOverwrite(read_messages=False, send_messages=False),
    }

    channel = config.TICKET_CHANNEL_NAME.replace("{username}", user.name)
    return await category.create_text_channel(channel, overwrites=overwrites)


def get_ticket(id: int):
    with open(file=config.TICKET_DATA_PATH, mode="r") as f:
        data = yaml.safe_load(f)
        if not data:
            return None

        if id in data:
            d = data[id]
            d["status"] = TicketStatus(d["status"])

        return {
            "id": id,
            "request": d["request"],
            "user_id": d["user_id"],
            "status": d["status"],
            "log": d["log"]
        }
