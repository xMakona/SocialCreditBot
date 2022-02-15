from discord.ext import commands
import logging
import asyncio
import datetime
import sys
sys.path.append('..')
import command_strings
import utils

# Loop function that dispatches life cycle tasks every minute
async def lifecycle_loop(discord_bot, lifecycle):
    global lifecycle_active
    lifecycle_active = True
    while True:
        current_time = datetime.datetime.utcnow()
        time_key = utils.get_time_key(current_time)
        discord_bot.loop.create_task(lifecycle.delete_censored_messages(time_key))

        sleep_duration = 60 - current_time.second
        await asyncio.sleep(sleep_duration)

# Put command signatures here
class Admin(commands.Cog):
    def __init__(self, discord_bot, lifecycle):
        self.discord_bot = discord_bot
        self.lifecycle = lifecycle
        self.lifecycle_active = False
    #####################################################     EVENTS     ###############################################################
    @commands.Cog.listener()
    async def on_ready(self):
        logging.info('Social credit system online')
        if self.lifecycle_active == False:
            self.discord_bot.loop.create_task(lifecycle_loop(self.discord_bot, self.lifecycle))

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.lifecycle.process_message(message)

    #####################################################     COMMANDS     ###############################################################
    @commands.command(name=command_strings.censor['name'], help=command_strings.censor['help'], usage=command_strings.censor['usage'])
    @commands.has_guild_permissions(administrator=True)
    async def censor(self, context):
        await self.lifecycle.censor(context)

    @commands.command(name=command_strings.sanction['name'], help=command_strings.sanction['help'], usage=command_strings.sanction['usage'])
    @commands.has_guild_permissions(administrator=True)
    async def sanction(self, context):
        await self.lifecycle.sanction(context)

    @commands.command(name=command_strings.purge['name'], help=command_strings.purge['help'], usage=command_strings.purge['usage'])
    @commands.has_guild_permissions(administrator=True)
    async def purge(self, context):
        await self.lifecycle.purge(context)