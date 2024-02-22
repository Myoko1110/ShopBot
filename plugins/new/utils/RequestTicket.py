import sqlite3
from datetime import datetime
from typing import Union

import discord

import config
from utils import Database, GuildSettings
from .RequestTicketStatus import RequestTicketStatus


class RequestTicket:
    def __init__(self,
                 guild_id: int,
                 channel_id: int,
                 user_id: int,
                 status: RequestTicketStatus,
                 log_message_id: int,
                 request_value: str,
                 complete_button: int,
                 created_at: datetime):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.status = status
        self.log_message_id = log_message_id
        self.request_value = request_value
        self.complete_button = complete_button
        self.created_at = created_at

    @staticmethod
    def add(guild_id: int,
            channel_id: int,
            user_id: int,
            log_message_id: int,
            request_value: str,
            complete_button_id: int):
        """
        依頼チケットのデータを追加します

        :param guild_id: ギルドID
        :param channel_id: チケットのチャンネルID
        :param user_id: 作成者のユーザーID
        :param log_message_id: ログメッセージのiD
        :param request_value: 依頼の内容
        :param complete_button_id: 終了ボタンのメッセージid
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        now = datetime.now().replace(microsecond=0)
        sql = "INSERT INTO request_tickets VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(sql, (
        guild_id, channel_id, user_id, RequestTicketStatus.WAITING.name, log_message_id,
        request_value, complete_button_id, str(now)))

        conn.commit()
        conn.close()

    @staticmethod
    def update(channel_id: int, status: RequestTicketStatus):
        """
        ステータスを更新します

        :param channel_id: チャンネルID
        :param status: ステータス
        """

        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "UPDATE request_tickets SET status = ? WHERE channel_id = ?"
        cur.execute(sql, (status.value, channel_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get(channel_id: int) -> Union['RequestTicket', None]:
        """
        チャンネルIDからRequestTicket型を取得します

        :param channel_id: チャンネルID
        :return: RequestTicket型
        """

        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM request_tickets WHERE channel_id = ?"
        cur.execute(sql, (channel_id,))

        result = cur.fetchone()
        if not result:
            return None

        return RequestTicket(
            result["guild_id"],
            result["channel_id"],
            result["user_id"],
            RequestTicketStatus(result["status"]),
            result["log_message_id"],
            result["request_value"],
            result["complete_button"],
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        )

    @staticmethod
    def get_all() -> Union[list['RequestTicket'], None]:
        """
        すべてのRequestTicket型を取得します

        :return: RequestTicketのリスト
        """

        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM request_tickets"
        cur.execute(sql)

        results = cur.fetchall()
        if not results:
            return None

        return [RequestTicket(
            result["guild_id"],
            result["channel_id"],
            result["user_id"],
            RequestTicketStatus(result["status"]),
            result["log_message_id"],
            result["request_value"],
            result["complete_button"],
            datetime.strptime(result["created_at"], "%Y-%m-%d %H:%M:%S"),
        ) for result in results]

    @staticmethod
    async def create_ticket_channel(user: discord.User, category: discord.CategoryChannel, setting: GuildSettings):
        """
        チケットチャンネルを作成します

        :param user: ユーザー
        :param category: カテゴリー
        :param setting: 設定
        :return: チャンネル
        """

        overwrites = {
            user:
                discord.PermissionOverwrite(read_messages=True, send_messages=True),
            category.guild.default_role:
                discord.PermissionOverwrite(read_messages=False, send_messages=False),
        }
        if setting.admin_role:
            overwrites[category.guild.get_role(setting.admin_role)] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = config.TICKET_CHANNEL_NAME.replace("{username}", user.name)
        return await category.create_text_channel(channel, overwrites=overwrites)
