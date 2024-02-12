import datetime
import random
import re

import discord
from discord import Interaction, app_commands
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

from plugins.giveaway.utils import Giveaway


class GiveawayCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        bot.add_view(EntryButton())
        self.giveaway_end.start()

    @app_commands.command(name="gcreate", description="Giveawayを作成します")
    @app_commands.default_permissions(administrator=True)
    async def gcreate(self, ctx: discord.Interaction):
        await ctx.response.send_modal(GiveawayModal())

    @app_commands.command(name="gend", description="Giveawayを即座に終了します")
    @app_commands.describe(id="GiveawayのID(メッセージID)")
    @app_commands.default_permissions(administrator=True)
    async def gend(self, ctx: discord.Interaction, id: str):
        try:
            i = Giveaway.get(int(id))
        except ValueError:
            ctx.response.send_message("Giveawayが見つかりませんでした", ephemeral=True)
            return

        if not i:
            ctx.response.send_message("Giveawayが見つかりませんでした", ephemeral=True)
            return

        msg = await self.bot.get_channel(i.channel_id).fetch_message(i.message_id)
        await msg.edit(view=None)

        if not i.entries:
            await msg.reply("エントリーがなかったため当選者はいませんでした")
            Giveaway.delete(i.message_id)
            return

        entries = i.winners if i.winners < len(i.entries) else len(i.entries)

        winner = [self.bot.get_user(j).mention for j in random.sample(i.entries, entries)]
        await msg.reply(", ".join(winner) + f"が**{i.prize}**を獲得しました！")
        Giveaway.delete(i.message_id)

        await ctx.response.send_message("")

    @app_commands.command(name="gdelete", description="Giveawayを削除します")
    @app_commands.describe(id="GiveawayのID(メッセージID)")
    @app_commands.default_permissions(administrator=True)
    async def gdelete(self, ctx: discord.Interaction, id: str):
        try:
            i = Giveaway.get(int(id))
        except ValueError:
            ctx.response.send_message("Giveawayが見つかりませんでした", ephemeral=True)
            return

        if not i:
            ctx.response.send_message("Giveawayが見つかりませんでした", ephemeral=True)

        msg = await self.bot.get_channel(i.channel_id).fetch_message(i.message_id)
        await msg.edit(view=None)

        Giveaway.delete(i.message_id)
        await ctx.response.send_message("Giveawayを削除しました", ephemeral=True)

    @tasks.loop(seconds=10)
    async def giveaway_end(self):
        giveaway = Giveaway.get_all()
        if not giveaway:
            return

        now = datetime.datetime.now()
        for i in giveaway:
            if now > i.end_at:

                msg = await self.bot.get_channel(i.channel_id).fetch_message(i.message_id)
                await msg.edit(view=None)

                if not i.entries:
                    await msg.reply("エントリーがなかったため当選者はいませんでした")
                    Giveaway.delete(i.message_id)
                    return

                entries = i.winner_members if i.winner_members < len(i.entries) else len(i.entries)

                winner = [self.bot.get_user(j).mention for j in random.sample(i.entries, entries)]
                await msg.reply(", ".join(winner) + f"が**{i.prize}**を獲得しました！")
                Giveaway.delete(i.message_id)


class GiveawayModal(discord.ui.Modal):
    duration = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="期間",
        placeholder="例) 1分 1時間 1日"
    )
    winners = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="獲得者数"
    )
    prize = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="賞品"
    )
    description = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="説明",
        required=False,
        default=None,
    )

    def __init__(self):
        super().__init__(title="Giveawayを作成")

    async def on_submit(self, ctx: Interaction):
        end_at = datetime.datetime.now().replace(microsecond=0)

        minutes_match = re.match(r"([0-9]{1,2})分|([0-9]{1,2})分間", self.duration.value)
        hours_match = re.match(r"([0-9]{1,2})時間", self.duration.value)
        days_match = re.match(r"([0-9]{1,2})日|([0-9]{1,2})日間", self.duration.value)

        if minutes_match:
            minutes = int(minutes_match.group(1))
            end_at += datetime.timedelta(minutes=minutes)
        elif hours_match:
            hours = int(hours_match.group(1))
            end_at += datetime.timedelta(hours=hours)
        elif days_match:
            days = int(days_match.group(1))
            end_at += datetime.timedelta(days=days)

        embed = discord.Embed(
            title=self.prize.value,
            description=self.description,
            timestamp=end_at
        )

        embed.add_field(name="終了",
                        value=f"<t:{int(end_at.timestamp())}:R>(<t:{int(end_at.timestamp())}:f>)")
        embed.add_field(name="開催者", value=ctx.user.mention)
        embed.add_field(name="参加者", value="0")
        embed.add_field(name="獲得者数", value=self.winners.value)

        msg = await ctx.channel.send(embed=embed, view=EntryButton())

        try:
            Giveaway.create(ctx.guild_id, ctx.channel_id, msg.id, ctx.user.id, self.prize.value,
                            int(self.winners.value), end_at)
        except ValueError:
            await ctx.response.send_message(f"獲得者数は整数を入力してください", ephemeral=True)
            return

        await ctx.response.send_message(f"Giveawayを作成しました ID:{msg.id}", ephemeral=True)


class EntryButton(discord.ui.View):

    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="🎉", custom_id="entry_button")
    async def entry(self, ctx: discord.Interaction, button: discord.ui.Button):
        entry = Giveaway.add_entry(ctx.message.id, ctx.user.id)
        if not entry:
            await ctx.response.send_message("すでにエントリー済みです", ephemeral=True)
            return

        embed = ctx.message.embeds[0]
        embed.set_field_at(2, name="参加者", value=str(int(embed.fields[2].value) + 1))

        await ctx.message.edit(embed=embed)
        await ctx.response.send_message("エントリーしました！", ephemeral=True)
