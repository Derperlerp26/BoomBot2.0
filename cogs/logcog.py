import logging

from discord.ext import commands


class Logger:
    """Logs everything."""

    def __init__(self, bot, log_dir = '\\logs'):
        self.log_dir = log_dir
        self.bot = bot
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        self.handler = logging.FileHandler(filename = f'{log_dir}cueball.log', encoding = 'utf-8', mode = 'w')
        self.handler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s ::\t%(name)s:  %(message)s'))
        self.logger.addHandler(self.handler)

    async def set_log_dir(self, ctx, log_dir):
        """Changes the directory to which the bot saves the log files to."""
        self.log_dir = log_dir
        await ctx.send(f"Successfully set log directory to {log_dir}")

    @commands.command()
    async def on_command(self, ctx):
        self.logger.info(ctx.command)
