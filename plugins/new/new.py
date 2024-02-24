import asyncio
import re
import traceback
from typing import Union

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import config
from utils import GuildSettings
from .utils import RequestButton, RequestTicket, RequestTicketStatus


class New(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        # 依頼ボタンのview
        request_button = RequestButton.get_all()
        if request_button:
            for i in request_button:
                self.bot.add_view(
                    RequestButtonView(
                        [discord.SelectOption(label=i, description="") for i in i.request],
                        self.bot,
                        self.bot.get_channel(i.category_id),
                        self.bot.get_guild(i.guild_id).get_role(i.role_id) if i.role_id else None,
                        i.first_message
                    ),
                    message_id=i.message_id
                )

        # 終了ボタンのview
        complete_button = RequestTicket.get_all()
        if complete_button:
            for i in complete_button:
                self.bot.add_view(
                    CompleteButton(self.bot.get_user(i.user_id), bot),
                    message_id=i.complete_button
                )

    @app_commands.command(name="new", description="チケットを作成する依頼ボタンを作成します")
    @app_commands.describe(title="パネルのタイトル",
                           description="パネルの説明",
                           menu_list="依頼セレクトパネルに表示するメニュー(例: 項目1,項目2,項目3)",
                           image="パネルに乗せる画像のURL",
                           category="チケットを作成するカテゴリ",
                           role="チケット作成時にメンションするロール",
                           first_message="チケット作成時に最初に送るメッセージ",
                           )
    @app_commands.default_permissions(administrator=True)
    async def new(self,
                  ctx: discord.Interaction,
                  title: str,
                  description: str,
                  menu_list: str,
                  category: discord.CategoryChannel,
                  role: discord.Role = None,
                  image: str = None,
                  first_message: str = None
                  ):
        if ctx.user.guild_permissions.administrator:
            """
            setting = GuildSettings.get(ctx.guild_id)
            if not setting.request_ticket_category:
                await ctx.response.send_message(
                    "チケットのカテゴリーが設定されていません。/channelset で設定してください。",
                    ephemeral=True)
                return
            """

            # embed作成
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.random(),
            )

            if image:
                embed.set_image(url=image)

            # リストを読み込み
            menu_split = re.split(", |,", menu_list)

            # リストからSelectOptionを生成
            menu = [discord.SelectOption(label=i, description="") for i in menu_split]

            # チャンネルにembed送信
            button = RequestButtonView(menu, self.bot, category, role, first_message)

            # 依頼ボタンを送信
            m = await ctx.channel.send(embed=embed, view=button)
            await ctx.response.send_message("依頼選択リストを送信しました", ephemeral=True)

            # 依頼ボタンの情報を保存
            role_id = None
            if role:
                role_id = role.id
            RequestButton.create(title, description, ctx.guild_id, ctx.channel_id, m.id, menu_split, category.id, role_id, first_message)
            print(f"依頼選択リストを送信しました: {m.id}")

        else:
            await ctx.response.send_message("このコマンドを実行する権限がありません",
                                            ephemeral=True)
            print("/newが実行されましたが権限がないため実行されませんでした")

    @app_commands.command(name="setrole", description="ロールの設定をします")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="ClientRole", value="ClientRole"),
            app_commands.Choice(name="BuyerRole", value="BuyerRole"),
            app_commands.Choice(name="AdminRole", value="AdminRole"),
            app_commands.Choice(name="VerifyRole", value="VerifyRole"),
            app_commands.Choice(name="HandleRole", value="HandleRole"),
        ]
    )
    @app_commands.rename(mode="タイプ", role="ロール")
    @app_commands.describe(
        role="ロールを指定します。指定しない場合はそのロールの付与や権限などが無効になります")
    @app_commands.default_permissions(administrator=True)
    async def roleset(self, ctx: discord.Interaction, mode: str,
                      role: Union[discord.Role, None] = None):

        # モード
        if mode == "ClientRole":
            if role:
                GuildSettings.set_client(ctx.guild_id, role.id)

            else:
                GuildSettings.set_client(ctx.guild_id, None)

        elif mode == "BuyerRole":
            if role:
                GuildSettings.set_buyer(ctx.guild_id, role.id)
            else:
                GuildSettings.set_buyer(ctx.guild_id, None)

        elif mode == "AdminRole":
            if role:
                GuildSettings.set_admin(ctx.guild_id, role.id)
            else:
                GuildSettings.set_admin(ctx.guild_id, None)

        elif mode == "VerifyRole":
            if role:
                GuildSettings.set_verify(ctx.guild_id, role.id)
            else:
                GuildSettings.set_verify(ctx.guild_id, None)

        elif mode == "HandleRole":
            if role:
                GuildSettings.set_handle(ctx.guild_id, role.id)
            else:
                GuildSettings.set_handle(ctx.guild_id, None)
            await ctx.response.send_message("ロールの設定を更新しました", ephemeral=True)
            return

        else:
            await ctx.response.send_message("タイプが不明です", ephemeral=True)
            return

        if role:
            if ctx.guild.self_role.position < role.position:
                await ctx.response.send_message(
                    "ロールの設定を更新しました\nロールの順序を入れ替えてください",
                    file=discord.File("RolePriority.gif"), ephemeral=True)
                return

        await ctx.response.send_message("ロールの設定を更新しました", ephemeral=True)

    @app_commands.command(name="channelset", description="チャンネルやカテゴリーの設定をします")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="LogChannel", value="LogChannel"),
            # app_commands.Choice(name="RequestTicketCategory", value="RequestTicketCategory"),
            app_commands.Choice(name="SlotCategory", value="SlotCategory"),
            # app_commands.Choice(name="TicketCategory", value="TicketCategory"),
        ]
    )
    @app_commands.rename(mode="タイプ", channel="チャンネル")
    @app_commands.describe(
        channel="チャンネルまたはカテゴリーを指定します。カテゴリーが表示されない場合は指定したいカテゴリー名を入力してみてください。")
    @app_commands.default_permissions(administrator=True)
    async def channelset(self, ctx: discord.Interaction, mode: str,
                         channel: Union[discord.CategoryChannel, discord.TextChannel]):
        if mode == "LogChannel":
            if not isinstance(channel, discord.TextChannel):
                await ctx.response.send_message(
                    "チャンネル引数にはテキストチャンネルを指定してください",
                    ephemeral=True)
                return
            GuildSettings.set_log_channel(ctx.guild_id, channel.id)
            await ctx.response.send_message("チャンネルの設定を更新しました", ephemeral=True)

        elif mode == "RequestTicketCategory":
            if not isinstance(channel, discord.CategoryChannel):
                await ctx.response.send_message("チャンネル引数にはカテゴリーを指定してください",
                                                ephemeral=True)
                return
            GuildSettings.set_request_category(ctx.guild_id, channel.id)
            await ctx.response.send_message("カテゴリーの設定を更新しました", ephemeral=True)

        elif mode == "SlotCategory":
            if not isinstance(channel, discord.CategoryChannel):
                await ctx.response.send_message("チャンネル引数にはカテゴリーを指定してください",
                                                ephemeral=True)
                return
            GuildSettings.set_slot_category(ctx.guild_id, channel.id)
            await ctx.response.send_message("カテゴリーの設定を更新しました", ephemeral=True)

        elif mode == "TicketCategory":
            if not isinstance(channel, discord.CategoryChannel):
                await ctx.response.send_message("チャンネル引数にはカテゴリーを指定してください",
                                                ephemeral=True)
                return
            GuildSettings.set_ticket_category(ctx.guild_id, channel.id)
            await ctx.response.send_message("カテゴリーの設定を更新しました", ephemeral=True)

        else:
            await ctx.response.send_message("タイプが不明です", ephemeral=True)
            return

    @Cog.listener()
    async def on_message(self, msg: discord.Message):

        # メッセージが送られたチャンネルのカテゴリーを取得
        try:
            cat_id = msg.channel.category_id
        except AttributeError:
            return

        # カテゴリーに所属していない場合
        if not cat_id:
            return

        ticket = RequestTicket.get(msg.channel.id)
        if not ticket:
            return

        # 管理者かつbotでなかったら
        if msg.author.guild_permissions.administrator:
            if msg.author.bot:
                return

            # チケット情報を取得
            d = RequestTicket.get(msg.channel.id)

            # ログがWAITINGでなかったら
            if d.status != RequestTicketStatus.WAITING:
                return

            # ギルド設定を取得
            setting = GuildSettings.get(msg.guild.id)
            if not setting.log_channel:
                return

            # ログメッセージを取得
            log = await self.bot.get_channel(setting.log_channel).fetch_message(
                d.log_message_id)

            # embedを更新
            embed = log.embeds[0]
            embed.colour = discord.Color.blue()
            embed.description = "依頼対応中"

            await log.edit(embed=embed)

            # チケットのステータスを更新
            RequestTicket.update(msg.channel.id, RequestTicketStatus.SERVING)

            print(f"依頼状況を対応中に更新しました: {d.channel_id}")


