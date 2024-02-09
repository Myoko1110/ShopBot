import random
from datetime import datetime
from typing import Union

import discord
from discord import Interaction, app_commands
from discord._types import ClientT
from discord.ext.commands import Bot, Cog


class Embed(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="embed")
    @app_commands.describe(
        title="タイトル",
        title_url="タイトル(URL)",
        description="タイトル(URL)",
        author_name="アーサー",
        author_name_url="アーサー(URL)",
        author_icon="アーサー(icon)",
        footer_text="フッター",
        footer_icon="フッター(icon)",
        color="色",
        image="画像",
        thumbnail="サムネイル",
        field_title_1="フィールドタイトル(1)",
        field_value_1="フィールドバリュー(1)",
        field_inline_1="フィールドインライン(1)",
        field_title_2="フィールドタイトル(2)",
        field_value_2="フィールドバリュー(2)",
        field_inline_2="フィールドインライン(2)",
        field_title_3="フィールドタイトル(3)",
        field_value_3="フィールドバリュー(3)",
        field_inline_3="フィールドインライン(3)",
        field_title_4="フィールドタイトル(4)",
        field_value_4="フィールドバリュー(4)",
        field_inline_4="フィールドインライン(4)",
    )
    async def embed(self, ctx: discord.Interaction,
                  title: str,
                  title_url: str = None,
                  description: str = None,
                  author_name: str = None,
                  author_name_url: str = None,
                  author_icon: str = None,
                  footer_text: str = None,
                  footer_icon: str = None,
                  color: str = None,
                  image: str = None,
                  thumbnail: str = None,
                  field_title_1: str = None,
                  field_value_1: str = None,
                  field_inline_1: bool = False,
                  field_title_2: str = None,
                  field_value_2: str = None,
                  field_inline_2: bool = False,
                  field_title_3: str = None,
                  field_value_3: str = None,
                  field_inline_3: bool = False,
                  field_title_4: str = None,
                  field_value_4: str = None,
                  field_inline_4: bool = False,
                  ):

        if color:
            embed = discord.Embed(
                title=title,
                description=description,
                url=title_url,
                colour=discord.Color.from_str(f"#{color}"),
            )
        else:

            embed = discord.Embed(
                title=title,
                description=description,
                url=title_url,
                colour=0x00b7ff,
            )

        if author_name:
            embed.set_author(name=author_name, url=author_name_url, icon_url=author_icon)

        if footer_text:
            embed.set_footer(text=footer_text, icon_url=footer_icon)

        if image:
            embed.set_image(url=image)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if field_title_1:
            embed.set_field_at(1, name=field_title_1, value=field_value_1, inline=field_inline_1)

        if field_title_2:
            embed.set_field_at(2, name=field_title_2, value=field_value_2, inline=field_inline_2)

        if field_title_3:
            embed.set_field_at(3, name=field_title_3, value=field_value_3, inline=field_inline_3)

        if field_title_4:
            embed.set_field_at(4, name=field_title_4, value=field_value_4, inline=field_inline_4)

        await ctx.channel.send(embed=embed)
        await ctx.response.send_message("Embedを送信しました！", ephemeral=True)

