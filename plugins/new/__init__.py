from discord.ext.commands import Bot

from plugins.new.new import New


def setup(bot: Bot):
    return bot.add_cog(New(bot))