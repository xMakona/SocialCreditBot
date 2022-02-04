from discord import Client
from discord.ext import commands
from dotenv import load_dotenv
import os
import config
import logging
import supreme_commands

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix='*')
os.makedirs(os.path.dirname(config.MESSAGE_LOG_FILEPATH), exist_ok=True)
logging.basicConfig(filename=config.MESSAGE_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.DEBUG)


# Once bot is ready...
@bot.event
async def on_ready():
    logging.info('Social credit system online')


# Put command signatures here
class SupremeRuler(Client):

    @bot.command(name='censor', help='Registers a user for censorship, deletes each message the user makes a set time after its creation.')
    @commands.has_any_role('Administrator', 'Developer')
    async def censor(self):
        await supreme_commands.censor(self)

    

    # @bot.event
    # async def on_message(self):
    #     logging.info(f'User {self.message.author.name} posted {self.message.content}')
    #     await bot.process_commands(self.message)


bot.run(TOKEN)
