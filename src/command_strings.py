#!/bin/python3

censor = {
    'name': 'censor',
    'help': 'Registers <@user> for censorship, deletes each message <@user> makes <minutes> after they create it. Supports multiple mentions in one command.',
    'usage': '<@user> <minutes>'
}
sanction = {
    'name': 'sanction',
    'help': 'No longer censors <@user>\'s messages. Supports multiple mentions in one command.',
    'usage': '<@user>'
}
purge = {
    'name': 'purge',
    'help': ('Purges all of <@user>\'s messages found in the last <limit> messages in <#channel>. '
        'If no channels are mentioned then the channel the command is issued in is purged. '
        'If no users are mentioned, the last <limit> messages are deleted. '
        'If no <limit> is given, defaults to last 500 messages. Supports multiple mentions in one command.'
        '\n\nRecommend one user/channel per purge. Discord does not like this command.'),
    'usage': '<@user> <#channel> <limit>'
}