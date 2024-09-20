from fatoshist.database.users import UserManager


def sudo(user_id):
    user_manager = UserManager()
    user = user_manager.get_user(user_id)
    if user and user.get('sudo') == 'true':
        return True
    return False
