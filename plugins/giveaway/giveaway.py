import datetime
import random
import re

import discord
from discord import Interaction, app_commands
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

from plugins.giveaway.utils.GiveawayData import GiveawayDataManager


class Giveaway(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        bot.add_view(EntryButton())
        self.giveaway_end.start()

    @app_commands.command(name="gcreate")
    async def gcreate(self, ctx: discord.Interaction):
        await ctx.response.send_modal(GiveawayModal())

    @app_commands.command(name="gend")
    async def gend(self, ctx: discord.Interaction, id: str):
        try:
            i = GiveawayDataManager.get(int(id))
        except ValueError:
            ctx.response.send_message("Giveawayが見つかりませんでした")
            return

        if i == False:
            ctx.response.send_message("Giveawayが見つかりませんでした")
            return

        msg = await self.bot.get_channel(i.channel_id).fetch_message(i.message_id)
        await msg.edit(view=None)

        if not i.entries:
            await msg.reply("エントリーがなかったため当選者はいませんでした")
            GiveawayDataManager.delete(i.message_id)
            return

        entries = i.winners if i.winners < len(i.entries) else len(i.entries)

        winner = [self.bot.get_user(j).mention for j in random.sample(i.entries, entries)]
        await msg.reply(", ".join(winner) + f"が**{i.prize}**を獲得しました！")
        GiveawayDataManager.delete(i.message_id)

        await ctx.response.send_message("")

    @app_commands.command(name="gdelete")
    async def gdelete(self, ctx: discord.Interaction, id: str):
        try:
            i = GiveawayDataManager.get(int(id))
        except ValueError:
            ctx.response.send_message("Giveawayが見つかりませんでした")
            return

        if i == False:
            ctx.response.send_message("Giveawayが見つかりませんでした")

        msg = await self.bot.get_channel(i.channel_id).fetch_message(i.message_id)
        await msg.edit(view=None)

        GiveawayDataManager.delete(i.message_id)
        await ctx.response.send_message("Giveawayを削除しました")

    @tasks.loop(seconds=10)
    async def giveaway_end(self):
        giveaway = GiveawayDataManager.getall()
        if not giveaway:
            return

        now = datetime.datetime.now()
        for i in giveaway:
            if now > i.end_at:

                msg = await self.bot.get_channel(i.channel_id).fetch_message(i.message_id)
                await msg.edit(view=None)

                if not i.entries:
                    await msg.reply("エントリーがなかったため当選者はいませんでした")
                    GiveawayDataManager.delete(i.message_id)
                    return

                entries = i.winners if i.winners < len(i.entries) else len(i.entries)

                winner = [self.bot.get_user(j).mention for j in random.sample(i.entries, entries)]
                await msg.reply(", ".join(winner) + f"が**{i.prize}**を獲得しました！")
                GiveawayDataManager.delete(i.message_id)


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
        default=None
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

        GiveawayDataManager.create(msg.id, end_at, ctx.channel_id, int(self.winners.value), self.prize.value)

        await ctx.response.send_message(f"Giveawayを作成しました ID:{msg.id}", ephemeral=True)


class EntryButton(discord.ui.View):

    def __init__(self, timeout=None):
        super().__init__(timeout=timeout)

    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="🎉", custom_id="entry_button")
    async def entry(self, ctx: discord.Interaction, button: discord.ui.Button):
        entry = GiveawayDataManager.add_entries(ctx.message.id, ctx.user.id)
        if entry == False:
            await ctx.response.send_message("すでにエントリー済みです", ephemeral=True)
            return

        embed = ctx.message.embeds[0]
        embed.set_field_at(2, name="参加者", value=str(int(embed.fields[2].value) + 1))

        await ctx.message.edit(embed=embed)
        await ctx.response.send_message("エントリーしました！", ephemeral=True)
