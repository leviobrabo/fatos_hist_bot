from fatoshist.handlers.commands_handlers import admin, experience, fotoshist, history, send, sudo, user


def register_all(bot):
    """Registra cada handler uma única vez e retorna comandos por escopo."""
    user_commands = list(user.register(bot))
    send_commands = list(send.register(bot))
    photo_commands = list(fotoshist.register(bot))
    history_commands = list(history.register(bot))
    experience_commands = list(experience.register(bot))
    admin_commands = list(admin.register(bot))
    sudo_commands = list(sudo.register(bot))

    private_commands = [*user_commands, *send_commands, *photo_commands, *history_commands, *experience_commands]
    return {
        'private': private_commands,
        'group': photo_commands,
        'admin': [*admin_commands, *photo_commands],
        'sudo': [*sudo_commands, *private_commands],
    }


def register_chat_private(bot):
    commands = []
    commands.extend(user.register(bot))
    commands.extend(send.register(bot))
    commands.extend(fotoshist.register(bot))
    commands.extend(history.register(bot))
    commands.extend(experience.register(bot))

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
    return commands
