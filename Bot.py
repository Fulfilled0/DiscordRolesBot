import configparser
from discord.ext import commands
import roles
import config
import bot_help

parser = configparser.ConfigParser()
parser.read("config.cfg")

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")

TOKEN = parser["bot"]["token"]


@bot.event
async def on_ready():
    print("Bot is ready.")

roles.init(bot)
config.init(bot)
bot_help.init(bot)

bot.run(TOKEN)
