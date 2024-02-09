from discord.ext.commands import Bot

from plugins.handle.handle import Handle


def setup(bot: Bot):
    return bot.add_cog(Handle(bot))
