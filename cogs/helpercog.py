import discord
from discord.ext import commands


class HelperCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command
    async def help(self, ctx, query = None):
        if query is not None:
            if query.__doc__ is not None:
                await ctx.author.send(query.__doc__)
            else:
                await ctx.author.send(f"No help exists for {query.__name__}.")
        else:
            await ctx.author.send()


def setup(bot):
    bot.add_cog(HelperCog(bot))
