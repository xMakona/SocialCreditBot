from discord import Client
from discord.ext import commands
from dotenv import load_dotenv
from lifecycle import LifeCycle
import os
import config
import logging
import asyncio
import datetime
import utils

load_dotenv()
TOKEN = os.getenv('TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX')

discord_bot = commands.Bot(command_prefix=BOT_PREFIX)
lifecycle = LifeCycle()
# Prevents multiple lifecycle_loop tasks
lifecycle_active = False
# Creates directory for log file if it does not exist
os.makedirs(os.path.dirname(config.BOT_LOG_FILEPATH), exist_ok=True)
logging.basicConfig(filename=config.BOT_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.INFO)

# Loop function that dispatches life cycle tasks every minute
async def lifecycle_loop():
    global lifecycle_active
    lifecycle_active = True
    while True:
        current_time = datetime.datetime.utcnow()
        time_key = utils.get_time_key(current_time)
        discord_bot.loop.create_task(lifecycle.delete_censored_messages(time_key))

        sleep_duration = 60 - current_time.second
        await asyncio.sleep(sleep_duration)

# Put command signatures here
class SupremeRuler(Client):
    #####################################################     EVENTS     ###############################################################
    @discord_bot.event
    async def on_ready():
        logging.info('Social credit system online')
        if lifecycle_active == False:
            discord_bot.loop.create_task(lifecycle_loop())

    @discord_bot.event
    async def on_message(message):
        await discord_bot.process_commands(message)
        await lifecycle.process_message(message)

    #####################################################     COMMANDS     ###############################################################

    @discord_bot.command(name='censor', help='Registers <@user> for censorship, deletes each message <@user> makes <minutes> after they create it.', usage='*censor <@user> <minutes>')
    @commands.has_any_role('Administrator', 'Developer')
    async def censor(self):
        await lifecycle.censor(self)

    @discord_bot.command(name='sanction', help='No longer censors a <@user>\'s messages.', usage='*sanction <@user>')
    @commands.has_any_role('Administrator', 'Developer')
    async def sanction(self):
        await lifecycle.sanction(self)

    @discord_bot.command(name='purge', help='Purges all of <@user>\'s messages from <#channel>, if no channels are mentioned then the channel the command is issued in is purged.', usage='*purge @<user> #<channel>')
    @commands.has_any_role('Administrator', 'Developer')
    async def sanction(self):
        await lifecycle.purge(self)

discord_bot.run(TOKEN)