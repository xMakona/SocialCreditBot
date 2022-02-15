from json import dump, load
import os
import logging
import config
import math
import asyncio
import utils

# Returns existing data in the censored users file, or an empty dict if the file does not exist
def load_censored_users():
    # Creates the directory the data files will be stored in, if it does not exist
    os.makedirs(os.path.dirname(config.CENSORED_USERS_FILEPATH), exist_ok=True)

    # Tries to load the censored users file as a json object
    try:
        with open(config.CENSORED_USERS_FILEPATH, 'r') as censored_users_file:
            return load(censored_users_file)
    # File doesn't exist or can't be read as JSON, return an empty dict
    except:
        logging.info(f"Censored users file not found")
        return {}

# Class for storing and manipulating data needed by bot.py
class LifeCycle:
    def __init__(self):
        # Dict of guilds(key: guild id) each containing dict of users(key: user id) each containing key: censor_delay
        self.censored_users = load_censored_users()
        # Dict of timestamps(key: timestamp from utils.get_time_key()) each containing an array of Message objects
        self.messages_to_delete = {}
    
    # Adds users to the self.censored_users dict
    async def censor(self, context):
        guild = context.message.guild
        censor_delay = config.DEFAULT_CENSOR_TIME

        # There are no users mentioned in the message so we do not need to go further
        if not len(context.message.mentions):
            logging.info(f"No users mentioned in command")
            await context.send(f"No users mentioned in command")
            return

        # Tries to retrieve a delay length from the message
        try:
            content = context.message.content.split(" ")
            censor_delay = float(content[len(content) - 1])
            censor_delay = math.ceil(censor_delay)
            logging.info(f"Censorship delay is set to {censor_delay} {'minutes' if censor_delay > 1 else 'minute'}")
            await context.send(f"Censorship delay is set to {censor_delay} {'minutes' if censor_delay > 1 else 'minute'}")
        # If no delay length is found, default delay length is used
        except:
            logging.info(f"No time given, censorship delay set to {censor_delay} minutes")
            await context.send(f"No time given, censorship delay set to {censor_delay} minutes")

        # Tries to add the users to self.censored_users dict
        try:
            # Each mention in the command message corresponds to a discord Member object
            for member in context.message.mentions:
                # Add user to guild's censored users if the guild already exists
                if str(guild.id) in self.censored_users:
                    self.censored_users[str(guild.id)][str(member.id)] = {
                        'censor_delay': censor_delay
                    }
                # If guild does not already exist in the dict, create one with the current user as its first entry
                else:
                    self.censored_users[str(guild.id)] = {
                        member.id: {
                            'censor_delay': censor_delay
                        }
                    }
                member_id = '<@' + str(member.id) + '>'
                logging.info(f"User {member_id} has been registered for censorship, their messages will be deleted after {censor_delay} {'minutes' if censor_delay > 1 else 'minute'}")
                await context.send(f"User {member_id} has been registered for censorship, their messages will be deleted after {censor_delay} {'minutes' if censor_delay > 1 else 'minute'}")
            # Rewrite censored users file with updated data
            with open(config.CENSORED_USERS_FILEPATH, 'w') as censored_users_file:
                dump(self.censored_users, censored_users_file)
        # Users could not be added to censored users file
        except:
            logging.exception(f"Error during censorship registration")
            await context.send("Error during censorship registration")
    
    # Removes users from the self.censored_users dict
    async def sanction(self, context):
        guild = context.message.guild

        # Tries to remove the users from the self.censored_users dict
        try:
            # There are no users mentioned in the message so we do not need to go further
            if not len(context.message.mentions):
                logging.info(f"No users mentioned in command")
                await context.send(f"No users mentioned in command")
                return

            # Each mention in the command message corresponds to a discord Member object
            for member in context.message.mentions:
                member_id = '<@' + str(member.id) + '>'
                # Checks that the guild exists in the censored users dict
                if str(guild.id) in self.censored_users:
                    # Remove user from guild's censored user list
                    if str(member.id) in self.censored_users[str(guild.id)]:
                        del self.censored_users[str(guild.id)][str(member.id)]
                        logging.info(f"{member_id} is no longer registered for censorship")
                        await context.send(f"{member_id} is no longer registered for censorship")
                    # User is not currently censored in the guild the message came from
                    else:
                        logging.info(f"{member_id} is not registered for censorship")
                        await context.send(f"{member_id} is not registered for censorship")
                # If guild does not exist then we cannot remove the user
                else:
                    logging.info(f"There are no users currently registered for censorship")
                    await context.send(f"There are no users currently registered for censorship")
                    return
            # Rewrite censored users file with updated data
            with open(config.CENSORED_USERS_FILEPATH, 'w') as censored_users_file:
                dump(self.censored_users, censored_users_file)
        # Users could not be removed from censored users file
        except:
            logging.exception(f"Error during censorship registration")
            await context.send("Error during censorship registration")

    async def purge(self, context):
        channels = context.message.channel_mentions
        mentions = context.message.mentions
        purge_limit = config.DEFAULT_PURGE_LIMIT

        # Tries to retrieve a purge limit from the message
        try:
            content = context.message.content.split(" ")
            purge_limit = int(content[len(content) - 1])
            logging.info(f"Purge limit is set to {purge_limit} messages")
        # If no purge limit is found, default purge limit is used
        except:
            logging.info(f"No limit given, purge limit is set to {purge_limit} messages")


        if(len(mentions) and len(channels)):
            for member in mentions:
                def purge_check(m):
                    return m.author == member
                for channel in channels:
                    await channel.purge(limit=purge_limit, check=purge_check)
        elif(len(mentions)):
            for member in mentions:
                def purge_check(m):
                    return m.author == member
                await context.message.channel.purge(limit=purge_limit, check=purge_check)
        elif(len(channels)):
            for channel in channels:
                await channel.purge(limit=purge_limit)
        else:
            await context.message.channel.purge(limit=purge_limit)


    # Processes messages from guilds the bot is in
    async def process_message(self, message):
        guild_id = str(message.guild.id)
        author_id = str(message.author.id)

        #Checks self.censored_users has an entry for the guild
        if guild_id in self.censored_users:
            # Checks if the message's author is censored in that guild
            if author_id in self.censored_users[guild_id]:
                # Creates time key for when the message should be deleted
                user = self.censored_users[guild_id][author_id]
                time_key = utils.get_time_key(message.created_at, user['censor_delay'])
                # If the time key does not already have an entry in self.messages_to_delete, create one with an empty array
                if not time_key in self.messages_to_delete:
                    self.messages_to_delete[time_key] = []
                self.messages_to_delete[time_key].append(message)
            # Author of the message is not censored in this guild, so return
            else:
                return
        # There are no censored users in this guild, so return
        else:
            return

    # Deletes any messages in self.messages_to_delete[time_key]
    async def delete_censored_messages(self, time_key):
        # Checks if time_key exists 
        if(time_key in self.messages_to_delete):
            # Awaits the completion of all message.delete calls
            await asyncio.gather(*[message.delete() for message in self.messages_to_delete[time_key]])
            del self.messages_to_delete[time_key]