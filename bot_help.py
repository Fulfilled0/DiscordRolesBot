import util


def init(bot):

    @bot.command(pass_context=True, no_pm=True)
    async def help(ctx):
        """
        Request help for bot functions.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        help_message = ""
        help_message += "```"
        help_message += "Commands:\n"
        help_message += "!help\n"
        help_message += "!permissions\n"
        help_message += "!roles add_role user role duration\n"
        help_message += "!roles remove_role user role\n"
        help_message += "!roles delete_user_role user_id role\n"
        help_message += "!roles clear_user user\n"
        help_message += "!roles remove_defunct_users\n"
        help_message += "!roles modify_duration user role duration_change\n"
        help_message += "!roles remove_defunct_roles\n"
        help_message += "!roles clear_role role\n"
        help_message += "!roles get_defunct_users\n"
        help_message += "!roles list_all\n"
        help_message += "!roles list_user user\n"
        help_message += "!config add_permission permission\n"
        help_message += "!config remove_permission permission\n"
        help_message += "!config list_permissions\n"
        help_message += "```"
        await bot.reply(help_message)

    @bot.command(pass_context=True, no_pm=True)
    async def permissions(ctx):
        """
        Return all permissions that are supported.
        """
        if not util.bot_permissions(ctx.message.author):
            return
        help_message = ""
        help_message += "```"
        help_message += "List of all supported permissions:\n"
        help_message += "create_instant_invite\n"
        help_message += "kick_members\n"
        help_message += "ban_members\n"
        help_message += "administrator\n"
        help_message += "manage_channels\n"
        help_message += "manage_server\n"
        help_message += "add_reactions\n"
        help_message += "view_audit_logs\n"
        help_message += "read_messages\n"
        help_message += "send_messages\n"
        help_message += "send_tts_messages\n"
        help_message += "manage_messages\n"
        help_message += "embed_links\n"
        help_message += "attach_files\n"
        help_message += "read_message_history\n"
        help_message += "mention_everyone\n"
        help_message += "external_emojis\n"
        help_message += "connect\n"
        help_message += "speak\n"
        help_message += "mute_members\n"
        help_message += "deafen_members\n"
        help_message += "move_members\n"
        help_message += "use_voice_activation\n"
        help_message += "change_nickname\n"
        help_message += "manage_nicknames\n"
        help_message += "manage_roles\n"
        help_message += "manage_webhooks\n"
        help_message += "manage_emojis\n"
        help_message += "```"
        await bot.reply(help_message)
