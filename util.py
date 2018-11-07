import discord
import db
from db import Settings


def convertible(str):
    """
    Check if given string is convertible into an int.
    """
    try:
        int(str)
    except ValueError:
        return False
    else:
        return True


def get_role(bot, role_id):
    """
    Return role object associated with role_id.
    """
    return discord.utils.get([r for server in bot.servers for r in server.roles], id=role_id)


def bot_permissions(user: discord.User):
    """
    Return if the user has permissions to use bot commands.
    """
    p = []
    with db.session_scope() as session:
        permissions = session.query(Settings).filter(Settings.key == "permissions")
        for permission in permissions:
            p.append(get_permission(user, permission.value))
    if p:
        return all(p)
    return False


def get_permission(user: discord.User, permission):
    """
    Return the permission of user. Permission is a string.
    """
    return getattr(user.server_permissions, permission)
