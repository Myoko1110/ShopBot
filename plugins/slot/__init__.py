from discord.ext.commands import Bot

from plugins.slot.slot import Slot


def setup(bot: Bot):
    return bot.add_cog(Slot(bot))
