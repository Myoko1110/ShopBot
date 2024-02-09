from discord.ext.commands import Bot

from plugins.new.command import New


def setup(bot: Bot):
    return bot.add_cog(New(bot))