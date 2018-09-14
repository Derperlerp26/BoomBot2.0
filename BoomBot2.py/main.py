import discord
import discord.ext.commands
from discord.ext import commands
import sys
import os
import time
import json
import logging
from collections import namedtuple
import pickle
import threading

# Load bot settings
if not os.path.isfile('botSettings.json'):
    sys.exit("The botSettings.json file is missing. Get your shit together.")
else:
    with open('botSettings.json') as botSettings:
        jSettings = json.load(botSettings)
    settings = namedtuple("Settings", jSettings.keys())(*jSettings.values())
    botSettings.close()
    print("Settings successfully loaded.")


# Bot and client
client = discord.Client()
bot = commands.Bot(command_prefix = settings.prefix, case_insensitive = True, description = settings.description)

# Token checker
try:
    hackerman = open('Hackerman.txt', 'r')
except:
    print("Ah ah ah! You didn\'t say the magic word!")
magicWord = str(hackerman.readlines()).translate(dict.fromkeys(map(ord, '[\']'), None))
if sys.platform != "win32":
    magicWord = magicWord[:(len(magicWord) - 2)]

# logs all debug information from discord module
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename = 'BoomBot2Debug.log', encoding = 'utf-8', mode = 'w')
handler.setFormatter(logging.Formatter('%(asctime)s :: %(levelname)s ::\t%(name)s:  %(message)s'))
logger.addHandler(handler)


class ObjStore(object):
    def __init__(self):
        self.tBanList = []
        self.tRoleList = []
        self.pRoleList = []
    def loadFile(self, loadFrom, loadTo):
        try:
            if not os.path.isfile(loadFrom):
                lFile = open(loadFrom, 'w').write('')
            elif os.path.getsize(loadFrom) > 0:
                with open(loadFrom, 'rb') as lFile:
                    setattr(self, loadTo, pickle.load(lFile))
                lFile.close()
            print("{} loaded.".format(loadFrom))
            print(getattr(self, loadTo))
        except Exception as exce:
            print("Error when loading from {}.".format(loadFrom))
            print(exce)

class TempBan(object):
    def __init__(self, user, duration, reason, guildID, startTime = round(time.time())):
        self.user = user
        self.duration = duration
        self.reason = reason
        self.startTime = startTime
        self.guildID = guildID

class TempRole(object):
    def __init__(self, userID, duration, roleID, guildID, startTime = round(time.time())):
        self.userID = userID
        self.duration = duration
        self.roleID = roleID
        self.startTime = startTime
        self.guildID = guildID

class PersistRole(object):
    def __init__(self, userID, roleID, guildID):
        self.userID = userID
        self.duration = duration
        self.roleID = roleID
        self.guildID = guildID

async def checkTime():
    """Checks all temp stuff and persist stuff."""
    while True:
        for tBan in objStore.tBanList:
            if (round(time.time()) - tBan.startTime) > (tBan.duration * 86400):
                await client.get_guild(tBan.guildID).unban(tBan.userID)
        for tRole in objStore.tRoleList:
            if (round(time.time()) - tRole.startTime) > (tRole.duration * 86400):
                await client.get_guild(tRole.guildID).get_member(tRole.userID).remove_roles(tBan.roleID)
            #elif client.get_role(tRole.roleID) not in client.get_guild(tRole.guildID).get_member(tRole.userID).roles:
                #await client.get_guild(tRole.guildID).get_member(tRole.userID).add_roles(roleID)
        for pRole in objStore.pRoleList:
            if client.get_role(pRole.roleID) not in client.get_guild(pRole.guildID).get_member(pRole.userID).roles:
                await client.get_guild(pRole.guildID).get_member(pRole.userID).add_roles(roleID)
        print("Time checked.")
        time.sleep(60)


objStore = ObjStore()
timeChecker = threading.Thread(target = checkTime)

def updateSettings():
    with open('botSettings.json', 'w') as outfile:
        json.dump(settings, outfile, indent = 4)
    outfile.close()

# Run when bot starts
@bot.event
async def on_ready():
    """Where we droppin', boys?"""
    print("{} :: Booted as {} (ID - {})\n".format(time.ctime(), bot.user.name, bot.user.id))
    print("Connected servers: ")
    for guild in bot.guilds:
        print("\tID - {} : Name - {}".format(guild.id, guild.name))
    await bot.change_presence(activity = discord.Game(name = settings.currActivity))
    print("Playing: {}\n\n".format(settings.currActivity))
    objStore.loadFile('tempBans.txt', 'tBanList')
    #timeChecker.start()

#@bot.event
#async def on_member_update():


@bot.command()
async def listEmojis(ctx):
    """Displays all emotes avaiable on a Server."""
    embed = discord.Embed(title = "Command: listEmojis", description = "All the emotes availible on servers with Boom Bot 2.0:", color = 0x0000ff)
    for emoji in bot.emojis:
        output = ("```" + str(emoji.name, emoji.id, emoji.managed, emoji.server.name) + "```")
        embed.add_field(name = emoji.name, value = output, inline = False)
    await ctx.send(embed = embed)

