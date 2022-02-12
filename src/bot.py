from discord import Client
from discord.ext import commands
from dotenv import load_dotenv
from lifecycle import LifeCycle
import os
import config
import logging
import asyncio

load_dotenv()
TOKEN = os.getenv('TOKEN')

discord_bot = commands.Bot(command_prefix='*')
lifecycle = LifeCycle()
os.makedirs(os.path.dirname(config.BOT_LOG_FILEPATH), exist_ok=True)
logging.basicConfig(filename=config.BOT_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.INFO)

@discord_bot.event
async def on_ready():
    logging.info('Social credit system online')

# Put command signatures here
class SupremeRuler(Client):
    #####################################################     EVENTS     ###############################################################

    # @discord_bot.event
    # async def on_message(self):
    #     await discord_bot.process_commands(self.message)

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