import sqlite3
from datetime import datetime
from typing import Union

from plugins.new.utils import RequestTicketStatus
from utils import Database


class Ticket:
    def __init__(self,
                 guild_id: int,
                 channel_id: int,
                 user_id: int,
                 status: RequestTicketStatus,
                 log_message_id: int,
                 complete_button: int,
                 created_at: datetime
                 ):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.status = status
        self.log_message_id = log_message_id
        self.complete_button = complete_button
        self.created_at = created_at

    @staticmethod
    def create(guild_id: int, channel_id: int, user_id: int, log_message_id: int, complete_button: int,):
        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        sql = "INSERT INTO tickets VALUES(?, ?, ?, ?, ?, ?, ?)"
        cur.execute(sql, (guild_id, channel_id, user_id, RequestTicketStatus.WAITING.name, log_message_id, complete_button, str(now)))

        conn.commit()
        conn.close()

    @staticmethod
    def update(channel_id: int, status: RequestTicketStatus):
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "UPDATE request_tickets SET status = ? WHERE channel_id = ?"
        cur.execute(sql, (status.name, channel_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get(channel_id: int):
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM tickets WHERE channel_id = ?"
        cur.execute(sql, (channel_id,))

        result = cur.fetchone()
        if not result:
            return None

        return Ticket(
            result["guild_id"],
            result["channel_id"],
            result["user_id"],
            RequestTicketStatus(result["status"]),
            result["log_message_id"],
            result["complete_button"],
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    def get_all() -> Union[list['Ticket'], None]:
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM request_tickets"
        cur.execute(sql)

        results = cur.fetchall()
        if not results:
            return None

        return [Ticket(
            result["guild_id"],
            result["channel_id"],
            result["user_id"],
            RequestTicketStatus(result["status"]),
            result["log_message_id"],
            result["complete_button"],
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        ) for result in results]
