from json import dump, load
import os
import math
import logging
import config

os.makedirs(os.path.dirname(config.MESSAGE_LOG_FILEPATH), exist_ok=True)
os.makedirs(os.path.dirname(config.CENSORED_USERS_FILEPATH), exist_ok=True)
logging.basicConfig(filename=config.BOT_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.DEBUG)

async def censor(context):
    censored_users = {}
    guild = context.message.guild
    censor_delay = config.DEFAULT_CENSOR_TIME

    try:
        with open(config.CENSORED_USERS_FILEPATH, 'r') as censored_users_file:
            censored_users = load(censored_users_file)
    except: # Censored users file does not exist, so it will be created at the end of the function
        logging.info(f"Creating censored users file")

    try:
        content = context.message.content.split(" ")
        censor_delay = float(content[len(content) - 1])
        censor_delay = math.ceil(censor_delay)
        logging.info(f'Censorship delay is set to {censor_delay} minutes')
        await context.send(f'Censorship delay is set to {censor_delay} minutes')
    except: # If no censor time, default time is used instead
        logging.info(f'No time given, censorship delay set to {censor_delay} minutes')
        await context.send(f'No time given, censorship delay set to {censor_delay} minutes')

    try:
        if not len(context.message.mentions):
            logging.info(f"No users mentioned in command")
            await context.send(f"No users mentioned in command")
        for member in context.message.mentions:
            if str(guild.id) in censored_users: # Add user to guild's censored users
                censored_users[str(guild.id)][str(member.id)] = {
                    'censor_delay': censor_delay
                }
            else: # If guild does not already have an entry, create one with current user as its first entry
                censored_users[str(guild.id)] = {
                    member.id: {
                        'censor_delay': censor_delay
                    }
                }
            member_id = '<@' + str(member.id) + '>'
            logging.info(f"User {member_id} has been registered for censorship")
            await context.send(f"User {member_id} has been registered for censorship")
        # Rewrite censored users file with updated data
        with open(config.CENSORED_USERS_FILEPATH, 'w') as censored_users_file:
            dump(censored_users, censored_users_file)
    except:
        logging.exception(f"Error during censorship registration")
        await context.send('Error during censorship registration')

async def sanction(context):
    censored_users = {}
    guild = context.message.guild

    try:
        with open(config.CENSORED_USERS_FILEPATH, 'r') as censored_users_file:
            censored_users = load(censored_users_file)
    except: # Censored users file does not exist, so it will be created at the end of the function
        logging.info(f"There are no users currently registered for censorship")
        await context.send(f"There are no users currently registered for censorship")
        return

    try:
        for member in context.message.mentions:
            member_id = '<@' + str(member.id) + '>'
            if str(guild.id) in censored_users: # Remove user from guild's censored user list
                if str(member.id) in censored_users[str(guild.id)]:
                    del censored_users[str(guild.id)][str(member.id)]
                    logging.info(f"{member_id} is no longer registered for censorship")
                    await context.send(f"{member_id} is no longer registered for censorship")
                else:
                    logging.info(f"{member_id} is not registered for censorship")
                    await context.send(f"{member_id} is not registered for censorship")
            else: # If guild does not exist then we cannot remove the user
                logging.info(f"There are no users currently registered for censorship")
                await context.send(f"There are no users currently registered for censorship")
                return
        # Rewrite censored users file with updated data
        with open(config.CENSORED_USERS_FILEPATH, 'w') as censored_users_file:
            dump(censored_users, censored_users_file)
    except:
        logging.exception(f"Error during censorship registration")
        await context.send('Error during censorship registration')
