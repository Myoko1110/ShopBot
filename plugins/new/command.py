import asyncio
import re
from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import config
from .utils.complete_button import Complete, CompleteManager
from .utils.request import Request, RequestManager
from .utils.ticket import Ticket, TicketManager, TicketStatus


class New(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        reqs = RequestManager.get_requests()
        if reqs:
            for i in reqs:
                self.bot.add_view(
                    RequestButton(
                        [discord.SelectOption(label=i, description="") for i in i.requests], bot),
                    message_id=i.id
                )

        btns = CompleteManager.get_buttons()
        if btns:
            for i in btns:
                self.bot.add_view(
                    CompleteButton(self.bot.get_user(i.user_id), bot),
                    message_id=i.message_id
                )

    @app_commands.command(name="new")
    async def new(self, ctx: discord.Interaction, title: str, message: str, menu_list: str):
        if ctx.user.guild_permissions.administrator:
            # embed作成
            embed = discord.Embed(
                title=title,
                description=message,
                # color=""
            )

            # リストを読み込み
            menu_split = re.split(", |,", menu_list)
            menu = [discord.SelectOption(label=i, description="") for i in menu_split]

            # チャンネルにembed送信
            button = RequestButton(menu, self.bot)

            m = await ctx.channel.send(embed=embed, view=button)
            await ctx.response.send_message("依頼選択リストを送信しました", ephemeral=True)

            req = Request(m.id, title, message, menu_split)
            RequestManager.create_request(req)

        else:
            await ctx.response.send_message("このコマンドを実行する権限がありません",
                                            ephemeral=True)

    @Cog.listener()
    async def on_message(self, msg: discord.Message):
        try:
            cat_id = msg.channel.category_id
        except AttributeError:
            return

        if not cat_id:
            return

        if cat_id == config.TICKET_CATEGORY_ID:
            if msg.author.guild_permissions.administrator:
                if msg.author.bot:
                    return

                d = TicketManager.get_ticket(msg.channel.id)

                ticket = Ticket(d["id"], d["request"], self.bot.get_user(d["user_id"]),
                                TicketStatus(d["status"]),
                                await self.bot.get_channel(config.LOG_CHANNEL_ID).fetch_message(
                                    d["log"]))

                if ticket.status == TicketStatus.SERVING or ticket.status == TicketStatus.COMPLETED:
                    return

                embed = ticket.log.embeds[0]
                embed.colour = discord.Color.blue()
                embed.description = "依頼対応中"

                await ticket.log.edit(embed=embed)


class RequestButton(discord.ui.View):

    def __init__(self, req: list[discord.SelectOption], bot: Bot, timeout=None):
        self.req = req
        self.bot = bot
        super().__init__(timeout=timeout)

    """ボタンの応答"""

    @discord.ui.button(label="依頼する", style=discord.ButtonStyle.success, emoji="🎫",
                       custom_id="request_view")
    async def request(self, ctx: discord.Interaction, button):
        # embed作成
        embed = discord.Embed(
            title="依頼",
            description="依頼したいメニューを選択してください"
        )

        # select作成
        select = RequestSelect(req=self.req, bot=self.bot)

        # viewに追加
        view_select = discord.ui.View()
        view_select.add_item(select)

        # 選択メッセージを送信
        await ctx.response.send_message(embed=embed, view=view_select, ephemeral=True)


class RequestSelect(discord.ui.Select):

    def __init__(self, req: list[discord.SelectOption], bot: Bot):
        self.bot = bot
        super().__init__(placeholder="選択", options=req)

    async def callback(self, ctx: discord.Interaction):
        if config.MODAL_MODE:
            await ctx.response.send_modal(RequestModal(request=self.values[0], bot=self.bot))
            return


        category = self.bot.get_channel(config.TICKET_CATEGORY_ID)
        ticket = await TicketManager.create_ticket_channel(ctx.user, category)

        # ログ送信
        c = self.bot.get_channel(config.LOG_CHANNEL_ID)
        embed = discord.Embed(
            title=f"依頼: {self.values[0]}",
            description="依頼対応待ち",
            color=discord.Color.red(),
        )
        embed.add_field(name="申込者", value=ctx.user.mention, inline=False)
        embed.add_field(name="チャンネル", value=ticket.mention, inline=False)
        log = await c.send(embed=embed)

        # セッション作成
        TicketManager.create_ticket(ticket.id, ctx.user, self.values[0], log)

        # 終了ボタン
        complete_button = CompleteButton(ctx.user, self.bot)
        btn = await ticket.send(view=complete_button)

        cp = Complete(ticket.id, btn.id, ctx.user.id)
        CompleteManager.create_button(cp)

        await ctx.response.send_message(
            f"チケットチャンネルを作成しました: <#{ticket.id}>", ephemeral=True)
        await ctx.user.add_roles(ctx.guild.get_role(config.TICKET_REQUESTING_ROLE))


class RequestModal(discord.ui.Modal):
    email = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="メールアドレス",
        custom_id="e-mail",
    )

    password = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="パスワード",
        custom_id="password",
    )

    paypay = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="PayPayリンク",
        custom_id="paypay_link",
        placeholder="https://pay.paypay.ne.jp/xxxxxxxxxx"
    )

    def __init__(self, request, bot: Bot):
        self.request = request
        self.bot = bot
        super().__init__(title="フォーム名", custom_id="request_form")

    async def on_submit(self, ctx: discord.Interaction):
        # email -> self.email
        # password -> self.password
        # paypay -> self.paypay

        category = self.bot.get_channel(config.TICKET_CATEGORY_ID)
        ticket = await TicketManager.create_ticket_channel(ctx.user, category)

        # ログ送信
        c = self.bot.get_channel(config.LOG_CHANNEL_ID)
        embed = discord.Embed(
            title=f"依頼: {self.request}",
            description="依頼対応待ち",
            color=discord.Color.red(),
        )
        embed.add_field(name="申込者", value=ctx.user.mention, inline=False)
        embed.add_field(name="メールアドレス", value=self.email, inline=False)
        embed.add_field(name="パスワード", value=self.password, inline=False)
        embed.add_field(name="PayPayリンク", value=self.paypay, inline=False)
        embed.add_field(name="チャンネル", value=ticket.mention, inline=False)
        log = await c.send(embed=embed)

        # セッション作成
        TicketManager.create_ticket(ticket.id, ctx.user, self.request, log)

        # 終了ボタン
        complete_button = CompleteButton(ctx.user, self.bot)
        btn = await ticket.send(view=complete_button)

        cp = Complete(ticket.id, btn.id, ctx.user.id)
        CompleteManager.create_button(cp)

        await ctx.response.send_message(
            f"チケットチャンネルを作成しました: <#{ticket.id}>", ephemeral=True)
        try:
            await ctx.user.add_roles(ctx.guild.get_role(config.TICKET_REQUESTING_ROLE))
        except Exception:
            pass


