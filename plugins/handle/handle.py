import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

from utils import GuildSettings

enable = discord.Embed(
    title="対応状況",
    description="現在対応可能です",
    color=discord.Color.green(),
)

disable = discord.Embed(
    title="対応状況",
    description="現在対応不可能です",
    color=discord.Color.red(),
)


class Handle(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        bot.add_view(HandleButton())

    @app_commands.command(name="handle", description="ハンドルを送信します")
    @app_commands.default_permissions(administrator=True)
    async def handle(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=enable, view=HandleButton())


class HandleButton(discord.ui.View):

    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="🔁",
                       custom_id="handle_button")
    async def request(self, ctx: discord.Interaction, button):
        setting = GuildSettings.get(ctx.guild_id)
        if setting.handle_role:
            if ctx.user.get_role(setting.handle_role):
                description = ctx.message.embeds[0].description

                if description == "現在対応可能です":
                    await ctx.message.edit(embed=disable)
                else:
                    await ctx.message.edit(embed=enable)

                await ctx.response.send_message("対応状況を更新しました！", ephemeral=True)
            else:
                await ctx.response.send_message("実行できません", ephemeral=True)

        else:
            if ctx.user.guild_permissions.administrator:
                description = ctx.message.embeds[0].description

                if description == "現在対応可能です":
                    await ctx.message.edit(embed=disable)
                else:
                    await ctx.message.edit(embed=enable)

                await ctx.response.send_message("対応状況を更新しました！", ephemeral=True)

            else:
                await ctx.response.send_message("実行できません", ephemeral=True)
