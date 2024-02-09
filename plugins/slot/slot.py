import datetime
from enum import Enum

import discord
from discord import TextChannel, app_commands
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

import config
from plugins.slot.utils.SlotData import SlotData, SlotDataManager, SlotType


class SlotCommand(Enum):
    new = 0
    old = 1


class Slot(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        bot.add_view(SlotButton(self.bot))

        self.task.start()

    @app_commands.command(name="slot")
    async def new(self, ctx: discord.Interaction, arg: SlotCommand):
        if ctx.user.guild_permissions.administrator:
            # embed作成
            embed = discord.Embed(
                title="スロット価格表",
                description="1週間: 100円\n1ヶ月: 200円\n永久: 250円",
                # color=""
            )

            embed.add_field(name="規約",
                            value="@everyone は１日２回まで\n相互の場合、200人以上の参加者必須\n└ @everyone は１日１回まで")

            await ctx.response.send_message(embed=embed, view=SlotButton(self.bot))

        else:
            await ctx.response.send_message("このコマンドを実行する権限がありません",
                                            ephemeral=True)

    @tasks.loop(time=datetime.time(hour=0))
    async def task(self):
        slots = SlotDataManager.getall()
        if not slots:
            return

        today = datetime.date.today()
        for i in slots:
            if not i.expiry:
                return

            if i.expiry <= today:
                await self.bot.get_channel(i.channel_id).delete()
                SlotDataManager.delete(i.channel_id)

            elif i.expiry - today == datetime.timedelta(days=1):
                embed = discord.Embed(
                    title="スロットの使用期限が残り１日となっております\n延長しますか？"
                )
                await self.bot.get_channel(i.channel_id).send(embed=embed, view=ExtendButton(self.bot))


class SlotButton(discord.ui.View):

    def __init__(self, bot: Bot, timeout=None):
        self.bot = bot
        super().__init__(timeout=timeout)

    """ボタンの応答"""

    @discord.ui.button(label="注文", style=discord.ButtonStyle.success,
                       custom_id="slot_order")
    async def request(self, ctx: discord.Interaction, button):
        # select作成
        select = SlotSelect([discord.SelectOption(label=i.value, description="") for i in SlotType],
                            self.bot)

        # viewに追加
        view_select = discord.ui.View()
        view_select.add_item(select)

        embed = discord.Embed(
            title="注文内容を選択してください"
        )

        # 選択メッセージを送信
        await ctx.response.send_message(embed=embed, view=view_select, ephemeral=True)


class SlotSelect(discord.ui.Select):

    def __init__(self, req: list[discord.SelectOption], bot):
        self.bot = bot
        super().__init__(placeholder="注文内容", options=req)

    async def callback(self, ctx: discord.Interaction):
        plan = SlotType(self.values[0])

        if plan == SlotType.MUTUAL:
            cat: discord.CategoryChannel = self.bot.get_channel(config.SLOT_MUTUAL_CATEGORY_ID)
            channel_name = config.SLOT_MUTUAL_CHANNEL_NAME.replace("{username}", ctx.user.name)

            overwrites = {
                cat.guild.get_role(config.ADMIN_ROLE_ID):
                    discord.PermissionOverwrite(read_messages=True, send_messages=True),
                ctx.user:
                    discord.PermissionOverwrite(read_messages=True, send_messages=True),
                cat.guild.default_role:
                    discord.PermissionOverwrite(read_messages=False, send_messages=False),
            }

            ch = await cat.create_text_channel(name=channel_name, overwrites=overwrites)
            await ctx.response.send_message("チケットチャンネルを作成しました: " + ch.mention, ephemeral=True)

        else:
            if config.MODAL_MODE:
                await ctx.response.send_modal(SlotModal(plan, self.bot))
                return

            else:
                category: discord.CategoryChannel = self.bot.get_channel(config.SLOT_CATEGORY_ID)
                overwrites = {
                    category.guild.get_role(config.ADMIN_ROLE_ID):
                        discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    ctx.user:
                        discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    category.guild.default_role:
                        discord.PermissionOverwrite(read_messages=True, send_messages=False),
                }

                today = datetime.date.today()
                channel_name = config.SLOT_CHANNEL_NAME.replace("{username}", ctx.user.name)
                text = ctx.user.mention + "\n期限は"
                if plan == SlotType.PERMANENT:
                    channel_name = channel_name.replace("{expiry}", "")
                    expire_at = None
                    text += "永久です"
                else:
                    if plan == SlotType.WEEKLY:
                        expire_at = today + datetime.timedelta(weeks=1)
                        text += "7日後です"

                    elif plan == SlotType.MONTHLY:
                        expire_at = today + datetime.timedelta(days=30)
                        text += "30日後です"
                    else:
                        return

                    channel_name = channel_name.replace("{expiry}",
                                                        f"-{expire_at.month}月{expire_at.day}日")

                # ログ送信
                c = self.bot.get_channel(config.LOG_CHANNEL_ID)
                embed = discord.Embed(
                    title=f"スロット",
                )
                embed.add_field(name="申込者", value=ctx.user.mention, inline=False)
                embed.add_field(name="プラン", value=plan.value, inline=False)
                if expire_at:
                    embed.add_field(name="期限",
                                    value=f"<t:{int(datetime.datetime.combine(expire_at, datetime.time(0, 0, 0)).timestamp())}:D>",
                                    inline=False)
                else:
                    embed.add_field(name="期限", value=f"なし", inline=False)
                await c.send(embed=embed)

                slot = await category.create_text_channel(name=channel_name, overwrites=overwrites)

                sd = SlotData(ctx.user.id, expire_at, slot.id)
                SlotDataManager.create(sd)

                await ctx.response.send_message(
                    f"スロットチャンネルを作成しました: <#{slot.id}>", ephemeral=True)

                embed = discord.Embed(
                    title="作成完了",
                    description=text
                )
                await slot.send(embed=embed)


class SlotModal(discord.ui.Modal):
    invite = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="サーバー招待リンク",
        custom_id="invite_link",
    )

    paypay = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="PayPayリンク",
        custom_id="paypay_link",
        placeholder="https://pay.paypay.ne.jp/xxxxxxxxxx"
    )

    def __init__(self, plan: SlotType, bot):
        self.plan = plan
        self.bot = bot
        super().__init__(title="フォーム名", custom_id="slot_form")

    async def on_submit(self, ctx: discord.Interaction):

        category: discord.CategoryChannel = self.bot.get_channel(config.SLOT_CATEGORY_ID)
        overwrites = {
            category.guild.get_role(config.ADMIN_ROLE_ID):
                discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.user:
                discord.PermissionOverwrite(read_messages=True, send_messages=True),
            category.guild.default_role:
                discord.PermissionOverwrite(read_messages=True, send_messages=False),
        }

        today = datetime.date.today()
        channel_name = config.SLOT_CHANNEL_NAME.replace("{username}", ctx.user.name)
        text = ctx.user.mention + "\n期限は"
        if self.plan == SlotType.PERMANENT:
            channel_name = channel_name.replace("{expiry}", "")
            expire_at = None
            text += "永久です"
        else:
            if self.plan == SlotType.WEEKLY:
                expire_at = today + datetime.timedelta(weeks=1)
                text += "7日後です"

            elif self.plan == SlotType.MONTHLY:
                expire_at = today + datetime.timedelta(days=30)
                text += "30日後です"
            else:
                return

            channel_name = channel_name.replace("{expiry}",
                                                f"-{expire_at.month}月{expire_at.day}日")

        # ログ送信
        c = self.bot.get_channel(config.LOG_CHANNEL_ID)
        embed = discord.Embed(
            title=f"スロット",
        )
        embed.add_field(name="申込者", value=ctx.user.mention, inline=False)
        embed.add_field(name="PayPayリンク", value=self.paypay, inline=False)
        embed.add_field(name="サーバー招待リンク", value=self.invite, inline=False)
        embed.add_field(name="プラン", value=self.plan.value, inline=False)
        if expire_at:
            embed.add_field(name="期限", value=f"<t:{int(datetime.datetime.combine(expire_at, datetime.time(0,0,0)).timestamp())}:D>", inline=False)
        else:
            embed.add_field(name="期限", value=f"なし", inline=False)
        await c.send(embed=embed)

        slot = await category.create_text_channel(name=channel_name, overwrites=overwrites)

        sd = SlotData(ctx.user.id, expire_at, slot.id)
        SlotDataManager.create(sd)

        await ctx.response.send_message(
            f"スロットチャンネルを作成しました: <#{slot.id}>", ephemeral=True)

        embed = discord.Embed(
            title="作成完了",
            description=text
        )
        await slot.send(embed=embed)