class CompleteButton(discord.ui.View):

    def __init__(self, user: Union[discord.Member, discord.User], bot: Bot, timeout=None):
        self.user = user
        self.bot = bot
        super().__init__(timeout=timeout)

    """ボタンの応答"""

    @discord.ui.button(label="終了", style=discord.ButtonStyle.primary, emoji="🎫",
                       custom_id="stop_ticket")
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="本当にこの依頼を終了しますか？",
            description="終了する場合は下の終了ボタンを押してください"
        )

        await ctx.response.send_message(embed=embed,
                                        view=ConfirmButton(self.user, ctx.message, self.bot),
                                        ephemeral=True)


class ConfirmButton(discord.ui.View):
    def __init__(self, user: Union[discord.Member, discord.User], message: discord.Message,
                 bot: Bot):
        self.user = user
        self.message = message
        self.bot = bot
        super().__init__()

    """ボタンの応答"""

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red, emoji="🎫")
    async def complete(self, ctx: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="ご利用ありがとうございました",
            description="このチャンネルは10秒後に削除されます"
        )

        # メッセージ削除
        await self.message.delete()

        # embed送信
        await ctx.response.send_message(embed=embed)

        d = TicketManager.get_ticket(ctx.channel.id)
        ticket = Ticket(d["id"], d["request"], self.bot.get_user(d["user_id"]),
                        TicketStatus(d["status"]),
                        await self.bot.get_channel(config.LOG_CHANNEL_ID).fetch_message(d["log"]))

        if ticket.status == TicketStatus.SERVING or ticket.status == TicketStatus.COMPLETED:
            return

        embed = ticket.log.embeds[0]
        embed.colour = discord.Color.green()
        embed.description = "依頼完了"

        await ticket.log.edit(embed=embed)

        # ロール付与
        if isinstance(self.user, discord.User):
            self.user = ctx.guild.get_member(self.user.id)

        try:
            await self.user.add_roles(ctx.guild.get_role(config.TICKET_COMPLETED_ROLE_ID))
            await self.user.remove_roles(ctx.guild.get_role(config.TICKET_REQUESTING_ROLE))
        except Exception:
            pass

        # 10秒後に削除
        await asyncio.sleep(10)
        await ctx.channel.delete()
