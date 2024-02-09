import re

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import config


class WelcomeMessage(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="vending")
    @app_commands.rename(
        title="タイトル",
        about="概要",
        image="画像",
    )
    async def vending(self, ctx: discord.Interaction,
                      title: str,
                      about: str,
                      ):
        await ctx.response.send_message("このコマンドは現在実行できません", ephemeral=True)
        return

        await ctx.response.send_message(embed=embed, view=BuyButton(select, self.bot))

    @Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        pass

