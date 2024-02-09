import discord

from .TicketStatus import TicketStatus


class Ticket:
    def __init__(
            self,
            id: int,
            request: str,
            user: discord.User,
            status: 'TicketStatus',
            log: discord.Message
    ):
        self.id = id
        self.request = request
        self.user = user
        self.status = status
        self.log = log
