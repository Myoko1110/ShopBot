import json
import sqlite3
from typing import Union

from utils import Database
from datetime import datetime


class RequestButton:
    def __init__(self,
                 title: str,
                 description: str,
                 guild_id: int,
                 channel_id: int,
                 message_id: int,
                 request: list,
                 category_id: int,
                 role_id: int,
                 first_message: str,
                 created_at: datetime):
        self.title = title
        self.description = description
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id
        self.request = request
        self.category_id = category_id
        self.role_id = role_id
        self.first_message = first_message
        self.created_at = created_at

    @staticmethod
    def create(title: str,
               description: str,
               guild_id: int,
               channel_id: int,
               message_id: int,
               request: list,
               category_id: int,
               role_id: int,
               first_message: str):

        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        sql = "INSERT INTO request_buttons VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(sql, (guild_id, channel_id, message_id, title, description, json.dumps(request), category_id, role_id, first_message, str(now)))

        conn.commit()
        conn.close()

    @staticmethod
    def get_all() -> Union[list['RequestButton'], None]:
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM request_buttons"
        cur.execute(sql)

        results = cur.fetchall()
        if not results:
            return None

        return [RequestButton(
            result["title"],
            result["description"],
            result["guild_id"],
            result["channel_id"],
            result["message_id"],
            json.loads(result["requests"]),
            result["category_id"],
            result["role_id"],
            result["first_message"],
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S")
        ) for result in results]