@bot.command()
async def about(ctx):
    """Tells you 'bout shit, what else would it do?"""
    await ctx.send(content = "About is still a work in progress, so fuck off until it\'s done")

@bot.command()
async def changeGame(ctx, *activity):
    """Changes what the bot is playing."""
    if ctx.message.author.guild_permissions.administrator:
        embed = discord.Embed(title = "Command: changeGame", color = 0xff0000)
        try:
            settings.currActivity = ' '.join(activity)
            updateSettings()
            await bot.change_presence(activity = discord.Game(name = settings.currActivity))
            embed.description = "Game successfully changed to *{}*".format(settings.currActivity)
            embed.color = 0x00ff00
        except:
            embed.description = "An error has occurred when trying to change the game. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it."
    else:
        embed.description = "You do not have permission to use this command. Begone, ***thot***."
    await ctx.send(embed = embed)

@bot.command()
async def tempBan(ctx, user : discord.Member, duration, *reason):
    """Tempbans a mothafucka."""
    embed = discord.Embed(title = "Command: tempBan", color = 0xff0000)
    if ctx.message.author.guild_permissions.kick_members:
        try:
            for tBan in objStore.tBanList:
                if tBan.userID == user.id:
                    embed.description = "This user is already in the banlist. Get your shit together, kachigga."
            else:
                try:
                    objStore.tBanList.append(TempBan(user.id, duration, ' '.join(reason), ctx.message.guild.id, round(time.time())))
                    #await user.ban(reason = ' '.join(reason), delete_message_days = 0)
                    try:
                        with open('tempBans.txt', 'wb') as tBans:
                            pickle.dump(objStore.tBanList, tBans)
                        tBans.close()
                        embed.description = "**{}** has been successfully banned for **{}** days.\nReason: *{}*".format(user.name, duration, ' '.join(reason))
                        embed.color = 0x00ff00
                    except Exception as exce:
                        print("Pickle error in tempBan:" + str(exce))
                        embed.add_field(name = "Error:", value = exce)
                except Exception as exce:
                    print(exce)
                    embed.description = "An error has occurred when trying to ban **{}**. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it.".format(user.name)
        except Exception as exce:
            print(exce)
            embed.description = "An error has occurred when trying to ban **{}**. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it.".format(user.name)
            embed.add_field(name = "Error:", value = exce)
    else:
        embed.description = "You do not have permission to use this command. Begone, ***thot***."
    await ctx.send(embed = embed)

@bot.command()
async def veiwTBans(ctx):
    """Displays everyone who has been tempbanned."""
    embed = discord.Embed(title = "Command: viewTBans", color = 0x0000ff)
    if ctx.message.author.guild_permissions.kick_members:
        for tBan in objStore.tBanList:
            if tBan.guildID == ctx.message.guild.id:
                embed.add_field(name = client.get_user(tBan.userID).name, value = str(tBan.duration, tban.startTime), inline = False)
    else:
        embed.description = "You do not have permission to use this command. Begone, ***thot***."
        embed.color = 0xff0000
    await ctx.send(embed = embed)

@bot.command()
async def tempRole(ctx, user : discord.Member, duration, role : discord.Role):
    """Grants a user a role for a time."""
    embed = discord.Embed(title = "Command: tempRole", color = 0xff0000)
    if ctx.message.author.guild_permissions.manage_roles:
        try:
            for tRole in objStore.tRoleList:
                if tRole.userID == user.id and tRole.roleID == role.id:
                    embed.description = "This user already has that role."
            else:
                try:
                    objStore.tRoleList.append(TempRole(user.id, duration, role.id, ctx.message.guild.id, round(time.time())))
                    #await user.add_roles(role.id)
                    try:
                        with open('tempRoles.txt', 'wb') as tRoles:
                            pickle.dump(objStore.tRoleList, tRoles)
                        tRoles.close()
                        embed.description = "**{}** has been successfully given **{}** for **{}** days.".format(user.name, role.name, duration)
                        embed.color = 0x00ff00
                    except Exception as exce:
                        print("Pickle error in tempRole:" + str(exce))
                        embed.add_field(name = "Error:", value = exce)
                except Exception as exce:
                    print(exce)
                    embed.description = "An error occurred when trying to give **{}** **{}**. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it.".format(user.name, role.name)
        except Exception as exce:
            print(exce)
            embed.description = "An error occurred when trying to give **{}** **{}**. If you're reading this, 1) Congrats on fucking up the bot, 2) Contact Xaereus about it.".format(user.name, role.name)
            embed.add_field(name = "Error:", value = exce)
    else:
        embed.description = "You do not have permission to use this command, {}. Begone, ***thot***.".format(user.mention)
    await ctx.send(embed = embed)

# Start up the bot
bot.run(magicWord)
