import asyncio

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

from utils import GuildSettings


class TicketCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        bot.add_view(CompleteButton(self.bot))
        bot.add_view(TicketButton(self.bot))

    @app_commands.command(name="ticket", description="チケット作成ボタンを送信します")
    @app_commands.describe(title="タイトル", description="説明")
    @app_commands.default_permissions(administrator=True)
    async def ticket(self, ctx: discord.Interaction, title: str, description: str):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)
            return

        setting = GuildSettings.get(ctx.guild_id)
        if not setting.ticket_category:
            await ctx.response.send_message("チケットを作成するカテゴリーが設定されていません。/channelsetで設定してください。", ephemeral=True)
            return

        embed = discord.Embed(
            title=title,
            description=description
        )

        await ctx.channel.send(embed=embed, view=TicketButton(self.bot))
        await ctx.response.send_message("チケット作成ボタンを送信しました", ephemeral=True)


class TicketButton(discord.ui.View):
    def __init__(self, bot: Bot, timeout=None):
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="発行", style=discord.ButtonStyle.primary, custom_id="issue_ticket")
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        setting = GuildSettings.get(ctx.guild_id)

        ch = await self.bot.get_channel(setting.ticket_category).create_text_channel(name=f"チケット-{ctx.user.name}")
        await ch.send(view=CompleteButton(self.bot))

        await ctx.response.send_message(f"チケットを作成しました: {ch.mention}", ephemeral=True)


class CompleteButton(discord.ui.View):
    def __init__(self, bot: Bot, timeout=None):
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red, custom_id="stop_ticket")
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="本当にこの依頼を終了しますか？",
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
