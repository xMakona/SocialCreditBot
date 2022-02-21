#!/bin/python3

from discord import Client
from discord.ext import commands
from Cogs.admin_cog import Admin
from lifecycle import LifeCycle
from dotenv import load_dotenv
import os
import config
import logging
import asyncio
import datetime
import utils
import command_strings

load_dotenv()
TOKEN = os.getenv('TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX')

discord_bot = commands.Bot(command_prefix=BOT_PREFIX)
lifecycle = LifeCycle()
# Creates directory for log file if it does not exist
os.makedirs(os.path.dirname(config.BOT_LOG_FILEPATH), exist_ok=True)
logging.basicConfig(filename=config.BOT_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.INFO)

discord_bot.add_cog(Admin(discord_bot, lifecycle))
discord_bot.run(TOKEN)