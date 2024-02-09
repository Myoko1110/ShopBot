import random
import traceback

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

from plugins.verify.utils.VerifyButtonsData import VerifyButtonData, VerifyButtonManager


class Verify(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        vb = VerifyButtonManager.getall()
        if vb:
            for i in vb:
                bot.add_view(VerifyButton(bot.get_guild(i.guild_id).get_role(i.role_id)), message_id=i.message_id)
    @app_commands.command(name="verify")
    @app_commands.describe(role="ロール")
    async def new(self, ctx: discord.Interaction, role: discord.Role):
        if not ctx.user.bot and ctx.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="認証",
                description="指示に従って、認証を完了させてください。",
                color=0x27e32d,
            )

            msg = await ctx.channel.send(embed=embed, view=VerifyButton(role))
            await ctx.response.send_message("認証メッセージを送信しました", ephemeral=True)

            vb = VerifyButtonData(msg.id, ctx.channel_id, role.id, ctx.guild_id)
            VerifyButtonManager.create(vb)
            
        else:
            await ctx.response.send_message("このコマンドを実行する権限がありません", ephemeral=True)


class VerifyButton(discord.ui.View):

    def __init__(self, role: discord.Role, timeout=None):
        self.role = role
        super().__init__(timeout=timeout)

    @discord.ui.button(label="認証する", style=discord.ButtonStyle.success, emoji="☑",
                       custom_id="verify_button")
    async def request(self, ctx: discord.Interaction, button):
        await ctx.response.send_modal(VerifyModal(self.role))


class VerifyModal(discord.ui.Modal):
    number = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="解答",
        custom_id="verify_answer"
    )

    def __init__(self, role: discord.Role, count=1):
        self.first_number = random.randint(1, 9)
        self.second_number = random.randint(1, 9)

        self.role = role

        self.count = count

        super().__init__(title=f"{self.first_number} + {self.second_number} を計算してください",
                         custom_id="request_form")

    async def on_submit(self, ctx: discord.Interaction):
        answer = self.first_number + self.second_number

        try:
            if int(self.number.value) == answer:
                await ctx.user.add_roles(self.role)
                await ctx.response.send_message("ロールを付与しました！", ephemeral=True)

            else:
                await ctx.response.send_message("解答が違います。もう一度お試しください", ephemeral=True)

        except ValueError:
            await ctx.response.send_message("解答が違います。もう一度お試しください", ephemeral=True)

        except Exception:
            traceback.print_exc()
            await ctx.response.send_message("エラーが発生しました。もう一度お試しください。", ephemeral=True)
