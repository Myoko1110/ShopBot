import datetime

import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import Bot, Cog

import config
from plugins.slot.utils import Slot
from utils import GuildSettings


class SlotCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.task.start()

    @app_commands.command(name="makeslot", description="スロットを作成します")
    @app_commands.describe(user="ユーザー", expiry_date="有効期限(日)")
    @app_commands.default_permissions(administrator=True)
    async def make(self, ctx: discord.Interaction, user: discord.User, expiry_date: int = None):
        if ctx.user.guild_permissions.administrator:

            # ギルド設定を取得
            setting = GuildSettings.get(ctx.guild_id)

            # スロットカテゴリーがなければエラーを返す
            if not setting or not setting.slot_category:
                await ctx.response.send_message("スロットチャンネルを作成するカテゴリーが設定されていません。/channelsetでSlotCategoryを設定してください", ephemeral=True)
                return

            # チャンネル名の{username}をユーザー名に
            channel_name = config.SLOT_CHANNEL_NAME.replace("{username}", user.name)

            # 期限があれば
            if expiry_date:

                # 期限を計算
                expire = datetime.date.today() + datetime.timedelta(days=expiry_date)

                # メッセージとチャンネル名を作成
                text = f"{user.mention}\n期限は{expiry_date}日後です"
                channel_name = channel_name.replace("{expiry}", f"-{expire.month}月{expire.day}日")

            else:

                # 期限をNoneに
                expire = None

                # メッセージとチャンネル名を作成
                text = f"{ctx.user.mention}\n期限は永久です"
                channel_name = channel_name.replace("{expiry}", "-永久")

            # logチャンネルが設定されていればログを送信
            if setting and setting.log_channel:
                log_channel = self.bot.get_channel(setting.log_channel)
                embed = discord.Embed(
                    title=f"スロット",
                )
                embed.add_field(name="申込者", value=ctx.user.mention, inline=False)
                if expire:
                    embed.add_field(name="期限",
                                    value=f"<t:{int(datetime.datetime.combine(expire, datetime.time(0, 0, 0)).timestamp())}:D>",
                                    inline=False)
                else:
                    embed.add_field(name="期限", value=f"なし", inline=False)
                await log_channel.send(embed=embed)

            # スロットカテゴリーを取得
            category = self.bot.get_channel(setting.slot_category)

            # 作成するチャンネルの権限を設定
            overwrites = {}
            if setting and setting.admin_role:
                overwrites[category.guild.get_role(setting.admin_role)] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            overwrites[user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            overwrites[category.guild.default_role] = discord.PermissionOverwrite(read_messages=True, send_messages=False)

            # カテゴリーにチャンネルを作成
            slot = await category.create_text_channel(name=channel_name, overwrites=overwrites)

            # スロット情報を保存
            Slot.create(ctx.guild_id, slot.id, user.id, expire)

            # レスポンスメッセージを送信
            await ctx.response.send_message(
                f"スロットチャンネルを作成しました: <#{slot.id}>", ephemeral=True)

            # スロットチャンネルに作成完了メッセージを送信
            embed = discord.Embed(
                title="作成完了",
                description=text
            )
            await slot.send(embed=embed)

        else:
            await ctx.response.send_message("このコマンドを実行する権限がありません",
                                            ephemeral=True)

    @tasks.loop(time=datetime.time(hour=0))
    async def task(self):
        slots = Slot.get_all()
        if not slots:
            return

        today = datetime.date.today()
        for i in slots:
            if not i.expiry:
                return

            if i.expiry <= today:
                await self.bot.get_channel(i.channel_id).delete()
                Slot.delete(i.channel_id)

            elif i.expiry - today == datetime.timedelta(days=1):
                embed = discord.Embed(
                    title="スロットの使用期限が残り１日となっております"
                )
                await self.bot.get_channel(i.channel_id).send(embed=embed)
