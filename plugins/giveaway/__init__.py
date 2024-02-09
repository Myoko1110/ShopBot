from discord.ext.commands import Bot

from plugins.giveaway.giveaway import Giveaway


def setup(bot: Bot):
    return bot.add_cog(Giveaway(bot))
