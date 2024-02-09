import re

import discord
from discord import app_commands
from discord.ext.commands import Bot, Cog

import config


class Vending(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(name="vending")
    @app_commands.rename(
        title="タイトル",
        about="概要",
        image="画像",
    )
    async def vending(self, ctx: discord.Interaction,
                      title: str,
                      about: str,
                      image: str = None,
                      ):
        await ctx.response.send_message("このコマンドは現在実行できません", ephemeral=True)
        return

        embed = discord.Embed(
            title=title,
            description=about,
        )

        if image:
            embed.set_image(url=image)

        select = []
        for i in config.VENDING_PRODUCTS:
            embed.add_field(name=i["name"], value=str(i["price"]), inline=False)
            select.append(discord.SelectOption(label=i["name"], description=str(i["price"])))

        await ctx.response.send_message(embed=embed, view=BuyButton(select, self.bot))


class BuyButton(discord.ui.View):

    def __init__(self, products: list[discord.SelectOption], bot: Bot, timeout=None):
        self.products = products
        self.bot = bot
        super().__init__(timeout=timeout)

    @discord.ui.button(label="購入する", style=discord.ButtonStyle.success, emoji="🧺",
                       custom_id="vending_buy")
    async def request(self, ctx: discord.Interaction, button):
        # embed作成
        embed = discord.Embed(
            title="購入",
            description="購入したい商品を選択してください"
        )

        # select作成
        select = VendingSelect(products=self.products, bot=self.bot)

        # viewに追加
        view_select = discord.ui.View()
        view_select.add_item(select)

        # 選択メッセージを送信
        await ctx.response.send_message(embed=embed, view=view_select, ephemeral=True)


class VendingSelect(discord.ui.Select):

    def __init__(self, products: list[discord.SelectOption], bot: Bot):
        self.bot = bot
        super().__init__(placeholder="商品を選択", options=products)

    async def callback(self, ctx: discord.Interaction):
        if config.MODAL_MODE:
            await ctx.response.send_modal(VendingModal(self.values, self.bot))



class VendingModal(discord.ui.Modal):
    link = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="送金リンク",
        custom_id="link",
    )

    def __init__(self, product, bot: Bot):
        self.product = product
        self.bot = bot
        super().__init__(title="お金を送金します", custom_id="paypay_form")

    async def on_submit(self, ctx: discord.Interaction):

        res = re.search(r"https://pay.paypay.ne.jp/([a-zA-Z0-9]+)", self.link.value)
        link = res.group(1)
        print(link)
        res = paypay.receive(link)
        print(res)

        # embed作成
        embed = discord.Embed(
            title="支払いが完了しました",
        )

        await ctx.response.send_message(embed=embed)
