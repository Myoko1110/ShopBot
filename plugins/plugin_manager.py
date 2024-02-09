import traceback

import discord
from discord import app_commands
from discord.app_commands import Group
from discord.ext.commands import Cog, Bot, ExtensionAlreadyLoaded, ExtensionNotLoaded, ExtensionNotFound

ALLOWED_USERS = [
    291126102108143616,
    886089494204399687
]


def is_allowed_user(user_id: int):
    return user_id in ALLOWED_USERS


class ManageCommand(Group):
    def __init__(self, bot: Bot):
        super().__init__(name="plugin")
        self.bot = bot

    @app_commands.command(name="enable")
    async def enable(self, inter: discord.Interaction, plugin: str):
        user = inter.user

        if not is_allowed_user(user.id):
            await inter.response.send_message("実行する権限がありません")
            return

        try:
            await self.bot.load_extension(f"plugins.{plugin}")
        except ExtensionAlreadyLoaded:
            await inter.response.send_message(f"{plugin} は既にロードされています")
        except ExtensionNotFound:
            await inter.response.send_message(f"{plugin} が見つかりません")
        except (Exception,):
            traceback.print_exc()
            await inter.response.send_message(f"{plugin} をロードできません。不明なエラーが発生しました。")
        else:
            await inter.response.send_message(f"{plugin} をロードしました")

    @app_commands.command(name="disable")
    async def disable(self, inter: discord.Interaction, plugin: str):
        user = inter.user

        if not is_allowed_user(user.id):
            await inter.response.send_message("実行する権限がありません")
            return

        try:
            await self.bot.unload_extension(f"plugins.{plugin}")
        except (ExtensionNotFound, ExtensionNotLoaded):
            await inter.response.send_message(f"{plugin} が見つかりません")
        except (Exception,):
            traceback.print_exc()
            await inter.response.send_message(f"{plugin} をアンロードできません。不明なエラーが発生しました。")
        else:
            await inter.response.send_message(f"{plugin} をアンロードしました")

    @app_commands.command(name="refresh")
    async def refresh(self, inter: discord.Interaction, plugin: str):
        user = inter.user

        if not is_allowed_user(user.id):
            await inter.response.send_message("実行する権限がありません")
            return

        try:
            await self.bot.reload_extension(f"plugins.{plugin}")
        except ExtensionNotFound:
            await inter.response.send_message(f"{plugin} が見つかりません")
        except (Exception,):
            traceback.print_exc()
            await inter.response.send_message(f"{plugin} をリロードできません。不明なエラーが発生しました。")
        else:
            await inter.response.send_message(f"{plugin} をリロードしました")

    @app_commands.command(name="resync")
    async def resync(self, inter: discord.Interaction):
        user = inter.user

        if not is_allowed_user(user.id):
            await inter.response.send_message("実行する権限がありません")
            return

        try:
            await self.bot.tree.sync(guild=inter.guild)
        except (Exception,):
            traceback.print_exc()


class PluginManager(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        bot.tree.add_command(ManageCommand(bot))


def setup(bot: Bot):
    return bot.add_cog(PluginManager(bot))