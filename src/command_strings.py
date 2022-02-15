group_names = {
    'admin': 'Admin use only',
    'general': 'General use'
}

censor = {
    'name': 'censor',
    'help': 'Registers <@user> for censorship, deletes each message <@user> makes <minutes> after they create it.',
    'usage': '<@user> <minutes>'
}
sanction = {
    'name': 'sanction',
    'help': 'No longer censors a <@user>\'s messages.',
    'usage': '<@user>'
}
purge = {
    'name': 'purge',
    'help': ('Purges all of <@user>\'s messages found in the last <limit> messages in <#channel>. '
        'If no channels are mentioned then the channel the command is issued in is purged. '
        'If no users are mentioned, the last <limit> messages are deleted. '
        'If no <limit> is given, defaults to last 500 messages.'),
    'usage': '<@user> <#channel> <limit>'
}