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

discord_bot = commands.Bot(command_prefix='*')
lifecycle = LifeCycle()
lifecycle_active = False
os.makedirs(os.path.dirname(config.BOT_LOG_FILEPATH), exist_ok=True)
logging.basicConfig(filename=config.BOT_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.INFO)

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

    @discord_bot.command(name='censor', help='Registers a user for censorship, deletes each message the user makes <minutes> after its creation.', usage='*censor @<user> <minutes>')
    @commands.has_any_role('Administrator', 'Developer')
    async def censor(self):
        await lifecycle.censor(self)

    @discord_bot.command(name='sanction', help='No longer censors a user\'s messages.', usage='*sanction @<user>')
    @commands.has_any_role('Administrator', 'Developer')
    async def sanction(self):
        await lifecycle.sanction(self)

discord_bot.run(TOKEN)