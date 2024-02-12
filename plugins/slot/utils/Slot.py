import sqlite3
from datetime import date, datetime
from typing import Union

from utils import Database


class Slot:
    def __init__(self, guild_id: int, channel_id: int, user_id: int, expiry: Union[date, None], created_at: datetime):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.expiry = expiry
        self.created_at = created_at

    @staticmethod
    def create(guild_id: int, channel_id: int, user_id: int, expiry: Union[date, None]):
        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        sql = "INSERT INTO slot_channels VALUES(?, ?, ?, ?, ?)"
        cur.execute(sql, (guild_id, channel_id, user_id, str(expiry) if expiry else None, now))

        conn.commit()
        conn.close()

    @staticmethod
    def get(channel_id: int):
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM slot_channels WHERE channel_id = ?"
        cur.execute(sql, (channel_id,))

        result = cur.fetchone()
        if not result:
            return None

        return Slot(
            result["guild_id"],
            result["channel_id"],
            result["user_id"],
            datetime.strptime(result["expiry"], "%Y-%m-%d").date() if "expires" in result.keys() else None,
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    def get_all():
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM slot_channels"
        cur.execute(sql)

        results = cur.fetchall()
        if not results:
            return None

        return [Slot(
            result["guild_id"],
            result["channel_id"],
            result["user_id"],
            datetime.strptime(result["expiry"], "%Y-%m-%d").date() if result["expiry"] else None,
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        ) for result in results]

    @staticmethod
    def delete(channel_id: int):
        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "DELETE FROM slot_channels WHERE channel_id = ?"
        cur.execute(sql, (channel_id,))

        conn.commit()
        conn.close()
