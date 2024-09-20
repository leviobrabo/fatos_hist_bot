from fatoshist.handlers.commands_handlers import admin, fotoshist, send, sudo, user


def register_chat_private(bot):
    commands = []
    commands.extend(user.register(bot))
    commands.extend(send.register(bot))
    commands.extend(fotoshist.register(bot))

    return commands


def register_chat_group(bot):
    commands = []
    commands.extend(fotoshist.register(bot))

    return commands


def register_admin_chat_group(bot):
    commands = []
    commands.extend(admin.register(bot))
    commands.extend(fotoshist.register(bot))
    return commands


def register_sudo(bot):
    commands = []
    commands.extend(sudo.register(bot))
    commands.extend(register_chat_private(bot))
    return commands
