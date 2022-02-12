from json import dump, load
import os
import logging
import config
import math

class LifeCycle:
    def __init__(self):
        os.makedirs(os.path.dirname(config.LIFECYCLE_LOG_FILEPATH), exist_ok=True)
        os.makedirs(os.path.dirname(config.CENSORED_USERS_FILEPATH), exist_ok=True)
        logging.basicConfig(filename=config.LIFECYCLE_LOG_FILEPATH, format='%(asctime)s %(message)s', level=logging.INFO)
        self.censored_users = {}
        try:
            with open(config.CENSORED_USERS_FILEPATH, 'r') as censored_users_file:
                self.censored_users = load(censored_users_file)
        except: # Censored users file does not exist, so it will be created at the end of the function
            logging.info(f"Censored users file not found")
        
    async def censor(self, context):
        guild = context.message.guild
        censor_delay = config.DEFAULT_CENSOR_TIME

        if not len(context.message.mentions):
            logging.info(f"No users mentioned in command")
            await context.send(f"No users mentioned in command")
            return

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
            for member in context.message.mentions:
                if str(guild.id) in self.censored_users: # Add user to guild's censored users
                    self.censored_users[str(guild.id)][str(member.id)] = {
                        'censor_delay': censor_delay
                    }
                else: # If guild does not already have an entry, create one with current user as its first entry
                    self.censored_users[str(guild.id)] = {
                        member.id: {
                            'censor_delay': censor_delay
                        }
                    }
                member_id = '<@' + str(member.id) + '>'
                logging.info(f"User {member_id} has been registered for censorship")
                await context.send(f"User {member_id} has been registered for censorship")
            # Rewrite censored users file with updated data
            with open(config.CENSORED_USERS_FILEPATH, 'w') as censored_users_file:
                dump(self.censored_users, censored_users_file)
        except:
            logging.exception(f"Error during censorship registration")
            await context.send('Error during censorship registration')
    
    async def sanction(self, context):
        guild = context.message.guild

        try:
            if not len(context.message.mentions):
                logging.info(f"No users mentioned in command")
                await context.send(f"No users mentioned in command")
                return

            for member in context.message.mentions:
                member_id = '<@' + str(member.id) + '>'
                if str(guild.id) in self.censored_users: # Remove user from guild's censored user list
                    if str(member.id) in self.censored_users[str(guild.id)]:
                        del self.censored_users[str(guild.id)][str(member.id)]
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
                dump(self.censored_users, censored_users_file)
        except:
            logging.exception(f"Error during censorship registration")
            await context.send('Error during censorship registration')

    