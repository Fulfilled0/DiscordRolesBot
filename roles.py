import discord
import db
import asyncio
import util


def init(bot):

    async def background_loop():
        """
        Remove any roles that have expired.
        """
        while not bot.is_closed:
            await asyncio.sleep(60)
            with db.session_scope() as session:
                all_users = session.query(db.UserRoles)
                for user in all_users:
                    user.mins_left -= 1
                    role = util.get_role(bot, user.role_id)
                    if user.mins_left == 0:
                        if role:
                            user_obj = discord.utils.get(bot.get_all_members(), id=user.user_id)
                            if user_obj:
                                await bot.remove_roles(user_obj, role)
                        session.delete(user)

    bot.loop.create_task(background_loop())

    @bot.group()
    async def roles():
        """Roles Commands"""

    @bot.event
    async def on_member_join(member):
        """
        When a new member joins a channel, add any unexpired roles they had previously.
        """
        with db.session_scope() as session:
            users = session.query(db.UserRoles).filter(db.UserRoles.user_id == member.id)
            for user in users:
                role = util.get_role(bot, user.role_id)
                if role:
                    await bot.add_roles(member, role)

    @roles.command(pass_context=True, no_pm=True)
    async def add_role(ctx, user: discord.User, role: discord.Role, duration):
        """
        Add role to user with fixed duration. Negative duration denotes permanent role.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        if util.convertible(duration):
            role_duration = int(duration)
        else:
            await bot.reply("Invalid duration!")
            return
        role_admin = ctx.message.author
        with db.session_scope() as session:
            new_user = session.query(db.UserRoles).filter(db.UserRoles.user_id == user.id).filter(role.id == db.UserRoles.role_id).first()
            if not new_user:
                new_user = db.UserRoles(user_id=user.id)
                session.add(new_user)
            new_user.role_id = role.id
            new_user.user_name = user.name
            new_user.admin_id = role_admin.id
            new_user.admin_name = role_admin.name
            new_user.mins_left = role_duration
        await bot.add_roles(user, role)
        await bot.reply("Adding role {0} for {1}!".format(role.name, user.name))
        return

    @roles.command(pass_context=True, no_pm=True)
    async def remove_role(ctx, user: discord.User, role: discord.Role):
        """
        Remove role from user.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        with db.session_scope() as session:
            user_delete = session.query(db.UserRoles).filter(db.UserRoles.user_id == user.id).filter(role.id == db.UserRoles.role_id).first()
            if not user_delete:
                await bot.reply("'{0}' currently does not have role {1}!".format(user.name, role.name))
                return
            session.delete(user_delete)
        await bot.remove_roles(user, role)
        await bot.reply("Removing role {0} from user {1}!".format(role.name, user.name))
        return

    @roles.command(pass_context=True, no_pm=True)
    async def delete_user_role(ctx, user_id, role: discord.Role):
        """
        Remove role from user with given user_id. This is used if the user has already left the server.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        with db.session_scope() as session:
            user_delete = session.query(db.UserRoles).filter(db.UserRoles.user_id == user_id).filter(role.id == db.UserRoles.role_id).first()
            if not user_delete:
                await bot.reply("'{0}' currently does not have role {1}!".format(user_id, role.name))
                return
            session.delete(user_delete)
        user = discord.utils.get(bot.get_all_members(), id=user_id)
        if user:
            await bot.remove_roles(user, role)
        else:
            await bot.reply("User with id '{0}' is no longer on the server!")
        await bot.reply("Removing role {0} from user {1}!".format(role.name, user_id))
        return

    @roles.command(pass_context=True, no_pm=True)
    async def clear_user(ctx, user: discord.User):
        """
        Remove all roles from a given user.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_roles = session.query(db.UserRoles).filter(db.UserRoles.user_id == user.id)
            for user_role in all_roles:
                role = util.get_role(bot, user_role.role_id)
                session.delete(user_role)
                if role:
                    await bot.remove_roles(user, role)
                    update_message += "Removing role {0} from {1}!\n".format(role.name, user.name)
                else:
                    update_message += "Removing defunct role {0} from {1}!\n".format(user_role.role_id, user.name)
        await bot.reply(update_message)

    @roles.command(pass_context=True, no_pm=True)
    async def modify_duration(ctx, user: discord.User, role: discord.Role, duration_change):
        """
        Increase the duration of role for given user by adding duration_change.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        if util.convertible(duration_change):
            change = int(duration_change)
        else:
            await bot.reply("Invalid duration change!")
            return
        with db.session_scope() as session:
            user_change = session.query(db.UserRoles).filter(db.UserRoles.user_id == user.id).filter(role.id == db.UserRoles.role_id).first()
            if not user_change:
                await bot.reply("'{0}' currently does not have role {1}!!".format(user.id, role.name))
                return
            user_change.mins_left += change
            await bot.reply("Role {0} for user {1} successfully had its duration increased by {2}.".format(role.name, user.name, change))
        return

    @roles.command(pass_context=True, no_pm=True)
    async def remove_defunct_roles(ctx):
        """
        Remove all defunct roles and any users who were assigned those roles.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_user_roles = session.query(db.UserRoles)
            for user_role in all_user_roles:
                if not util.get_role(bot, user_role.role_id):
                    session.delete(user_role)
                    update_message += "Removing role {0} from user {1}!\n".format(user_role.role_id, user_role.user_id)
        await bot.reply(update_message)

    @roles.command(pass_context=True, no_pm=True)
    async def clear_role(ctx, role: discord.Role):
        """
        Remove all users with a given role_id.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_user_roles = session.query(db.UserRoles).filter(db.UserRoles.role_id == role.id)
            for user_role in all_user_roles:
                session.delete(user_role)
                user = discord.utils.get(bot.get_all_members(), id=user_role.user_id)
                if user:
                    await bot.remove_roles(user, role)
                    update_message += "Removing role {0} from user {1}!\n".format(role.name, user_role.user_name)
                else:
                    update_message += "Removing role {0} from defunct user {1}!\n".format(role.name, user_role.user_id)
        await bot.reply(update_message)

    @roles.command(pass_context=True, no_pm=True)
    async def get_defunct_users(ctx):
        """
        Get all defunct users and any roles they had.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_user_roles = session.query(db.UserRoles)
            for user_role in all_user_roles:
                if not discord.utils.get(bot.get_all_members(), id=user_role.user_id):
                    role = util.get_role(bot, user_role.role_id)
                    if role:
                        update_message += "UserID: {0} with Username: {1}, has role {2} set by AdminID: {3} with AdminUsername: {4} with {5} minutes left on role.\n".format(user_role.user_id, user_role.user_name, role.name, user_role.admin_id, user_role.admin_name, user_role.mins_left)
                    else:
                        update_message += "UserID: {0} with Username: {1}, has defunct role with id {2} set by AdminID: {3} with AdminUsername: {4} with {5} minutes left on role.\n".format(user_role.user_id, user_role.user_name, user_role.role_id, user_role.admin_id, user_role.admin_name, user_role.mins_left)
        await bot.reply(update_message)

    @roles.command(pass_context=True, no_pm=True)
    async def remove_defunct_users(ctx):
        """
        Remove all defunct users and any roles they had.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_user_roles = session.query(db.UserRoles)
            for user_role in all_user_roles:
                if not discord.utils.get(bot.get_all_members(), id=user_role.user_id):
                    session.delete(user_role)
                    update_message += "Removing role {0} from user {1}!\n".format(user_role.role_id, user_role.user_id)
        await bot.reply(update_message)

    @roles.command(pass_context=True, no_pm=True)
    async def list_all(ctx):
        """
        List all users with their roles and durations currently assigned.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_users = session.query(db.UserRoles)
            if not all_users.first():
                await bot.reply("No roles currently assigned!")
                return
            for user in all_users:
                role = util.get_role(bot, user.role_id)
                if role:
                    update_message += "UserID: {0} with Username: {1}, has role {2} set by AdminID: {3} with AdminUsername: {4} with {5} minutes left on role.\n".format(user.user_id, user.user_name, role.name, user.admin_id, user.admin_name, user.mins_left)
                else:
                    update_message += "UserID: {0} with Username: {1}, has defunct role with id {2} set by AdminID: {3} with AdminUsername: {4} with {5} minutes left on role.\n".format(user.user_id, user.user_name, user.role_id, user.admin_id, user.admin_name, user.mins_left)
        await bot.reply(update_message)

    @roles.command(pass_context=True, no_pm=True)
    async def list_user(ctx, user: discord.User):
        """
        List the roles and durations currently assigned to a single given user.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        update_message = ""
        with db.session_scope() as session:
            all_roles = session.query(db.UserRoles).filter(db.UserRoles.user_id == user.id)
            if not all_roles.first():
                await bot.reply("No roles for user {0}".format(user.name))
                return
            for user_role in all_roles:
                role = util.get_role(bot, user_role.role_id)
                if role:
                    update_message += "UserID: {0} with Username: {1}, has role {2} set by AdminID: {3} with AdminUsername: {4} with {5} minutes left on role.\n".format(user_role.user_id, user_role.user_name, role.name, user_role.admin_id, user_role.admin_name, user_role.mins_left)
                else:
                    update_message += "UserID: {0} with Username: {1}, has defunct role with id {2} set by AdminID: {3} with AdminUsername: {4} with {5} minutes left on role.\n".format(user.user_id, user.user_name, user.role_id, user.admin_id, user.admin_name, user.mins_left)
        await bot.reply(update_message)
