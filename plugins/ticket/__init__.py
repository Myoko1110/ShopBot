from discord.ext.commands import Bot

from plugins.ticket.ticket import TicketCog


def setup(bot: Bot):
    return bot.add_cog(TicketCog(bot))