class ExtendButton(discord.ui.View):

    def __init__(self, bot: Bot, timeout=None):
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="延期", style=discord.ButtonStyle.success,
                       custom_id="slot_extend")
    async def extend(self, ctx: discord.Interaction, button):
        slot = SlotDataManager.get(ctx.channel_id)
        if slot.user_id != ctx.user.id:
            await ctx.response.send_message("実行できません", ephemeral=True)
            return

        # select作成
        select = ExtendSelect([
            discord.SelectOption(label=SlotType.WEEKLY.value, description=""),
            discord.SelectOption(label=SlotType.MONTHLY.value, description=""),
            discord.SelectOption(label=SlotType.PERMANENT.value, description=""),
        ], self.bot, slot)

        # viewに追加
        view_select = discord.ui.View()
        view_select.add_item(select)

        embed = discord.Embed(
            title="注文内容を選択してください"
        )

        # 選択メッセージを送信
        await ctx.response.send_message(embed=embed, view=view_select, ephemeral=True)


class ExtendSelect(discord.ui.Select):

    def __init__(self, req: list[discord.SelectOption], bot, slot):
        self.bot = bot
        self.slot = slot
        super().__init__(placeholder="注文内容", options=req)

    """セレクトメニューの応答"""

    async def callback(self, ctx: discord.Interaction):
        plan = SlotType(self.values[0])

        if plan == SlotType.MUTUAL:
            pass
        else:

            if config.MODAL_MODE:
                await ctx.response.send_modal(ExtendModal(plan, self.bot, self.slot))
            else:
                expiry = self.slot.expiry
                channel_name = config.SLOT_CHANNEL_NAME.replace("{username}", ctx.user.name)
                text = ctx.user.mention + "\n期限は"
                if plan == SlotType.PERMANENT:
                    channel_name = channel_name.replace("{expiry}", "")
                    expire_at = None
                    text += "永久です"
                else:
                    if plan == SlotType.WEEKLY:
                        expire_at = expiry + datetime.timedelta(weeks=1)
                        text += "7日後です"

                    elif plan == SlotType.MONTHLY:
                        expire_at = expiry + datetime.timedelta(days=30)
                        text += "30日後です"

                    channel_name = channel_name.replace("{expiry}",
                                                        f"-{expire_at.month}月{expire_at.day}日")

                slot_ch: TextChannel = self.bot.get_channel(self.slot.channel_id)
                await slot_ch.edit(name=channel_name)

                SlotDataManager.extend(self.slot.channel_id, expire_at)
                await ctx.response.send_message(
                    f"更新が完了しました！", ephemeral=True)

                embed = discord.Embed(
                    title="更新完了",
                    description=text
                )
                await slot_ch.send(embed=embed)


