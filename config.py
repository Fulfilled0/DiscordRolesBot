import db


def init(bot):

    @bot.group()
    async def config():
        """Config Commands"""

    @config.command(pass_context=True, no_pm=True)
    async def add_permission(ctx, permission):
        """
        Add additional permission to use the bot. Only server administrators can use this command.
        """
        if not ctx.message.author.server_permissions.administrator:
            return
        with db.session_scope() as session:
            p = session.query(db.Settings).filter((db.Settings.key == "permissions") & (db.Settings.value == permission)).first()
            if p:
                await bot.reply("Bot permission {0} is already being enforced.".format(permission))
                return
            p = db.Settings(key="permissions", value=permission)
            session.add(p)
            await bot.reply("Bot permission {0} added.".format(permission))

    @config.command(pass_context=True, no_pm=True)
    async def remove_permission(ctx, permission):
        """
        Remove a single permission to use the bot. Only server administrators can use this command.
        """
        if not ctx.message.author.server_permissions.administrator:
            return
        with db.session_scope() as session:
            p = session.query(db.Settings).filter((db.Settings.key == "permissions") & (db.Settings.value == permission)).first()
            if not p:
                await bot.reply("Bot permission {0} not currently enforced.".format(permission))
                return
            p = db.Settings(key="permissions", value=permission)
            session.delete(p)
            await bot.reply("Bot permission {0} removed.".format(permission))

    @config.command(pass_context=True, no_pm=True)
    async def list_permissions(ctx):
        """
        List all permissions required to use the bot. Only server administrators can use this command.
        """
        if not ctx.message.author.server_permissions.administrator:
            return
        with db.session_scope() as session:
            permissions = session.query(db.Settings).filter(db.Settings.key == "permissions")
            if not permissions:
                await bot.reply("No permission required to use the bot currently")
                return
            p = []
            for permission in permissions:
                p.append(permission.value)
            await bot.reply("Permissions required to use the bot: {0}".format(p))
