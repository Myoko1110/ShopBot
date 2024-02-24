import sqlite3

from utils import Database


class TicketButton:
    def __init__(self, guild_id: int, channel_id: int, message_id: int, role_id: int, category_id: int, first_message: str):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.role_id = role_id
        self.category_id = category_id
        self.first_message = first_message

    @staticmethod
    def create(guild_id: int, channel_id: int, message_id: int, role_id: int, category_id: int, first_message: str):

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "INSERT INTO ticket_buttons VALUES(?, ?, ?, ?, ?, ?)"
        cur.execute(sql, (guild_id, channel_id, message_id, role_id, category_id, first_message))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all():
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM ticket_buttons"
        cur.execute(sql)

        results = cur.fetchall()
        if not results:
            return None

        return [TicketButton(
            result["guild_id"],
            result["channel_id"],
            result["message_id"],
            result["role_id"],
            result["category_id"],
            result["first_message"],
        ) for result in results]
