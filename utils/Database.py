import sqlite3

import config


class Database:
    @staticmethod
    def initialize():
        """
        データベースを初期化します
        """

        conn = Database.get_connection()
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS request_tickets(guild_id INTEGER, channel_id INTEGER PRIMARY KEY, user_id INTEGER, status TEXT, log_message_id INTEGER, request_value INTEGER, complete_button INTEGER, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS request_buttons(guild_id INTEGER, channel_id INTEGER, message_id INTEGER PRIMARY KEY, title TEXT, description TEXT, requests JSON, category_id INTEGER, role_id INTEGER, first_message TEXT, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS guild_settings(guild_id INTEGER PRIMARY KEY, client_role INTEGER, buyer_role INTEGER, admin_role INTEGER, verify_role INTEGER, handle_role INTEGER, log_channel INTEGER, request_category INTEGER, slot_category INTEGER, ticket_category INTEGER, link_checker INTEGER)")
        cur.execute("CREATE TABLE IF NOT EXISTS slot_channels(guild_id INTEGER, channel_id INTEGER, user_id INTEGER, expiry TEXT, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS giveaway(guild_id INTEGER, channel_id INTEGER, message_id INTEGER PRIMARY KEY, host_id INTEGER, prize TEXT, winner_members INTEGER, entries JSON, end_at TEXT, created_at TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS ticket_buttons(guild_id INTEGER, channel_id INTEGER, message_id INTEGER PRIMARY KEY, role_id INTEGER, category_id INTEGER, first_message TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS tickets(guild_id INTEGER, channel_id INTEGER PRIMARY KEY, user_id INTEGER, status TEXT, log_message_id INTEGER, complete_button INTEGER, created_at TEXT)")
        conn.commit()
        conn.close()

    @staticmethod
    def get_connection():
        """
        コネクションを取得します

        :return: Connection
        """

        return sqlite3.connect(config.DATABASE_NAME)
