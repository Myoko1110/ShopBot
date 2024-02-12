import sqlite3
from typing import Union

from utils import Database


class GuildSettings:
    def __init__(self,
                 guild_id: int,
                 client_role: Union[int, None],
                 buyer_role: Union[int, None],
                 admin_role: Union[int, None],
                 verify_role: Union[int, None],
                 log_channel: Union[int, None],
                 request_ticket_category: Union[int, None],
                 slot_category: Union[int, None],
                 ticket_category: Union[int, None],
                 ):
        self.guild_id = guild_id
        self.client_role = client_role
        self.buyer_role = buyer_role
        self.admin_role = admin_role
        self.verify_role = verify_role
        self.log_channel = log_channel
        self.request_ticket_category = request_ticket_category
        self.slot_category = slot_category
        self.ticket_category = ticket_category

    def __str__(self):
        return f"RoleSetting({self.guild_id})"

    @staticmethod
    def set_client(guild_id: int, client_role: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param client_role: クライアントのロールID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, client_role) VALUES(?, ?)"
        cur.execute(sql, (guild_id, client_role))

        conn.commit()
        conn.close()

    @staticmethod
    def set_buyer(guild_id: int, buyer_role: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param buyer_role: 購入者のロールID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, buyer_role) VALUES(?, ?)"
        cur.execute(sql, (guild_id, buyer_role))

        conn.commit()
        conn.close()

    @staticmethod
    def set_admin(guild_id: int, admin_role: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param admin_role: 管理者のロールID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, admin_role) VALUES(?, ?)"
        cur.execute(sql, (guild_id, admin_role))

        conn.commit()
        conn.close()

    @staticmethod
    def set_verify(guild_id: int, verify_role: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param verify_role: 認証者のロールID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, verify_role) VALUES(?, ?)"
        cur.execute(sql, (guild_id, verify_role))

        conn.commit()
        conn.close()

    @staticmethod
    def set_log_channel(guild_id: int, log_channel: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param log_channel: ログのチャンネルID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, log_channel) VALUES(?, ?)"
        cur.execute(sql, (guild_id, log_channel))

        conn.commit()
        conn.close()

    @staticmethod
    def set_request_category(guild_id: int, request_category: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param request_category: 依頼チケットのカテゴリーID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, request_category) VALUES(?, ?)"
        cur.execute(sql, (guild_id, request_category))

        conn.commit()
        conn.close()

    @staticmethod
    def set_slot_category(guild_id: int, slot_category: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param slot_category: 依頼チケットのカテゴリーID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, slot_category) VALUES(?, ?)"
        cur.execute(sql, (guild_id, slot_category))

        conn.commit()
        conn.close()

    @staticmethod
    def set_ticket_category(guild_id: int, ticket_category: Union[int, None] = None):
        """
        ギルドの設定を設定(更新)します

        :param guild_id: ギルドID
        :param ticket_category: チケットを発行するカテゴリーID
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        sql = "REPLACE INTO guild_settings(guild_id, ticket_category) VALUES(?, ?)"
        cur.execute(sql, (guild_id, ticket_category))

        conn.commit()
        conn.close()

    @staticmethod
    def get(guild_id: int):
        conn = Database.get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = "SELECT * FROM guild_settings WHERE guild_id = ?"
        cur.execute(sql, (guild_id,))

        result = cur.fetchone()
        if not result:
            return None

        return GuildSettings(
            result["guild_id"],
            result["client_role"],
            result["buyer_role"],
            result["admin_role"],
            result["verify_role"],
            result["log_channel"],
            result["request_category"],
            result["slot_category"],
            result["ticket_category"],
        )
