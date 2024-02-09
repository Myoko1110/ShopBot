from discord.ext.commands import Bot

from plugins.embed.embed import Embed


def setup(bot: Bot):
    return bot.add_cog(Embed(bot))
