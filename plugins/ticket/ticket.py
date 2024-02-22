import asyncio

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import config
from plugins.ticket.utils import Ticket
from utils import GuildSettings


class TicketCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        bot.add_view(CompleteButton(self.bot))

        for i in Ticket.get_all():
            role = self.bot.get_guild(i.guild_id).get_role(i.role_id) if i.role_id else None
            bot.add_view(TicketButton(self.bot, self.bot.get_channel(i.category_id), role, i.first_message), message_id=i.message_id)

    @app_commands.command(name="ticket", description="チケット作成ボタンを送信します")
    @app_commands.describe(title="タイトル",
                           description="パネルの説明",
                           image="パネルに乗せる画像のURL",
                           category="チケットを作成するカテゴリ",
                           role="チケット作成時にメンションするロール",
                           first_message="チケット作成時に最初に送るメッセージ",)
    @app_commands.default_permissions(administrator=True)
    async def ticket(self,
                     ctx: discord.Interaction,
                     title: str,
                     description: str,
                     category: discord.CategoryChannel,
                     role: discord.Role = None,
                     image: str = None,
                     first_message: str = None):

        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)
            return

        """
        setting = GuildSettings.get(ctx.guild_id)
        if not setting.ticket_category:
            await ctx.response.send_message("チケットを作成するカテゴリーが設定されていません。/channelsetで設定してください。", ephemeral=True)
            return
        """

        embed = discord.Embed(
            title=title,
            description=description
        )

        if image:
            embed.set_image(url=image)

        message = await ctx.channel.send(embed=embed, view=TicketButton(self.bot, category, role, first_message))

        role_id = None
        if role:
            role_id = role.id
        Ticket.create(ctx.guild_id, ctx.channel_id, message.id, role_id, category.id, first_message)
        await ctx.response.send_message("チケット作成ボタンを送信しました", ephemeral=True)


class TicketButton(discord.ui.View):
    def __init__(self, bot: Bot, category: discord.CategoryChannel, role: discord.Role=None, first_message=None, timeout=None):
        self.bot = bot
        self.category = category
        self.role = role
        self.first_message = first_message
        super().__init__(timeout=timeout)

    @discord.ui.button(label="発行", style=discord.ButtonStyle.primary, custom_id="issue_ticket")
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        ticket_name = config.TICKET_CHANNEL_NAME.replace("{username}", ctx.user.name)
        ch = await self.category.create_text_channel(name=ticket_name)

        if self.role:
            content = f"{self.role.mention}\n{self.first_message}"
        else:
            content = self.first_message

        await ch.send(content, view=CompleteButton(self.bot))
        await ctx.response.send_message(f"チケットを作成しました: {ch.mention}", ephemeral=True)


class CompleteButton(discord.ui.View):
    def __init__(self, bot: Bot, timeout=None):
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red, custom_id="stop_ticket")
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="本当にこのチケットを終了しますか？",
            description="終了する場合は下の終了ボタンを押してください"
        )

        await ctx.response.send_message(embed=embed, view=ConfirmButton(ctx.message, self.bot), ephemeral=True)


class ConfirmButton(discord.ui.View):
    def __init__(self, message: discord.Message, bot: Bot):
        self.message = message
        self.bot = bot
        super().__init__()

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="ご利用ありがとうございました",
            description="このチャンネルは10秒後に削除されます"
        )

        # メッセージ削除
        await self.message.delete()

        # embed送信
        await ctx.response.send_message(embed=embed)

        # 10秒後に削除
        await asyncio.sleep(10)
        await ctx.channel.delete()
