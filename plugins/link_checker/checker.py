import re

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

from utils import GuildSettings


class LinkChecker(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="linkchecker", description="リンクチェッカーをオン・オフします")
    async def switch(self, ctx: discord.Interaction):
        setting = GuildSettings.get(ctx.guild_id)

        if not setting:
            GuildSettings.set_link_checker(ctx.guild_id, True)
            await ctx.response.send_message("リンクチェッカーをオンにしました", ephemeral=True)

        elif setting.link_checker:
            GuildSettings.set_link_checker(ctx.guild_id, False)
            await ctx.response.send_message("リンクチェッカーをオフにしました", ephemeral=True)

        else:
            GuildSettings.set_link_checker(ctx.guild_id, True)
            await ctx.response.send_message("リンクチェッカーをオンにしました", ephemeral=True)

    @Cog.listener()
    async def on_message(self, msg: discord.Message):
        try:
            setting = GuildSettings.get(msg.guild.id)
        except AttributeError:
            return

        if not setting or not setting.link_checker:
            return

        if "pay.paypay.ne.jp" in msg.content:
            link_result = re.findall(r"\[(.*?)]\((https?://.*?)\)", msg.content)
            if len(link_result) != 0:
                links = {}

                for i in link_result:
                    if not i[1].startswith("https://pay.paypay.ne.jp/"):
                        links[i[1]] = True
                    else:
                        links[i[1]] = False

                if links.values():
                    if True in links.values():
                        embed = discord.Embed(
                            title=":warning: 詐欺リンク",
                            description="このリンクはPayPayの支払いリンクではありません",
                            color=discord.Color.red(),
                        )

                        content = ""
                        for link, is_dangerous in links.items():
                            status = ":x: 詐欺" if is_dangerous else ":blue_circle: 正常"
                            content += f"{status}: `{link}`\n"

                        embed.add_field(name="検証結果", value=content)

                    else:
                        embed = discord.Embed(
                            title=":white_check_mark: 正常リンク",
                            description="安全性が確認できました",
                            color=3916277,
                        )

                        content = ""
                        for link, is_dangerous in links.items():
                            status = ":x: 詐欺" if is_dangerous else ":blue_circle: 正常"
                            content += f"{status}: `{link}`\n"

                        embed.add_field(name="検証結果", value=content)
                    await msg.reply(embed=embed, mention_author=False)
