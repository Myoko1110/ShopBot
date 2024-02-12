import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

from utils import GuildSettings


class Verify(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        bot.add_view(VerifyButtonView())

    @app_commands.command(name="verify", description="認証ボタンを送信します")
    @app_commands.default_permissions(administrator=True)
    async def new(self, ctx: discord.Interaction):
        if not ctx.user.bot and ctx.user.guild_permissions.administrator:
            setting = GuildSettings.get(ctx.guild_id)
            if not setting.verify_role:
                await ctx.response.send_message("認証時に付与するロールが設定されていません。/channelsetで設定してください。", ephemeral=True)
                return

            embed = discord.Embed(
                title="認証",
                description="下のボタンを押して認証してください",
                color=0x27e32d,
            )

            await ctx.channel.send(embed=embed, view=VerifyButtonView())
            await ctx.response.send_message("認証メッセージを送信しました", ephemeral=True)

        else:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)


class VerifyButtonView(discord.ui.View):

    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="認証する", style=discord.ButtonStyle.success, emoji="☑",
                       custom_id="verify_button")
    async def request(self, ctx: discord.Interaction, button):
        if not ctx.user.bot:
            setting = GuildSettings.get(ctx.guild_id)
            role = ctx.guild.get_role(setting.verify_role)

            await ctx.user.add_roles(role)
            await ctx.response.send_message("ロールを付与しました！", ephemeral=True)
