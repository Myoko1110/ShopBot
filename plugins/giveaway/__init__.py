from discord.ext.commands import Bot

from plugins.giveaway.giveaway import GiveawayCog


def setup(bot: Bot):
    return bot.add_cog(GiveawayCog(bot))
