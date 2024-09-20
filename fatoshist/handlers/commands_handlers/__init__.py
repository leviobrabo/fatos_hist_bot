from fatoshist.handlers.commands_handlers import admin, fotoshist, send, sudo, user


def register(bot):
    user.register(bot)
    send.register(bot)
    admin.register(bot)
    sudo.register(bot)
    fotoshist.register(bot)
