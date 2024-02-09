import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog


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

    @app_commands.command(name="handle")
    async def handle(self, ctx: discord.Interaction):
        await ctx.response.send_message(embed=enable, view=HandleButton())


class HandleButton(discord.ui.View):

    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="🔁",
                       custom_id="handle_button")
    async def request(self, ctx: discord.Interaction, button):

        description = ctx.message.embeds[0].description

        if description == "現在対応可能です":
            await ctx.message.edit(embed=disable)
        else:
            await ctx.message.edit(embed=enable)

        await ctx.response.send_message("対応状況を更新しました！", ephemeral=True)
