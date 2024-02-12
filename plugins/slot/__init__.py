from discord.ext.commands import Bot

from plugins.slot.slot import SlotCog


def setup(bot: Bot):
    return bot.add_cog(SlotCog(bot))
