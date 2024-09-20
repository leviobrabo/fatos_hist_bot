from fatoshist.handlers.commands_handlers import user, send, admin, sudo,fotoshist

def register(bot):
    user.register(bot)
    send.register(bot)
    admin.register(bot)
    sudo.register(bot)
    fotoshist.register(bot)