class RequestButtonView(discord.ui.View):

    def __init__(self,
                 req: list[discord.SelectOption],
                 bot: Bot,
                 category: discord.CategoryChannel,
                 role: Union[discord.Role, None],
                 first_message: str,
                 timeout=None):
        self.req = req
        self.bot = bot
        self.category = category
        self.role = role
        self.first_message = first_message
        super().__init__(timeout=timeout)

    @discord.ui.button(label="依頼する", style=discord.ButtonStyle.success, emoji="🎫",
                       custom_id="request_view")
    async def request(self, ctx: discord.Interaction, button):
        # embed作成
        embed = discord.Embed(
            title="依頼",
            description="依頼したいメニューを選択してください"
        )

        # select作成
        select = RequestSelect(self.req, self.bot, self.category, self.role, self.first_message)

        # viewに追加
        view_select = discord.ui.View()
        view_select.add_item(select)

        # 選択メッセージを送信
        await ctx.response.send_message(embed=embed, view=view_select, ephemeral=True)


class RequestSelect(discord.ui.Select):

    def __init__(self,
                 req: list[discord.SelectOption],
                 bot: Bot,
                 category: discord.CategoryChannel,
                 role: Union[discord.Role, None],
                 first_message: str):
        self.bot = bot
        self.category = category
        self.role = role
        self.first_message = first_message
        super().__init__(placeholder="選択", options=req)

    async def callback(self, ctx: discord.Interaction):
        if config.MODAL_MODE:
            await ctx.response.send_modal(RequestModal(request=self.values[0], bot=self.bot))
            return

        setting = GuildSettings.get(ctx.guild_id)

        # category = self.bot.get_channel(setting.request_ticket_category)
        ticket = await RequestTicket.create_ticket_channel(ctx.user, self.category, setting)

        # ログ送信
        log_id = None
        if setting.log_channel:
            c = self.bot.get_channel(setting.log_channel)
            embed = discord.Embed(
                title=f"依頼: {self.values[0]}",
                description="依頼対応待ち",
                color=discord.Color.red(),
            )
            embed.add_field(name="申込者", value=ctx.user.mention, inline=False)
            embed.add_field(name="チャンネル", value=ticket.mention, inline=False)
            log = await c.send(embed=embed)
            log_id = log.id

        # 終了ボタン
        complete_button = CompleteButton(ctx.user, self.bot)

        content = ""
        if self.role:
            content = f"{self.role.mention}\n"
        if self.first_message:
            content += f"{self.first_message}\n"
        content += f"依頼内容: {self.values[0]}"
        btn = await ticket.send(content, view=complete_button)

        # セッション作成
        RequestTicket.add(ctx.guild_id, ticket.id, ctx.user.id, log_id, self.values[0], btn.id)

        await ctx.response.send_message(
            f"チケットチャンネルを作成しました: <#{ticket.id}>", ephemeral=True)

        if setting.client_role:
            await ctx.user.add_roles(ctx.guild.get_role(setting.client_role))

        print(f"チケットチャンネルを作成しました: {ticket.id} by{ctx.user}")


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

        setting = GuildSettings.get(ctx.guild_id)

        category = self.bot.get_channel(setting.request_ticket_category)
        ticket = await RequestTicket.create_ticket_channel(ctx.user, category, setting)

        # ログ送信
        log_id = None
        if setting.log_channel:
            c = self.bot.get_channel(setting.log_channel)
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

            log_id = log.id

        # 終了ボタン
        complete_button = CompleteButton(ctx.user, self.bot)
        btn = await ticket.send(view=complete_button)

        # セッション作成
        RequestTicket.add(ctx.guild_id, ticket.id, ctx.user.id, log_id, self.request, btn.id)

        await ctx.response.send_message(
            f"チケットチャンネルを作成しました: <#{ticket.id}>", ephemeral=True)
        try:
            if setting.client_role:
                await ctx.user.add_roles(ctx.guild.get_role(setting.client_role))
        except Exception:
            pass

        print(f"チケットチャンネルを作成しました: {ticket.id} by{ctx.user}")


class CompleteButton(discord.ui.View):

    def __init__(self, user: Union[discord.Member, discord.User], bot: Bot, timeout=None):
        self.user = user
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red, custom_id="stop_request_ticket")
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

        setting = GuildSettings.get(ctx.guild_id)

        if setting.log_channel:
            d = RequestTicket.get(ctx.channel.id)
            log = await self.bot.get_channel(setting.log_channel).fetch_message(d.log_message_id)

            embed = log.embeds[0]
            embed.colour = discord.Color.green()
            embed.description = "依頼完了"

            await log.edit(embed=embed)
            RequestTicket.update(ctx.channel_id, RequestTicketStatus.COMPLETED)

        print(f"依頼が完了しました: {ctx.channel_id}")

        # ロール付与
        if isinstance(self.user, discord.User):
            self.user = ctx.guild.get_member(self.user.id)

        try:
            if setting.buyer_role:
                await self.user.add_roles(ctx.guild.get_role(setting.buyer_role))
            if setting.client_role:
                await self.user.remove_roles(ctx.guild.get_role(setting.client_role))

        except Exception:
            traceback.print_exc()

        # 10秒後に削除
        await asyncio.sleep(10)
        await ctx.channel.delete()
