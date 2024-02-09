from discord.ext.commands import Bot

from plugins.verify.verify import Verify


def setup(bot: Bot):
    return bot.add_cog(Verify(bot))
