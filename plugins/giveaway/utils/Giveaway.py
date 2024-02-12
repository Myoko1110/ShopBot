import json
import sqlite3
from datetime import datetime

from utils import Database


class Giveaway:
    def __init__(self,
                 guild_id: int,
                 channel_id: int,
                 message_id: int,
                 host_id: int,
                 prize: str,
                 winner_members: int,
                 entries: list[int],
                 end_at: datetime,
                 created_at: datetime):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.host_id = host_id
        self.prize = prize
        self.winner_members = winner_members
        self.entries = entries
        self.end_at = end_at
        self.created_at = created_at

    @staticmethod
    def create(guild_id: int,
               channel_id: int,
               message_id: int,
               host_id: int,
               prize: str,
               winner_members: int,
               end_at: datetime):

        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        sql = "INSERT INTO giveaway VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(sql, (guild_id, channel_id, message_id, host_id, prize, winner_members, json.dumps([]), str(end_at), str(now)))

        conn.commit()
        conn.close()

    @staticmethod
    def add_entry(message_id: int, user_id: int):
        conn = Database.get_connection()
        cur = conn.cursor()

        entries = Giveaway.get(message_id).entries
        if user_id in entries:
            return False

        entries.append(user_id)

        sql = "UPDATE giveaway SET entries = ? WHERE message_id = ?"
        cur.execute(sql, (json.dumps(entries), message_id))

        conn.commit()
        conn.close()

        return True

    @staticmethod
    def get(message_id: int):
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM giveaway WHERE message_id = ?"
        cur.execute(sql, (message_id,))

        result = cur.fetchone()
        if not result:
            return None

        return Giveaway(
            result["guild_id"],
            result["channel_id"],
            result["message_id"],
            result["host_id"],
            result["prize"],
            result["winner_members"],
            json.loads(result["entries"]),
            datetime.strptime(result["end_at"], "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    def get_all():
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM giveaway"
        cur.execute(sql)

        results = cur.fetchall()
        if not results:
            return None

        return [Giveaway(
            result["guild_id"],
            result["channel_id"],
            result["message_id"],
            result["host_id"],
            result["prize"],
            result["winner_members"],
            json.loads(result["entries"]),
            datetime.strptime(result["end_at"], "%Y-%m-%d %H:%M:%S"),
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        ) for result in results]

    @staticmethod
    def delete(message_id: int):
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "DELETE FROM giveaway WHERE message_id = ?"
        cur.execute(sql, (message_id,))

        conn.commit()
        conn.close()