class ExtendModal(discord.ui.Modal):
    invite = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="サーバー招待リンク",
        custom_id="invite_link",
    )

    paypay = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="PayPayリンク",
        custom_id="paypay_link",
        placeholder="https://pay.paypay.ne.jp/xxxxxxxxxx"
    )

    def __init__(self, plan, bot, slot: SlotData):
        self.plan = plan
        self.bot = bot
        self.slot = slot
        super().__init__(title="フォーム名", custom_id="slot_form")

    async def on_submit(self, ctx: discord.Interaction):

        expiry = self.slot.expiry
        channel_name = config.SLOT_CHANNEL_NAME.replace("{username}", ctx.user.name)
        text = ctx.user.mention + "\n期限は"
        if self.plan == SlotType.PERMANENT:
            channel_name = channel_name.replace("{expiry}", "")
            expire_at = None
            text += "永久です"
        else:
            if self.plan == SlotType.WEEKLY:
                expire_at = expiry + datetime.timedelta(weeks=1)
                text += "7日後です"

            elif self.plan == SlotType.MONTHLY:
                expire_at = expiry + datetime.timedelta(days=30)
                text += "30日後です"

            channel_name = channel_name.replace("{expiry}",
                                                f"-{expire_at.month}月{expire_at.day}日")

        slot_ch: TextChannel = self.bot.get_channel(self.slot.channel_id)
        await slot_ch.edit(name=channel_name)

        SlotDataManager.extend(self.slot.channel_id, expire_at)
        await ctx.response.send_message(
            f"更新が完了しました！", ephemeral=True)

        embed = discord.Embed(
            title="更新完了",
            description=text
        )
        await slot_ch.send(embed=embed)
